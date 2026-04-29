# Final Project Quick Reference Guide

## Starting the Robot Server

### On Raspberry Pi (with hardware):
```bash
cd ~/Robotics_Group28/Final\ Project
python app.py --seed 42 --script testDialogFileForPractice.txt --lidar-port /dev/ttyUSB0
```

### Access the Web Interface:
- Open browser: `http://localhost:5000`
- Or from another machine: `http://<pi-ip>:5000`

---

## Web Interface Controls

### Drive Control (Joystick)
- Drag joystick to control robot movement
- Center = stop
- Up = forward
- Down = backward
- Left/Right = rotation

### Head Control (Sliders)
- **Pan:** -90° (left) to +90° (right)
- **Tilt:** -90° (down) to +90° (up)
- **Waist:** -90° to +20° (mechanical center at -35°)

### Voice Output
- Pre-loaded phrases available
- Custom text in code

### LIDAR Safety Display
- **Front:** 0-30° and 330-360° zones
- **Rear:** 150-210° zone
- Green = clear, Red = blocked
- Automatically prevents collisions

### Wall Follower
- **Start:** Begins autonomous right-wall following
- **Stop:** Halts autonomous navigation
- **Status:** Shows RUNNING/STOPPED state
- **Distances:** Real-time zone distances

### Dialog Engine
- **Load Script:** Select `.txt` dialog file
- **Refresh State:** Get current engine state
- **Type & Send:** Process user dialog input
- **Conversation Log:** Shows all interactions

---

## Dialog Script Format

```
% Comments start with %

u: (~name [patterns])
    - Response option 1
    - Response option 2

u: (~greeting [hello hi hey])
    a: (user_destination)
        - I can help you with that!
        ^{action_name arg1 arg2}

~name: [
    pattern1
    pattern2
]
```

### Available Variables
- `$varname` - Reference variable in response
- Set in action definitions

---

## Troubleshooting

### LIDAR Not Found
```bash
# Check if connected
ls /dev/ttyUSB*

# Update port in app.py call
python app.py --lidar-port /dev/ttyUSB1
```

### Speech Recognition Error
- Requires internet connection (uses Google API)
- Install: `pip install SpeechRecognition`

### Servo/Motor Issues
```bash
# Verify Maestro connection
ls /dev/ttyACM*

# Run diagnostic
python test.py
```

### Dialog Engine Won't Load
- Check script file path is correct
- Verify syntax with sample `testDialogFileForPractice.txt`

---

## Testing (Without Hardware)

### Test Wall Follower Decision Logic:
```bash
python test_wall_follower.py
```
Output shows state transitions for various distance inputs.

### Test LIDAR Driver:
```bash
python test.py
```
Attempts LIDAR connection and reports distances.

---

## File Descriptions

| File | Purpose | Lines |
|------|---------|-------|
| app.py | Flask server + routes | 283 |
| robot.py | Hardware abstraction | 153 |
| wall_follower.py | Autonomous navigation | 174 |
| greeter_controller.py | Greeting sequence | 223 |
| dialog_engine.py | Dialog processing | ~600 |
| index.html | Web interface | 955 |
| lidar.py | LIDAR monitor | ~300 |
| motor.py | Motor control | ~50 |
| servo.py | Servo control | ~50 |

---

## Important Constants

### Wall Following
```python
WALL_TARGET_MM   = 1750   # desired distance from wall
WALL_LOWER_MM    = 700    # too close threshold
WALL_UPPER_MM    = 2000   # too far threshold
FRONT_STOP_MM    = 450    # obstacle detection
BASE_SPEED       = 0.40   # nominal forward speed
```

### Safety
```python
_SPEED_THRESHOLD = 0.05   # minimum speed for safety checks
# Pure turns (opposite speeds) always allowed
# Forward/backward only blocked when LIDAR detects obstruction
```

### LIDAR Zones
```
Front: 0-30° and 330-360°
Front-Right: 30-90°
Right: 90-150°
Rear-Right: 150-210°
```

---

## Performance Metrics

- **Joystick Update Rate:** 60 FPS (JS)
- **Wall Follower Loop:** 10 Hz (Python)
- **LIDAR Polling:** ~30 Hz
- **Dialog Processing:** <100ms
- **Web Response Time:** <50ms (typical)

---

## Safety Features

✅ **LIDAR Safety Stops** - Prevents forward/backward on obstruction  
✅ **Speed Limiting** - All motors capped at 75% for drive  
✅ **Emergency Stop** - Red button stops all motion immediately  
✅ **Automatic Cleanup** - All systems stop on server shutdown  
✅ **Thread-Safe Operations** - All components use locks where needed  

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Joystick not moving robot | Check drive route responding with `/drive` POST |
| LIDAR showing CLEAR but robot can't move | Check if `front_blocked` flag is stuck in code |
| Dialog not responding | Load script with `/dialog/load` POST first |
| Wall follower not starting | Verify LIDAR is returning valid distances |
| Head servo stuck | Check servo angle limits: -90 to +90 |
| Motor spins wrong direction | May be physical wiring - flip motor connections |

---

## Next Steps for Testing

1. **Verify Hardware Connections:**
   - Maestro to Pi via USB
   - LIDAR to Pi via USB serial
   - Wheel motors on Maestro channels 0-1
   - Head servos on channels 3-4
   - Waist servo on channel 2

2. **Test Basic Motion:**
   - Use joystick to verify forward/backward/turn
   - Use head sliders to verify servo movement

3. **Test Safety:**
   - Put hand in front of LIDAR
   - Verify forward motion is blocked
   - Test emergency stop button

4. **Test Autonomous Mode:**
   - Load dialog script
   - Start wall follower
   - Verify automatic navigation

5. **Test Advanced Features:**
   - Activate greeter controller
   - Test speech recognition
   - Run full autonomous greeting sequence

---

## Project Architecture Diagram

```
┌─────────────────────────────────────┐
│         Web Browser (HTML/JS)       │
├─────────────────────────────────────┤
│     Flask Server (app.py)           │
│  ┌──────────────────────────────┐   │
│  │   15 API Endpoints           │   │
│  └──────────────────────────────┘   │
├─────────────────────────────────────┤
│  ┌────────────────────────────────┐ │
│  │  Robot Abstraction (robot.py)  │ │
│  │  - Wheel speeds                │ │
│  │  - Head/Waist angles           │ │
│  │  - Speech synthesis            │ │
│  │  - LIDAR safety gates          │ │
│  └────────────────────────────────┘ │
├─────────────────────────────────────┤
│  ┌──────────┬──────────┬──────────┐ │
│  │  Dialog  │   Wall   │ Greeter  │ │
│  │ Engine   │ Follower │Controller│ │
│  └──────────┴──────────┴──────────┘ │
├─────────────────────────────────────┤
│  Hardware Drivers                   │
│  ├─ Maestro (maestro.py)            │
│  ├─ LIDAR (lidar.py)                │
│  ├─ Motors (motor.py)               │
│  ├─ Servos (servo.py)               │
│  ├─ Speaker (speaker.py)            │
│  └─ Audio (listen.py)               │
└─────────────────────────────────────┘
```

---

## Contact / Support

- **Project Location:** `/home/owen/Documents/Classes/Robotics-455/Robotics_Group28/Final Project/`
- **Repository:** `Robotics_Group28` (main branch)
- **Documentation:** `PROJECT_COMPLETION_SUMMARY.md` (in project directory)
