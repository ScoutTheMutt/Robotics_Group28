"""
Flask Control Server for Robot
Serves web interface and handles control commands
"""

from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path

# Import your robot control layer here
# from robot_control import RobotController

app = Flask(__name__)

# Initialize robot controller
# robot = RobotController()

# Store last known state for safety
robot_state = {
    'left_wheel': 0,
    'right_wheel': 0,
    'head_tilt': 90,  # neutral position
    'head_pan': 90,   # neutral position
    'waist': 90       # neutral position
}

# Safety limits
LIMITS = {
    'wheel_speed': (-100, 100),
    'head_tilt': (0, 180),
    'head_pan': (0, 180),
    'waist': (0, 180)
}

# Predefined phrases for TTS
PHRASES = {
    'phrase1': 'Hello, Hunter.',
    'phrase2': 'Hunter is so cool.',
    'phrase3': 'Please do not touch my wheels.',
    'phrase4': 'Hunter is the greatest.'
}


def validate_value(value, min_val, max_val):
    """Validate that a value is within safe limits"""
    try:
        val = float(value)
        return max(min_val, min(max_val, val))
    except (ValueError, TypeError):
        return None


def stop_robot():
    """Emergency stop - set all motors to neutral"""
    global robot_state
    robot_state['left_wheel'] = 0
    robot_state['right_wheel'] = 0
    
    # Call robot control layer stop function
    # robot.stop_all()
    
    print("ROBOT STOPPED")


@app.route('/')
def index():
    """Serve the main control interface"""
    return render_template('index.html')


@app.route('/api/drive', methods=['POST'])
def drive():
    """Handle drive commands from joystick"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Extract and validate wheel speeds
        left = validate_value(
            data.get('left', 0),
            LIMITS['wheel_speed'][0],
            LIMITS['wheel_speed'][1]
        )
        right = validate_value(
            data.get('right', 0),
            LIMITS['wheel_speed'][0],
            LIMITS['wheel_speed'][1]
        )
        
        if left is None or right is None:
            return jsonify({'error': 'Invalid wheel speed values'}), 400
        
        # Update state
        robot_state['left_wheel'] = left
        robot_state['right_wheel'] = right
        
        # Send to robot control layer
        # robot.set_wheel_speeds(left, right)
        
        print(f"Drive command: L={left:.1f}, R={right:.1f}")
        
        return jsonify({
            'status': 'success',
            'left': left,
            'right': right
        })
        
    except Exception as e:
        print(f"Error in drive endpoint: {e}")
        stop_robot()
        return jsonify({'error': str(e)}), 500


@app.route('/api/head', methods=['POST'])
def head():
    """Handle head tilt and pan commands"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        response = {}
        
        # Handle tilt if present
        if 'tilt' in data:
            tilt = validate_value(
                data['tilt'],
                LIMITS['head_tilt'][0],
                LIMITS['head_tilt'][1]
            )
            if tilt is None:
                return jsonify({'error': 'Invalid tilt value'}), 400
            
            robot_state['head_tilt'] = tilt
            # robot.set_head_tilt(tilt)
            response['tilt'] = tilt
            print(f"Head tilt: {tilt:.1f}")
        
        # Handle pan if present
        if 'pan' in data:
            pan = validate_value(
                data['pan'],
                LIMITS['head_pan'][0],
                LIMITS['head_pan'][1]
            )
            if pan is None:
                return jsonify({'error': 'Invalid pan value'}), 400
            
            robot_state['head_pan'] = pan
            # robot.set_head_pan(pan)
            response['pan'] = pan
            print(f"Head pan: {pan:.1f}")
        
        response['status'] = 'success'
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in head endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/waist', methods=['POST'])
def waist():
    """Handle waist rotation commands"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        rotation = validate_value(
            data.get('rotation', 90),
            LIMITS['waist'][0],
            LIMITS['waist'][1]
        )
        
        if rotation is None:
            return jsonify({'error': 'Invalid rotation value'}), 400
        
        robot_state['waist'] = rotation
        # robot.set_waist_rotation(rotation)
        
        print(f"Waist rotation: {rotation:.1f}")
        
        return jsonify({
            'status': 'success',
            'rotation': rotation
        })
        
    except Exception as e:
        print(f"Error in waist endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/speak', methods=['POST'])
def speak():
    """Handle text-to-speech commands"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        phrase_id = data.get('phrase')
        
        if phrase_id not in PHRASES:
            return jsonify({'error': 'Invalid phrase ID'}), 400
        
        text = PHRASES[phrase_id]
        
        # Send to robot TTS system
        # robot.speak(text)
        
        print(f"Speaking: {text}")
        
        return jsonify({
            'status': 'success',
            'text': text
        })
        
    except Exception as e:
        print(f"Error in speak endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def stop():
    """Emergency stop endpoint"""
    try:
        stop_robot()
        return jsonify({'status': 'success', 'message': 'Robot stopped'})
    except Exception as e:
        print(f"Error in stop endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Get current robot state"""
    return jsonify({
        'status': 'success',
        'state': robot_state
    })


# Error handlers for safety
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    stop_robot()
    return jsonify({'error': 'Server error - robot stopped'}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("Robot Control Server Starting")
    print("=" * 50)
    print(f"Access the interface at: http://<robot-ip>:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run Flask server
    # For development: debug=True
    # For production: debug=False, threaded=True
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,
        debug=True,
        threaded=True
    )
