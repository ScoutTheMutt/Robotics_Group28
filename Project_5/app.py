"""
Flask Robot Control Server — Project 5

Starts the robot web UI, LIDAR monitor, wall follower, dialog engine, and
autonomous greeter controller. Flask routes call Robot/Engine/Lidar methods;
hardware access stays inside those component classes.
"""

import argparse
import sys
import atexit

from flask import Flask, render_template, request, jsonify

from robot import Robot
from dialog_engine import DialogEngine, FatalParseError
from action_runner import ActionRunner
from lidar import LidarMonitor
from wall_follower import WallFollower
from greeter_controller import GreeterController


parser = argparse.ArgumentParser(description="Project 5 Robot Greeter Server")
parser.add_argument('--seed', type=int, default=None, help="RNG seed for deterministic dialog output")
parser.add_argument('--script', default='testDialogFileForPractice.txt',
                    help="Dialog script file to load on startup")
parser.add_argument('--lidar-port', default='/dev/ttyUSB0',
                    help="Serial port for RPLIDAR (default: /dev/ttyUSB0)")
args = parser.parse_args()


app = Flask(__name__)

# Initialize hardware
robot = Robot()
lidar = LidarMonitor(port=args.lidar_port)
robot.set_lidar(lidar)
lidar.start()

wall_follower = WallFollower(robot, lidar)
greeter = GreeterController(robot, lidar, wall_follower)

# Initialize dialog engine and action runner
engine = DialogEngine(seed=args.seed)
action_runner = ActionRunner(robot, greeter)

# Load dialog script
try:
    engine.load(args.script)
except FatalParseError as e:
    print(f"[FATAL] {e}")
    sys.exit(1)


def cleanup():
    greeter.stop()
    wall_follower.stop()
    action_runner.cancel()
    robot.stop()
    lidar.stop()
    print("Robot stopped — server shutting down")


atexit.register(cleanup)


# ===========================================================================
# Basic robot routes
# ===========================================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/drive', methods=['POST'])
def drive():
    try:
        data = request.get_json()
        if not data or 'left' not in data or 'right' not in data:
            return jsonify(status="error", message="Missing left or right speed"), 400
        left_speed = float(data['left'])
        right_speed = float(data['right'])
        if abs(left_speed) > 1.0 or abs(right_speed) > 1.0:
            return jsonify(status="error", message="Speed must be between -1.0 and 1.0"), 400
        robot.setWheelSpeeds(left_speed, right_speed)
        return jsonify(status="ok")
    except ValueError:
        return jsonify(status="error", message="Invalid speed values"), 400
    except Exception as e:
        print(f"Drive error: {e}")
        robot.stop()
        return jsonify(status="error", message=str(e)), 500


@app.route('/stop', methods=['POST', 'HEAD'])
def stop():
    try:
        robot.stop()
        return jsonify(status="ok")
    except Exception as e:
        print(f"Stop error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/calibrate', methods=['POST'])
def calibrate():
    """Test motor calibration - both wheels same speed."""
    try:
        data = request.get_json() or {}
        speed = float(data.get('speed', 0.2))
        duration = float(data.get('duration', 3.0))
        robot.testCalibration(test_speed=speed, duration=duration)
        return jsonify(status='calibration test complete')
    except Exception as e:
        print(f"Calibration error: {e}")
        robot.stop()
        return jsonify(status="error", message=str(e)), 500


@app.route('/head/pan', methods=['POST'])
def head_pan():
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
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify(status="error", message="Missing text"), 400
        text = str(data['text'])
        if len(text) > 200:
            return jsonify(status="error", message="Text too long"), 400
        robot.speak(text)
        return jsonify(status="ok")
    except Exception as e:
        print(f"Speak error: {e}")
        return jsonify(status="error", message=str(e)), 500


# ===========================================================================
# LIDAR status route
# ===========================================================================

@app.route('/lidar/status', methods=['GET'])
def lidar_status():
    """Return current front/rear blocked state from the lidar monitor."""
    return jsonify(
        front_blocked=lidar.front_blocked,
        rear_blocked=lidar.rear_blocked
    )


# ===========================================================================
# Dialog routes
# ===========================================================================

@app.route('/dialog', methods=['POST'])
def dialog():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify(status="error", message="Missing text"), 400

        user_text = str(data['text']).strip()
        if not user_text:
            return jsonify(status="error", message="Empty text"), 400

        speak_text, actions, is_interrupt = engine.process(user_text)

        if is_interrupt:
            action_runner.cancel()
            action_runner.resume()
            return jsonify(
                response=speak_text,
                state=engine.state,
                actions=[],
                matched=True,
                interrupted=True
            )

        if speak_text:
            robot.speak(speak_text)

        if actions:
            action_runner.enqueue(actions)

        return jsonify(
            response=speak_text,
            state=engine.state,
            actions=actions,
            matched=(speak_text is not None),
            interrupted=False
        )

    except Exception as e:
        print(f"Dialog error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/dialog/load', methods=['POST'])
def dialog_load():
    try:
        data = request.get_json()
        if not data or 'file' not in data:
            return jsonify(status="error", message="Missing file path"), 400
        filepath = str(data['file'])
        engine.load(filepath)
        return jsonify(status="ok", state=engine.state)
    except FatalParseError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        print(f"Dialog load error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/dialog/state', methods=['GET'])
def dialog_state():
    return jsonify(
        state=engine.state,
        scope_depth=engine.scope_depth,
        variables=engine.variables
    )


# ===========================================================================
# Autonomous wall follower routes
# ===========================================================================

@app.route('/wall_follow/start', methods=['POST'])
def wall_follow_start():
    """Start the autonomous wall follower."""
    try:
        wall_follower.start()
        return jsonify(status="ok", state=wall_follower.state)
    except Exception as e:
        print(f"Wall follow start error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/wall_follow/stop', methods=['POST'])
def wall_follow_stop():
    """Stop the autonomous wall follower."""
    try:
        wall_follower.stop()
        return jsonify(status="ok", state=wall_follower.state)
    except Exception as e:
        print(f"Wall follow stop error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/wall_follow/status', methods=['GET'])
def wall_follow_status():
    """Return current wall follower state and LIDAR zone distances."""
    return jsonify(
        state=wall_follower.state,
        front_dist=lidar.front_dist,
        front_right_dist=lidar.front_right_dist,
        right_dist=lidar.right_dist,
        rear_right_dist=lidar.rear_right_dist,
        left_dist=lidar.left_dist,
    )


# ===========================================================================
# Autonomous greeter routes
# ===========================================================================

@app.route('/greeter/start', methods=['POST'])
def greeter_start():
    """Start the autonomous greeter controller."""
    try:
        greeter.start()
        return jsonify(status="ok", state=greeter.state)
    except Exception as e:
        print(f"Greeter start error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/greeter/stop', methods=['POST'])
def greeter_stop():
    """Stop the autonomous greeter controller."""
    try:
        greeter.stop()
        return jsonify(status="ok", state=greeter.state)
    except Exception as e:
        print(f"Greeter stop error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/greeter/reset', methods=['POST'])
def greeter_reset():
    """Reset greeter to WAITING for next greeting."""
    try:
        greeter.reset()
        return jsonify(status="ok", state=greeter.state)
    except Exception as e:
        print(f"Greeter reset error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/greeter/command', methods=['POST'])
def greeter_command():
    """Keyboard fallback: inject a destination while greeter is listening."""
    try:
        data = request.get_json() or {}
        destination = str(data.get('destination', '')).strip().lower()
        if destination not in ('bathroom', 'lab'):
            return jsonify(status="error", message="Destination must be 'bathroom' or 'lab'"), 400

        accepted = greeter.inject_destination(destination)
        if not accepted:
            return jsonify(status="error", message="Greeter is not currently listening"), 409

        return jsonify(status="ok", destination=destination, state=greeter.state)
    except Exception as e:
        print(f"Greeter command error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/greeter/status', methods=['GET'])
def greeter_status():
    """Return current greeter state and destination."""
    return jsonify(
        state=greeter.state,
        destination=greeter.destination,
        running=True
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
