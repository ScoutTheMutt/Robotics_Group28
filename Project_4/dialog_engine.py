"""
Dialog Engine
Parses DSL script files, performs rule matching, manages state machine.
Returns (speak_text, actions, is_safety_interrupt) tuples.
"""

import re
import random


class FatalParseError(Exception):
    pass


class Rule:
    def __init__(self, level, pattern_str, output_str, line_num):
        self.level = level            # 0=u:, 1=u1:, 2=u2:, etc.
        self.pattern_str = pattern_str  # raw pattern text inside (...)
        self.output_str = output_str    # raw output text after final :
        self.line_num = line_num
        self.children = []            # child Rule objects
        self.compiled = None          # compiled re.Pattern
        self.capture_vars = []        # variable names for each _ capture


def _parse_choice_list(content):
    """Parse [a b "two words"] style content into list of alternatives."""
    tokens = []
    i = 0
    while i < len(content):
        if content[i] == ' ':
            i += 1
            continue
        if content[i] == '"':
            end = content.find('"', i + 1)
            if end != -1:
                tokens.append(content[i + 1:end])
                i = end + 1
            else:
                i += 1
        else:
            m = re.match(r'\S+', content[i:])
            if m:
                tokens.append(m.group(0))
                i += m.end()
            else:
                i += 1
    return tokens


class DialogEngine:
    # Known action tag names
    KNOWN_ACTIONS = {'head_yes', 'head_no', 'arm_raise', 'dance90'}
    # Max nesting depth (rules at level >= 6 are rejected; depth = level+1 > 6)
    MAX_LEVEL = 5

    def __init__(self, seed=None):
        self.rules = []            # top-level u: rules only
        self.definitions = {}      # ~name -> list[str] of alternatives
        self.variables = {}        # varname -> value
        self.current_scope = None  # Rule whose children are currently active
        self.scope_depth = 0
        self.state = 'BOOT'
        self.unmatched_in_scope = 0
        self.rng = random.Random(seed)
        self.filename = ''

    # ------------------------------------------------------------------
    # Loading / Parsing
    # ------------------------------------------------------------------

    def load(self, filepath):
        """Parse a DSL script file and build the rule tree."""
        self.rules = []
        self.definitions = {}
        self.variables = {}
        self.current_scope = None
        self.scope_depth = 0
        self.unmatched_in_scope = 0
        self.filename = filepath

        # Regexes for line types
        DEF_RE = re.compile(r'^\s*~(\w+)\s*:\s*\[(.+)\]\s*$')
        RULE_RE = re.compile(r'^\s*(u(\d*))\s*:\s*\((.+?)\)\s*:\s*(.*?)\s*$')

        # level-keyed dict tracking the last rule seen at each level
        last_at_level = {}

        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise FatalParseError(f"Script file not found: {filepath}")

        for line_num, raw_line in enumerate(lines, start=1):
            # Strip comments
            line = raw_line.split('#')[0].rstrip()

            # Skip blank lines
            if not line.strip():
                continue

            # --- Definition line ---
            dm = DEF_RE.match(line)
            if dm:
                name, content = dm.group(1), dm.group(2)
                alts = _parse_choice_list(content)
                if alts:
                    self.definitions[name] = alts
                else:
                    print(f"[PARSE ERROR] {filepath}:{line_num} empty definition (non-fatal)")
                continue

            # --- Rule line ---
            rm = RULE_RE.match(line)
            if rm:
                tag, num_str, pattern_str, output_str = (
                    rm.group(1), rm.group(2), rm.group(3), rm.group(4)
                )
                level = int(num_str) if num_str else 0

                # Max nesting depth guard: depth = level+1; reject if > 6
                if level > self.MAX_LEVEL:
                    print(f"[PARSE ERROR] {filepath}:{line_num} nesting depth {level+1} > 6, rule rejected (non-fatal)")
                    continue

                # Check for unbalanced brackets in output
                if output_str.count('[') != output_str.count(']'):
                    print(f"[PARSE ERROR] {filepath}:{line_num} unbalanced brackets in output (non-fatal)")
                    continue

                rule = Rule(level, pattern_str.strip(), output_str, line_num)

                # Build tree
                if level == 0:
                    self.rules.append(rule)
                else:
                    parent_level = level - 1
                    if parent_level in last_at_level:
                        last_at_level[parent_level].children.append(rule)
                    else:
                        print(f"[PARSE ERROR] {filepath}:{line_num} u{level} rule has no parent at level {parent_level} (non-fatal)")
                        continue

                last_at_level[level] = rule
                # Remove all keys deeper than this level
                for k in list(last_at_level.keys()):
                    if k > level:
                        del last_at_level[k]
                continue

            # --- Neither definition nor rule: check for common errors ---
            stripped = line.strip()

            # Detect missing-second-colon pattern: u:(pattern) text
            if re.match(r'^\s*u\d*\s*:\s*\(.+\)\s+\S', line):
                print(f"[PARSE ERROR] {filepath}:{line_num} missing second colon delimiter (non-fatal)")
                continue

            # Detect bad definition (missing colon after ~name)
            if re.match(r'^\s*~\w+\s+\[', line):
                print(f"[PARSE ERROR] {filepath}:{line_num} bad definition line, missing colon (non-fatal)")
                continue

            # Any other non-blank, non-comment line that didn't match
            if stripped:
                print(f"[PARSE ERROR] {filepath}:{line_num} unrecognized line format (non-fatal)")

        if not self.rules:
            raise FatalParseError(f"No valid u: rules found in {filepath}")

        # Compile all rules
        self._compile_all(self.rules)

        self.state = 'IDLE'
        print(f"[STATE] IDLE (script loaded: {filepath}, {len(self.rules)} top-level rules)")

    def _compile_all(self, rule_list):
        """Recursively compile all rules in the tree."""
        for rule in rule_list:
            self._compile_rule(rule)
            self._compile_all(rule.children)

    def _compile_rule(self, rule):
        """Compile rule.pattern_str into a regex and populate capture_vars."""
        # Determine capture variable names from output_str
        rule.capture_vars = re.findall(r'\$(\w+)', rule.output_str)

        try:
            regex_body = self._pattern_to_regex(rule.pattern_str)
            rule.compiled = re.compile('^' + regex_body + '$', re.IGNORECASE)
        except re.error as e:
            print(f"[PARSE ERROR] {self.filename}:{rule.line_num} regex compile error: {e} (non-fatal)")
            rule.compiled = None

    def _pattern_to_regex(self, pattern_str):
        """Convert a DSL pattern string to a regex body (no anchors)."""
        # Tokenize: find quoted phrases, bracket groups, ~defs, wildcards, words
        TOKEN_RE = re.compile(
            r'"([^"]*)"'        # group 1: quoted phrase
            r'|\[([^\]]*)\]'    # group 2: bracket group [...]
            r'|~(\w+)'          # group 3: definition ~name
            r'|(_)'             # group 4: wildcard _
            r'|(\S+)'           # group 5: plain word/token
        )
        parts = []
        for m in TOKEN_RE.finditer(pattern_str):
            quoted, bracket, defname, wildcard, word = m.groups()

            if quoted is not None:
                # Quoted phrase: match words separated by whitespace
                words = quoted.split()
                parts.append(r'\s+'.join(re.escape(w) for w in words) if words else '')

            elif bracket is not None:
                choices = _parse_choice_list(bracket)
                if choices:
                    alts = [r'\s+'.join(re.escape(w) for w in c.split()) for c in choices]
                    parts.append('(?:' + '|'.join(alts) + ')')
                # empty bracket → skip

            elif defname is not None:
                if defname in self.definitions:
                    alts = [r'\s+'.join(re.escape(w) for w in c.split())
                            for c in self.definitions[defname]]
                    parts.append('(?:' + '|'.join(alts) + ')')
                else:
                    # Unknown definition → match literally
                    parts.append(re.escape('~' + defname))

            elif wildcard is not None:
                parts.append('(.+?)')

            elif word is not None:
                parts.append(re.escape(word))

        return r'\s+'.join(parts) if parts else '.*'

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def process(self, user_input):
        """
        Process user input and return (speak_text, actions, is_safety_interrupt).
        speak_text may be None if no rule matched.
        """
        if self.state == 'BOOT':
            return (None, [], False)

        # Strip punctuation for matching; keep original case for variable capture
        stripped = re.sub(r'[.,!?]', '', user_input).strip()
        normalized = stripped.lower()  # lowercase only for safety check

        # Safety interrupt check (before rule matching)
        if re.match(r'^(stop|cancel|reset|quit)$', normalized):
            self._reset_to_idle()
            print(f"[STATE] IDLE (safety interrupt)")
            return ("OK. Stopping now.", [], True)

        # Build active rules: scope children first, then top-level
        active = []
        if self.current_scope is not None:
            active.extend(self.current_scope.children)
        active.extend(self.rules)

        # Try each rule (regex uses re.IGNORECASE so match against stripped original)
        for rule in active:
            if rule.compiled is None:
                continue
            m = rule.compiled.match(stripped)
            if m:
                # Store captured variables (preserve original case)
                groups = m.groups()
                for i, varname in enumerate(rule.capture_vars):
                    if i < len(groups) and groups[i] is not None:
                        self.variables[varname] = groups[i]

                speak_text, actions = self._resolve_output(rule.output_str)

                # Update scope
                self._update_scope(rule)
                self.unmatched_in_scope = 0

                print(f"[RULE MATCHED] line {rule.line_num}: {rule.pattern_str}")
                print(f"[STATE] {self.state}")
                return (speak_text, actions, False)

        # No match
        self.unmatched_in_scope += 1
        if self.current_scope is not None and self.unmatched_in_scope >= 4:
            print(f"[SAFETY] Unmatched-in-scope reset after {self.unmatched_in_scope} consecutive misses")
            self._reset_to_idle()
        return (None, [], False)

    def _update_scope(self, matched_rule):
        """Update FSM scope after a successful rule match."""
        if matched_rule.children and (matched_rule.level + 1) < 6:
            self.current_scope = matched_rule
            self.scope_depth = matched_rule.level + 1
            self.state = f"IN_SCOPE({self.scope_depth})"
        else:
            self.current_scope = None
            self.scope_depth = 0
            self.state = "IDLE"

    def _reset_to_idle(self):
        """Reset state machine to IDLE."""
        self.current_scope = None
        self.scope_depth = 0
        self.unmatched_in_scope = 0
        self.state = 'IDLE'

    # ------------------------------------------------------------------
    # Output Resolution
    # ------------------------------------------------------------------

    def _resolve_output(self, output_str):
        """
        Resolve an output string into (speak_text, known_actions).
        Steps: extract actions, expand choices, expand defs, substitute vars.
        """
        actions = []

        # Step 1: Extract <action_name> tags
        def replace_action(m):
            name = m.group(1)
            if name in self.KNOWN_ACTIONS:
                actions.append(name)
            else:
                print(f"[WARNING] Unknown action: <{name}>")
            return ''

        text = re.sub(r'<(\w+)>', replace_action, output_str)

        # Step 2: Expand [choice1 choice2 "phrase"] in output (pick random)
        def expand_choice(m):
            choices = _parse_choice_list(m.group(1))
            return self.rng.choice(choices) if choices else ''

        text = re.sub(r'\[([^\]]*)\]', expand_choice, text)

        # Step 3: Expand ~name definitions (pick random)
        def expand_def(m):
            name = m.group(1)
            if name in self.definitions:
                return self.rng.choice(self.definitions[name])
            return m.group(0)

        text = re.sub(r'~(\w+)', expand_def, text)

        # Step 4: Substitute $varname
        def replace_var(m):
            varname = m.group(1)
            return self.variables.get(varname, "I don't know")

        text = re.sub(r'\$(\w+)', replace_var, text)

        return text.strip(), actions
