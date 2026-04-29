# Dialog Engine Integration with Greeter Controller

## Overview

The **greeter function is now fully integrated into the dialog engine**. Instead of being controlled only via direct HTTP routes (`/greeter/start`, `/greeter/stop`, etc.), the greeter can now be activated/deactivated as **dialog actions** within conversation scripts.

This allows for a more natural conversational flow where the robot can enter listening mode based on what users say.

---

## How It Works

### Architecture

```
Dialog Engine (dialog_engine.py)
    ↓
    Recognizes pattern match with <action> tags
    ↓
Action Runner (action_runner.py)
    ↓
    Dispatches action handlers
    ↓
Greeter Controller (greeter_controller.py)
    ↓
    Executes autonomous greeting sequence
```

### Action Tags

Two new action tags are now recognized:

| Action Tag | Effect | Time Cap |
|-----------|--------|----------|
| `<start_greeter>` | Activates autonomous greeting (IDLE state) | 1.0 sec |
| `<stop_greeter>` | Stops autonomous greeting | 1.0 sec |

These are part of the dialog output, just like `<head_yes>`, `<head_no>`, `<arm_raise>`, and `<dance90>`.

---

## Usage in Dialog Scripts

### Basic Example

```plaintext
u:([start greeter]): Starting greeting mode. <start_greeter>

u:([stop greeter]): Stopping greeting mode. <stop_greeter>
```

When the user says "start greeter", the robot:
1. Matches the pattern `[start greeter]`
2. Speaks: "Starting greeting mode."
3. Executes action: `<start_greeter>`
4. Greeter controller transitions from IDLE to waiting for human detection

### Scope Example

You can have conditional responses after activating the greeter:

```plaintext
u:([activate greeter]): I'll start greeting people now. <start_greeter>
    
    % Now in nested scope u1 - respond to user while greeter is running
    u1:(~affirm): Great!
    u1:(~deny): Okay, I'll stop. <stop_greeter>
    u1:([how long]): Until you tell me to stop.
    u1:([stop]): Done greeting. <stop_greeter>
```

### Complex Workflow

```plaintext
u:(can you greet): Sure thing! <start_greeter>
    u1:(~affirm): Activating greeter now.
    u1:(~deny): [okay never mind|no problem] <stop_greeter>

u:(~greet): [Hi!|Hello!|Hey there!] <head_yes>

% Command to exit greeter mode
u:([back to normal mode]): Deactivating greeter. <stop_greeter>
```

---

## Integration Details

### Dialog Engine Changes

**File: `dialog_engine.py`**

Updated `KNOWN_ACTIONS` set to include greeter actions:

```python
KNOWN_ACTIONS = {
    'head_yes', 
    'head_no', 
    'arm_raise', 
    'dance90',
    'start_greeter',      # ← NEW
    'stop_greeter'        # ← NEW
}
```

### Action Runner Changes

**File: `action_runner.py`**

1. **Constructor** now accepts optional `greeter` parameter:
```python
def __init__(self, robot, greeter=None):
    self.robot = robot
    self.greeter = greeter  # ← NEW
    # ... rest of init
```

2. **Action dispatch** now handles greeter actions:
```python
handler = {
    'head_yes': self._head_yes,
    'head_no': self._head_no,
    'arm_raise': self._arm_raise,
    'dance90': self._dance90,
    'start_greeter': self._start_greeter,   # ← NEW
    'stop_greeter': self._stop_greeter,     # ← NEW
}.get(action_name)
```

3. **New action handlers**:
```python
def _start_greeter(self):
    """Start the autonomous greeter controller."""
    if self.greeter is None:
        print("[ACTION] Greeter not available")
        return
    try:
        self.greeter.start()
        print("[ACTION] Greeter started")
    except Exception as e:
        print(f"[ACTION] Error starting greeter: {e}")
    self.resume()

def _stop_greeter(self):
    """Stop the autonomous greeter controller."""
    if self.greeter is None:
        print("[ACTION] Greeter not available")
        return
    try:
        self.greeter.stop()
        print("[ACTION] Greeter stopped")
    except Exception as e:
        print(f"[ACTION] Error stopping greeter: {e}")
    self.resume()
```

4. **Time caps** for actions:
```python
CAPS = {
    'head_yes': 3.0,
    'head_no': 3.0,
    'arm_raise': 4.0,
    'dance90': 6.0,
    'start_greeter': 1.0,   # ← NEW (quick start)
    'stop_greeter': 1.0,    # ← NEW (quick stop)
}
```

### Flask App Changes

**File: `app.py`**

Pass greeter to action runner during initialization:

```python
action_runner = ActionRunner(robot, greeter)  # ← Pass greeter
```

---

## State Flow

When a dialog rule triggers `<start_greeter>`:

```
Dialog Rule Matched
    ↓
Speak response text
    ↓
Enqueue [action_name] to ActionRunner
    ↓
ActionRunner._dispatch('start_greeter')
    ↓
ActionRunner._start_greeter()
    ↓
greeter.start()  # Transitions to IDLE, waits for human
    ↓
Greeter main loop detects human
    ↓
Robot enters GREETING state
    ↓
Robot says "Hello! How can I help you today?"
    ↓
Robot enters LISTENING state
    ↓
Speech recognition captures destination
    ↓
Robot navigates autonomously
```

When `<stop_greeter>` is triggered:

```
Dialog Rule Matched
    ↓
Speak response text
    ↓
Enqueue [action_name] to ActionRunner
    ↓
ActionRunner._dispatch('stop_greeter')
    ↓
ActionRunner._stop_greeter()
    ↓
greeter.stop()  # Halts all autonomous behavior
    ↓
Robot returns to manual control
```

---

## Testing

### Test 1: Activate Greeter via Dialog

```bash
curl -X POST http://localhost:5000/dialog \
  -H "Content-Type: application/json" \
  -d '{"text": "start greeter"}'
```

**Expected Response:**
```json
{
  "response": "Starting greeting mode.",
  "state": "IDLE",
  "actions": ["start_greeter"],
  "matched": true,
  "interrupted": false
}
```

**Expected Behavior:**
- Greeter controller starts in background
- Waits for human detection
- Eventually transitions to GREETING → LISTENING state

### Test 2: Deactivate Greeter via Dialog

```bash
curl -X POST http://localhost:5000/dialog \
  -H "Content-Type: application/json" \
  -d '{"text": "stop greeter"}'
```

**Expected Response:**
```json
{
  "response": "Stopping greeting mode.",
  "state": "IDLE",
  "actions": ["stop_greeter"],
  "matched": true,
  "interrupted": false
}
```

**Expected Behavior:**
- Greeter controller stops
- Robot returns to idle state
- Manual control via web interface works again

### Test 3: Load Custom Dialog Script

```bash
curl -X POST http://localhost:5000/dialog/load \
  -H "Content-Type: application/json" \
  -d '{"file": "greeterDialogExample.txt"}'
```

Then interact with the dialog:

```bash
# Activate
curl -X POST http://localhost:5000/dialog \
  -H "Content-Type: application/json" \
  -d '{"text": "activate greeter"}'

# Check state
curl http://localhost:5000/greeter/status

# Deactivate
curl -X POST http://localhost:5000/dialog \
  -H "Content-Type: application/json" \
  -d '{"text": "deactivate greeter"}'
```

---

## Example Dialog Script

See **`greeterDialogExample.txt`** in the Final Project directory.

Key features:
- Simple activation/deactivation patterns
- Scope-based responses while greeter is active
- Multiple ways to activate/deactivate
- Testing patterns

Usage:
```bash
python app.py --script greeterDialogExample.txt --lidar-port /dev/ttyUSB0
```

---

## Error Handling

### Greeter Not Available

If the greeter cannot be initialized (e.g., missing dependencies), the action will log a warning but not crash:

```
[ACTION] Greeter not available
```

The dialog response will still be spoken, but the greeter won't actually start.

### Action Timeout

Actions have a 1-second timeout. If `greeter.start()` or `greeter.stop()` takes longer, a watchdog timer will interrupt it:

```
[ACTION] TIMEOUT start_greeter — cancelling
```

### Missing Greeter Parameter

If action runner was created without passing the greeter instance:

```python
action_runner = ActionRunner(robot)  # ← No greeter!
```

The action will safely degrade:
```
[ACTION] Greeter not available
```

---

## Integration Points

### 1. **Dialog Engine** → Recognizes `<start_greeter>` and `<stop_greeter>` tags
### 2. **Action Runner** → Dispatches actions to greeter methods
### 3. **Greeter Controller** → Executes autonomous greeting sequence
### 4. **Robot** → Physical hardware abstraction
### 5. **LIDAR** → Provides human detection and safety

All components communicate through well-defined interfaces without direct coupling.

---

## Benefits

✅ **Natural conversation flow** — Greeter activates through dialogue, not just web buttons  
✅ **Conditional triggering** — Can activate greeter only in certain contexts  
✅ **Scope-based behavior** — Different responses while greeter is running  
✅ **Easy to test** — Use curl/Postman to trigger from dialog  
✅ **Follows pattern** — Same architecture as other actions (head_yes, dance90, etc.)  
✅ **Graceful degradation** — Missing greeter doesn't crash dialog  
✅ **Safe timeouts** — All actions have hard time caps  

---

## Next Steps

1. **Load dialog script**: Use `greeterDialogExample.txt` as starting point
2. **Test activation**: Send "activate greeter" through dialog API
3. **Monitor greeter state**: Watch logs and use `/greeter/status` endpoint
4. **Customize patterns**: Edit dialog script to add your own greeting triggers
5. **Deploy to hardware**: Robot will now support full conversational control

---

## Files Modified

- ✅ `dialog_engine.py` — Added 'start_greeter', 'stop_greeter' to KNOWN_ACTIONS
- ✅ `action_runner.py` — Added greeter parameter, handlers, time caps
- ✅ `app.py` — Pass greeter to action_runner
- ✅ `greeterDialogExample.txt` — New example dialog script (NEW)

## Files Unchanged

- ✅ `greeter_controller.py` — No changes (already fully implemented)
- ✅ `speech_recognizer.py` — No changes (already fully implemented)
- ✅ `human_detector.py` — No changes (already fully implemented)

---

## Summary

The greeter function is now a first-class citizen in the dialog engine. When the user's input matches a pattern with a greeter action tag, the robot will automatically activate the autonomous greeting sequence. This provides a seamless conversational interface for controlling the robot's behavior.
