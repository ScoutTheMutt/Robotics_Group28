# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Server

```bash
cd Project_1
python app.py
# Server runs on http://0.0.0.0:5000
```

The robot requires a Pololu Maestro servo controller connected via USB (`/dev/ttyACM0`). On a dev machine without hardware, `maestro.py` will raise a `serial.SerialException` on import. Mock the `Controller` class for offline testing.

## Project Structure

- **`Project_1/`** — Complete Flask robot controller (the base to extend for Project 2)
- **`Project_2/`** — Project 2 work lives here; currently only has `testDialogFileForPractice.txt`
- **`CSCI455_Project2_DialogEngine_with_Actions.pdf`** — Full project spec
- **`DialogAPIRules.pdf`** — TangoChat/ALDialog DSL reference

## Project 1 Architecture

Strict layering: Flask routes → `Robot` → hardware components. Flask **never** touches hardware directly.

```
app.py (Flask routes)
  └── robot.py (Robot class — single instance, owns all hardware)
        ├── motor.py (Motor — channels 0,1 — speed -1.0 to 1.0)
        ├── servo.py (Servo — channels 2,3,4 — angle -90 to 90°)
        ├── head.py  (Head — wraps tilt servo ch3, pan servo ch4)
        └── speaker.py (Speaker — espeak via background thread queue)
maestro.py — Pololu serial protocol driver (third-party, do not modify)
```

**Servo channel map:**
- Ch 0: Left drive motor
- Ch 1: Right drive motor
- Ch 2: Waist rotation (hardware center is -35°, not 0°)
- Ch 3: Head tilt (up/down)
- Ch 4: Head pan (left/right)

**Positions** are in quarter-microseconds. Center = 6000. Range = 4000–8000. `setAngle()` maps degrees to this range relative to `default_position`.

`Speaker.say()` is non-blocking — queues text; background daemon thread calls `espeak`.

## Project 2 — What Needs to Be Built

Project 2 adds a **Dialog Engine** on top of Project 1. The recommended architecture (from the spec):

1. **`dialog_engine.py`** — Parses the DSL script file; performs rule matching; returns `(speak_text, [action_tags])`. Stateful: tracks current scope level and variables.
2. **`action_runner.py`** — Maps `<head_yes>`, `<head_no>`, `<arm_raise>`, `<dance90>` to robot primitives. Runs actions from a queue in a background thread (never blocks Flask).
3. **`app.py`** (extended from Project 1) — Add a `/dialog` POST endpoint accepting `{"text": "user input"}`. Add a text input box to `index.html`. Flask handler enqueues work and returns immediately.

### DSL Language Rules (from `testDialogFileForPractice.txt` and API docs)

- **Definitions:** `~name: [word1 word2 "two words"]` — expands inline in patterns and outputs
- **Rules:** `u:(pattern): output` — level `u`, `u1`, `u2`, ... determines scope depth
- **Scope:** Indentation signals parent-child relationship. When a `u:` matches and has `u1:` children, those children become the active rule set. A new top-level `u:` match clears the previous scope.
- **Wildcard capture:** `_` in a pattern captures the matched text; referenced as `$varname` in output (variable name inferred from context — see spec). If variable never set, output `"I don't know"`.
- **Bracket choices in patterns:** `[a b "two words"]` matches any option
- **Bracket choices in outputs:** `[a b "two words"]` picks one randomly (use `--seed N` for determinism)
- **Action tags:** `<head_yes>`, `<head_no>`, `<arm_raise>`, `<dance90>` — stripped from spoken text, executed in order after speech. Unknown tags: log warning, ignore.
- **Comments:** `#` to end of line. Blank lines ignored. Whitespace around tokens is flexible.
- **Parse errors:** non-fatal (bad line) → log with filename+line number and skip; fatal (no valid `u:` rules at all) → refuse to run.

### Safety Requirements

- **Global interrupt:** input matching `stop|cancel|reset|quit` (case-insensitive) → immediately stop wheels, cancel action queue, reset to IDLE scope.
- **Bounded action times:** head actions ≤ 3s, `arm_raise` ≤ 4s, `dance90` ≤ 6s (use `threading.Timer` or `timeout` in worker).
- **Wheel deadman:** wrap any wheel movement in try/finally to guarantee `robot.stop()`.
- **Unmatched-in-scope guard:** 4 consecutive unmatched inputs while in a nested scope → reset to IDLE.
- **Max nesting depth guard:** nesting > 6 → log error, reset safely.

### State Machine States

`BOOT` → `IDLE` → `IN_SCOPE(k)` ↔ `EXEC_ACTIONS` → back to `IDLE` or `IN_SCOPE`

Print state transitions, rule matches, and action start/end to console (required for demo).
