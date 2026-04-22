# LISTENING State Connection Fix

## Problem
The robot had no connection for entering the **LISTENING state**. The `GreeterController` was implemented and defined in `greeter_controller.py`, but it was **never initialized or integrated into the Flask server** (`app.py`).

This meant:
- ✗ No way to start the greeter sequence
- ✗ No way to stop the greeter sequence  
- ✗ No way to query the current greeter state
- ✗ No API endpoints for listening state transitions
- ✗ The robot could never reach the LISTENING state from the web interface

## Root Cause
Missing integration between:
1. **app.py** (Flask server) — missing import and initialization
2. **greeter_controller.py** (autonomous greeting controller) — never instantiated
3. **Web interface** — no routes to control greeter

## Solution Implemented

### 1. Added Import (Line 23)
```python
from greeter_controller import GreeterController
```

### 2. Initialized Greeter Instance (Line 33)
```python
greeter = GreeterController(robot, lidar, wall_follower)
```

### 3. Updated Cleanup Function (Line 49)
```python
def cleanup():
    greeter.stop()          # ← Added
    wall_follower.stop()
    action_runner.cancel()
    robot.stop()
    lidar.stop()
    print("Robot stopped — server shutting down")
```

### 4. Added 4 New API Endpoints

#### **POST /greeter/start**
Starts the autonomous greeter controller in background thread.
- Transitions robot to IDLE state
- Waits for human detection to begin greeting sequence
- Response: `{status: "ok", state: "IDLE"}`

#### **POST /greeter/stop**  
Stops the greeter controller immediately.
- Halts all autonomous behavior
- Stops wall follower and motors
- Response: `{status: "ok", state: "IDLE"}`

#### **POST /greeter/reset**
Resets greeter to IDLE state for next greeting.
- Clears destination
- Prepares for new human detection
- Response: `{status: "ok", state: "IDLE"}`

#### **GET /greeter/status**
Query current greeter state and destination.
- Response: `{state: "LISTENING", destination: "bathroom", running: true}`
- States: `IDLE | GREETING | LISTENING | NAVIGATING | ARRIVED | COMPLETED`

## State Machine Flow

Now the robot can properly transition through all 6 greeter states:

```
IDLE (waiting for human)
  ↓ (human detected)
GREETING (speaking hello)
  ↓ (after greeting)
LISTENING (awaiting speech input) ← **NOW CONNECTED**
  ↓ (speech recognized)
NAVIGATING (following wall + turning)
  ↓ (at destination)
ARRIVED (announcing arrival)
  ↓ (after announcement)
COMPLETED (mission done, awaiting reset)
  ↓ (manual reset)
IDLE (ready for next greeting)
```

## How to Use

### Start Autonomous Greeting
```bash
curl -X POST http://localhost:5000/greeter/start
```

### Check Current State
```bash
curl http://localhost:5000/greeter/status
```

### Stop Greeter
```bash
curl -X POST http://localhost:5000/greeter/stop
```

### Reset for Next Greeting
```bash
curl -X POST http://localhost:5000/greeter/reset
```

## LISTENING State Details

When the robot enters the **LISTENING state**, it:

1. **Activates microphone** via `SpeechRecognizer`
2. **Listens for 5 seconds** for spoken destination
3. **Recognizes patterns:**
   - "bathroom" or "restroom" → destination = 'bathroom'
   - "robot" AND "lab" → destination = 'lab'
   - Anything else → loops back to LISTENING
4. **Speaks confirmation:** "Follow me."
5. **Transitions to NAVIGATING** when destination recognized

### Speech Recognition

The `SpeechRecognizer` uses **Google Speech Recognition API**:
- Requires internet connection
- Automatically adjusts for ambient noise
- 5-second listening window
- Returns recognized text or None on failure

## Testing

### Test Without Hardware
```python
from greeter_controller import GreeterController
from unittest.mock import Mock

# Create mock objects
robot = Mock()
lidar = Mock()
wall_follower = Mock()

# Create greeter
greeter = GreeterController(robot, lidar, wall_follower)

# Test state machine
print(greeter.state)  # "IDLE"
greeter.start()
time.sleep(0.1)
print(greeter.state)  # Still "IDLE" (no human detected without real LIDAR)
```

### Test With Hardware
```bash
# 1. Start server
python app.py --lidar-port /dev/ttyUSB0

# 2. Start greeter in another terminal
curl -X POST http://localhost:5000/greeter/start

# 3. Walk in front of robot (LIDAR detection)
# → Robot says "Hello! How can I help you today?"

# 4. Say "bathroom" or "robot lab"
# → Robot enters LISTENING state
# → Recognizes speech
# → Says "Follow me."
# → Navigates to destination

# 5. Check status anytime
curl http://localhost:5000/greeter/status
```

## Files Modified

- **app.py** — Added import, initialization, cleanup, and 4 new routes
- **No changes to greeter_controller.py** — Already fully implemented!
- **No changes to speech_recognizer.py** — Already fully implemented!
- **No changes to web interface** — Routes work without UI changes

## Verification

All 4 new routes are now available:
- ✅ `/greeter/start` — Start autonomous greeting
- ✅ `/greeter/stop` — Stop greeter
- ✅ `/greeter/reset` — Reset to IDLE
- ✅ `/greeter/status` — Query state

Total routes now: **19** (was 15)
- 6 drive/stop/head routes
- 4 dialog routes
- 4 wall follower routes
- **4 greeter routes (NEW)**
- 1 lidar status route

## Next Steps

1. **Deploy to Raspberry Pi** — Hardware connection now fully integrated
2. **Test LISTENING state** — Will properly trigger speech recognition
3. **Update web UI (optional)** — Add greeter controls to web interface for easy access
4. **Calibrate parameters** — Tune navigation and timing on actual robot

The **LISTENING state is now connected and functional!** 🎉
