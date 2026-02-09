"""
Flask Robot Control Server
Serves web interface and handles control commands
Flask NEVER touches hardware - only calls Robot methods
"""

from flask import Flask, render_template, request, jsonify
from robot import Robot
import atexit

app = Flask(__name__)

# Initialize robot (single instance)
robot = Robot()

# Safety: ensure robot stops when server exits
def cleanup():
    robot.stop()
    print("Robot stopped - server shutting down")

atexit.register(cleanup)


@app.route('/')
def index():
    """Serve the main control page"""
    return render_template('index.html')


@app.route('/drive', methods=['POST'])
def drive():
    """
    Handle drive commands from joystick
    Expects JSON: {"left": <speed>, "right": <speed>}
    Speeds range from -1.0 to 1.0
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'left' not in data or 'right' not in data:
            return jsonify(status="error", message="Missing left or right speed"), 400
        
        left_speed = float(data['left'])
        right_speed = float(data['right'])
        
        # Additional validation
        if abs(left_speed) > 1.0 or abs(right_speed) > 1.0:
            return jsonify(status="error", message="Speed must be between -1.0 and 1.0"), 400
        
        # Send to robot
        robot.setWheelSpeeds(left_speed, right_speed)
        
        return jsonify(status="ok")
        
    except ValueError:
        return jsonify(status="error", message="Invalid speed values"), 400
    except Exception as e:
        print(f"Drive error: {e}")
        robot.stop()  # Safety first
        return jsonify(status="error", message=str(e)), 500


@app.route('/stop', methods=['POST'])
def stop():
    """Emergency stop command"""
    try:
        robot.stop()
        return jsonify(status="ok")
    except Exception as e:
        print(f"Stop error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/head/pan', methods=['POST'])
def head_pan():
    """
    Set head pan position
    Expects JSON: {"angle": <degrees>}
    Angle range: -90 to 90
    """
    try:
        data = request.get_json()
        
        if not data or 'angle' not in data:
            return jsonify(status="error", message="Missing angle"), 400
        
        angle = float(data['angle'])
        
        if abs(angle) > 90:
            return jsonify(status="error", message="Angle must be between -90 and 90"), 400
        
        robot.setHeadPan(angle)
        
        return jsonify(status="ok")
        
    except ValueError:
        return jsonify(status="error", message="Invalid angle value"), 400
    except Exception as e:
        print(f"Head pan error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/head/tilt', methods=['POST'])
def head_tilt():
    """
    Set head tilt position
    Expects JSON: {"angle": <degrees>}
    Angle range: -90 to 90
    """
    try:
        data = request.get_json()
        
        if not data or 'angle' not in data:
            return jsonify(status="error", message="Missing angle"), 400
        
        angle = float(data['angle'])
        
        if abs(angle) > 90:
            return jsonify(status="error", message="Angle must be between -90 and 90"), 400
        
        robot.setHeadTilt(angle)
        
        return jsonify(status="ok")
        
    except ValueError:
        return jsonify(status="error", message="Invalid angle value"), 400
    except Exception as e:
        print(f"Head tilt error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/waist', methods=['POST'])
def waist():
    """
    Set waist rotation
    Expects JSON: {"angle": <degrees>}
    Angle range: -90 to 90
    """
    try:
        data = request.get_json()
        
        if not data or 'angle' not in data:
            return jsonify(status="error", message="Missing angle"), 400
        
        angle = float(data['angle'])
        
        if abs(angle) > 90:
            return jsonify(status="error", message="Angle must be between -90 and 90"), 400
        
        robot.setWaistRotation(angle)
        
        return jsonify(status="ok")
        
    except ValueError:
        return jsonify(status="error", message="Invalid angle value"), 400
    except Exception as e:
        print(f"Waist rotation error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/speak', methods=['POST'])
def speak():
    """
    Speak a phrase
    Expects JSON: {"text": "<phrase>"}
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify(status="error", message="Missing text"), 400
        
        text = str(data['text'])
        
        # Basic validation - limit length
        if len(text) > 200:
            return jsonify(status="error", message="Text too long"), 400
        
        robot.speak(text)
        
        return jsonify(status="ok")
        
    except Exception as e:
        print(f"Speak error: {e}")
        return jsonify(status="error", message=str(e)), 500


if __name__ == '__main__':
    # Run on all interfaces so it's accessible from network
    # Use port 5000 (can be changed)
    app.run(host='0.0.0.0', port=5000, debug=False)
