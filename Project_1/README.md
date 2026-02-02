# Robot Control Interface - Flask Server & Web UI

This package contains the Flask web server and HTML control interface for Project 1A.

## 📁 File Structure

```
Project_1/
├── flaskServer.py            # Flask server application
├── templates/
│    └── index.html           # Web control interface
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

On your Raspberry Pi, install Flask:

```bash
pip3 install -r requirements.txt
```

### 2. Integrate Your Robot Control Layer

Open `robot_server.py` and uncomment/modify these sections:

**Import your robot controller:**
```python
from robot_control import RobotController  # Line ~7
```

**Initialize robot:**
```python
robot = RobotController()  # Line ~12
```

**Connect API endpoints to robot functions:**
- Line ~90: `robot.set_wheel_speeds(left, right)`
- Line ~132: `robot.set_head_tilt(tilt)`
- Line ~145: `robot.set_head_pan(pan)`
- Line ~179: `robot.set_waist_rotation(rotation)`
- Line ~203: `robot.speak(text)`
- Line ~57: `robot.stop_all()`

### 3. Run the Server

```bash
python3 robot_server.py
```

The server will start on port 5000. You'll see:
```
Robot Control Server Starting
Access the interface at: http://<robot-ip>:5000
```

### 4. Access the Interface

From your phone or laptop (on the same network):
```
http://<your-robot-ip>:5000
```

Replace `<your-robot-ip>` with your Raspberry Pi's IP address.

## 🎮 Control Interface Features

### Drive Control (Joystick)
- **Mouse/Touch joystick** for intuitive control
- Differential drive: push forward/back, left/right
- Dead zone to prevent drift
- Real-time wheel speed display
- Auto-stop when released

### Head Control (Sliders)
- **Tilt slider**: 0° to 180° (up/down)
- **Pan slider**: 0° to 180° (left/right)
- Real-time angle display
- Smooth movement with throttling

### Waist Control (Slider)
- **Rotation slider**: 0° to 180°
- Real-time position display

### Voice Output (Buttons)
Four predefined phrases:
1. "Hello, Hunter."
2. "Hunter is so cool."
3. "Please do not touch my wheels."
4. "Hunter is the greatest."

### Emergency Stop
- Large red **EMERGENCY STOP** button
- Immediately stops all motors
- Sets robot to neutral state

## 🛡️ Safety Features

The system includes multiple safety mechanisms:

### 1. **Input Validation**
- All values checked against safe limits
- Invalid commands rejected before reaching robot
- Type checking and range enforcement

### 2. **Command Throttling**
- Prevents command flooding (100ms minimum between commands)
- Reduces network and processing load
- Smoother robot operation

### 3. **Connection Monitoring**
- Heartbeat every 3 seconds
- Automatic connection loss detection
- Visual warning overlay when disconnected

### 4. **Page Lifecycle Handling**
- Auto-stop on page refresh
- Auto-stop on page close
- Auto-stop when tab becomes inactive
- Auto-stop when leaving the page

### 5. **Error Recovery**
- Try-catch blocks around all API calls
- Automatic robot stop on server errors
- User-friendly error messages
- Graceful degradation

## 📊 API Endpoints

### POST /api/drive
Control wheel speeds
```json
{
  "left": -100 to 100,
  "right": -100 to 100
}
```

### POST /api/head
Control head position
```json
{
  "tilt": 0 to 180,    // optional
  "pan": 0 to 180      // optional
}
```

### POST /api/waist
Control waist rotation
```json
{
  "rotation": 0 to 180
}
```

### POST /api/speak
Trigger text-to-speech
```json
{
  "phrase": "phrase1" | "phrase2" | "phrase3" | "phrase4"
}
```

### POST /api/stop
Emergency stop (no body required)

### GET /api/status
Get current robot state

## 🔧 Configuration

### Safety Limits (in robot_server.py)
```python
LIMITS = {
    'wheel_speed': (-100, 100),
    'head_tilt': (0, 180),
    'head_pan': (0, 180),
    'waist': (0, 180)
}
```

### Timing Parameters (in index.html)
```javascript
const COMMAND_THROTTLE = 100;  // ms between commands
const JOYSTICK_DEAD_ZONE = 10; // pixels
```

### Server Settings (in robot_server.py)
```python
app.run(
    host='0.0.0.0',     # Listen on all interfaces
    port=5000,          # Port number
    debug=True,         # Set False for production
    threaded=True       # Handle multiple requests
)
```

## 📱 Mobile Compatibility

The interface is fully responsive and works on:
- ✅ Desktop browsers (Chrome, Firefox, Safari, Edge)
- ✅ Mobile phones (iOS Safari, Android Chrome)
- ✅ Tablets (iPad, Android tablets)

Touch controls automatically enabled on mobile devices.

## 🐛 Troubleshooting

### Can't access the interface
1. Check Raspberry Pi is on the network: `ip addr show`
2. Verify port 5000 is open: `sudo netstat -tulpn | grep 5000`
3. Try accessing from Pi itself: `curl http://localhost:5000`
4. Check firewall: `sudo ufw status`

### Robot not responding
1. Check console output in terminal running Flask
2. Verify robot control layer is connected
3. Check hardware connections
4. Review debug log for errors

### Joystick not working
1. Check browser console for JavaScript errors (F12)
2. Verify mouse/touch events are registering
3. Try refreshing the page
4. Check if joystick is inside the container

### Commands being ignored
1. Check command throttling (100ms delay)
2. Verify values are within safe limits
3. Check network connection status
4. Review server logs for validation errors

## 🎯 Testing Failure Cases

To demonstrate failure handling for the project:

### 1. Page Refresh
- Control robot, then refresh browser
- Robot should stop immediately

### 2. Network Loss
- Disconnect WiFi while controlling
- Connection lost overlay should appear
- Robot should stop

### 3. Invalid Commands
- Use browser console to send bad data:
```javascript
fetch('/api/drive', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({left: 999, right: 'bad'})
})
```
- Command should be rejected

### 4. Command Flooding
- Rapidly click buttons
- System should throttle and handle gracefully

### 5. Server Restart
- Stop and restart Flask while interface is open
- Interface should detect and show connection error

## 📝 Debug Log Suggestions

Document these entries for your reflection log:

1. **Initial setup issues**: WiFi, IP addressing, port conflicts
2. **Flask integration**: Connecting to robot control layer
3. **Joystick math**: Differential drive calculations, dead zones
4. **Safety testing**: Each failure case and how it was handled
5. **Hardware problems**: Which components worked vs. needed fixing
6. **Network issues**: Latency, packet loss, connection drops
7. **Incorrect assumptions**: What you thought would work but didn't

## 🎨 Customization

### Change Phrases
Edit the `PHRASES` dictionary in `robot_server.py`:
```python
PHRASES = {
    'phrase1': 'Your custom phrase here',
    'phrase2': 'Another phrase',
    ...
}
```

### Modify Colors
Edit CSS variables in `templates/index.html`:
```css
:root {
    --primary: #1a1a2e;      /* Dark background */
    --accent: #0f4c75;       /* Primary color */
    --highlight: #3282b8;    /* Bright accent */
    --danger: #e94560;       /* Stop button */
}
```

### Adjust Layout
The control grid automatically adjusts for screen size. Modify in `index.html`:
```css
.control-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
}
```

## ✅ Project Requirements Checklist

- [x] Flask server runs on robot
- [x] HTML/JS hosted by Flask
- [x] Works on local network (no cloud)
- [x] Joystick for drive control
- [x] Sliders for head tilt/pan
- [x] Buttons for voice output (4 phrases)
- [x] Data validation on server
- [x] Safe limits enforced
- [x] Emergency stop function
- [x] Connection monitoring
- [x] Failure case handling (5+ scenarios)
- [x] Mobile-friendly interface

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review console output (both server and browser)
3. Test each component individually
4. Consult your robot control layer documentation

Good luck with your demo! 🤖✨
