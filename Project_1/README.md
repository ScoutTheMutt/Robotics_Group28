# Robot Web Control System

Browser-based control interface for a physical robot using Flask and Python.

## System Architecture

```
Web Browser (HTML/JS) → Flask Server (on Pi) → Robot Control Code (Python)
```

## File Structure

```
.
├── app.py                  # Flask server (main application)
├── robot.py               # Robot class (owns all hardware)
├── motor.py               # Motor component class
├── servo.py               # Servo component class
├── head.py                # Head component class
├── speaker.py             # Speaker component with threading
├── hardware_test.py       # Step A verification script
├── maestro.py             # Maestro controller library (required)
├── templates/
│   └── index.html         # Web control interface
└── README.md              # This file
```

## Hardware Mapping

Based on ServoFunctions.txt:

- **Servo 0**: Forward/Backward (Left wheel)
- **Servo 1**: Left/Right (Right wheel)
- **Servo 2**: Body turn left/right (Waist)
- **Servo 3**: Head up/down (Tilt)
- **Servo 4**: Head left/right (Pan)
- **Servo 5**: Right arm lift (BROKEN - do not use)
- **Servos 6-16**: Arm servos (tested but not web-controlled)

## Step A: Hardware Bring-Up & Verification

Before running the web interface, verify hardware:

```bash
python hardware_test.py
```

This script will:
- Test drive wheels individually
- Test head tilt and pan
- Test waist rotation
- Diagnose arm servos

**Note any broken components before proceeding.**

## Installation

1. Ensure `maestro.py` library is in the same directory
2. Install Flask:
   ```bash
   pip install flask
   ```

3. Verify `espeak` is installed for voice output:
   ```bash
   sudo apt-get install espeak
   ```

## Running the Server

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000`

## Accessing the Interface

From any device on the same network:

```
http://<robot-ip-address>:5000
```

Example: `http://192.168.1.100:5000`

To find your robot's IP address:
```bash
hostname -I
```

## Web Interface Features

### Drive Control
- **Joystick**: Drag to control wheel speeds
  - Up/Down: Forward/Backward
  - Left/Right: Differential turning
  - Release: Robot stops

### Head Control
- **Pan Slider**: Move head left (-90°) to right (+90°)
- **Tilt Slider**: Move head down (-90°) to up (+90°)
- **Waist Slider**: Rotate body left/right (-90° to +90°)

### Voice Output
Four predefined phrases:
- "Hello, Hunter"
- "Hunter is so cool"
- "Please do not touch my wheels"
- "Hunter is the greatest"

### Emergency Stop
Red button stops all motion immediately

## Safety Features

The system handles:
1. **Page Refresh**: Robot stops automatically via `beforeunload` event
2. **Lost Connection**: Heartbeat monitor detects connection loss
3. **Invalid Values**: Server validates all commands before execution
4. **Command Flooding**: Each command validated independently
5. **Server Restart**: `atexit` cleanup stops robot on shutdown

## API Endpoints

### POST /drive
Control wheel speeds
```json
{
  "left": -1.0 to 1.0,
  "right": -1.0 to 1.0
}
```

### POST /stop
Emergency stop all motors

### POST /head/pan
Set head pan angle
```json
{
  "angle": -90 to 90
}
```

### POST /head/tilt
Set head tilt angle
```json
{
  "angle": -90 to 90
}
```

### POST /waist
Set waist rotation
```json
{
  "angle": -90 to 90
}
```

### POST /speak
Speak text
```json
{
  "text": "phrase to speak"
}
```

## Object-Oriented Design

Following the Software Design and Engineering for Robotics guidelines:

### Component Hierarchy
```
Robot (robot.py)
├── Motor (motor.py) - Left wheel
├── Motor (motor.py) - Right wheel
├── Servo (servo.py) - Waist
├── Head (head.py)
│   ├── Servo (servo.py) - Tilt
│   └── Servo (servo.py) - Pan
└── Speaker (speaker.py) - Background thread
```

### Key Design Principles

1. **Encapsulation**: Each hardware component is a class
2. **Single Responsibility**: Flask only routes commands
3. **No Global State**: Robot instance owns all hardware
4. **Thread Safety**: Speaker uses queue-based threading
5. **Layered Architecture**: Browser → Flask → Robot → Components → Hardware

### Flask Never Touches Hardware

```python
@app.route('/drive', methods=['POST'])
def drive():
    # Flask validates
    # Flask calls robot method
    robot.setWheelSpeeds(left, right)
    # Robot handles hardware
```

## Testing the Control Layer Independently

You can test robot control without Flask:

```python
from robot import Robot

robot = Robot()

# Test driving
robot.driveForward(0.5)
time.sleep(2)
robot.stop()

# Test head
robot.setHeadPan(45)
robot.setHeadTilt(30)

# Test speech
robot.speak("Hello world")
```

## Troubleshooting

### Robot doesn't move
1. Check hardware with `python hardware_test.py`
2. Verify servo positions (should be around 6000 for center)
3. Check Maestro USB connection

### Can't access web interface
1. Verify server is running: `python app.py`
2. Check robot IP: `hostname -I`
3. Ensure firewall allows port 5000
4. Try from robot itself: `http://localhost:5000`

### Voice doesn't work
1. Check espeak: `espeak "test"`
2. Verify audio output settings
3. Check speaker thread in Speaker class

### Connection timeout
1. Ensure devices on same network
2. Check robot WiFi connection
3. Try `ping <robot-ip>` from client device

## Known Issues

- **Servo 5** (Right arm lift) is broken and not used
- Arms are tested but not included in web interface (as per project requirements)

## Debug Log Requirements

For your project submission, maintain a debug log with:
- Date and time of each entry
- Hardware issues vs software issues
- At least one incorrect assumption discovered
- Solutions attempted and results

## Project Deliverables Checklist

- [ ] Hardware bring-up verification completed
- [ ] Robot control layer tested independently
- [ ] Flask server runs and serves webpage
- [ ] Web interface controls all required functions
- [ ] Emergency stop works
- [ ] At least 3 failure cases handled
- [ ] Live demo prepared
- [ ] Debug/reflection log completed (6+ entries)

## License

Created for Software Design and Engineering for Robotics course project.
