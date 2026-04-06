"""
Flask Robot Control Server — Project 2
Extends Project 1 with a Dialog Engine and Action Runner.
Flask NEVER touches hardware directly — only calls Robot/Engine methods.
"""

import argparse
import sys

# Parse CLI args before importing Flask (so --script/--seed work)
parser = argparse.ArgumentParser(description="Project 2 Robot Dialog Server")
parser.add_argument('--seed', type=int, default=None, help="RNG seed for deterministic output")
parser.add_argument('--script', default='testDialogFileForPractice.txt',
                    help="Dialog script file to load on startup")
args = parser.parse_args()

from flask import Flask, render_template, request, jsonify
from robot import Robot
import atexit

from dialog_engine import DialogEngine, FatalParseError
from action_runner import ActionRunner

app = Flask(__name__)

# Initialize robot (single instance)
robot = Robot()

# Initialize dialog engine and action runner
engine = DialogEngine(seed=args.seed)
action_runner = ActionRunner(robot)

# Load script (fatal if no valid rules)
try:
    engine.load(args.script)
except FatalParseError as e:
    print(f"[FATAL] {e}")
    sys.exit(1)


# Safety: ensure robot stops when server exits
def cleanup():
    action_runner.cancel()
    robot.stop()
    print("Robot stopped - server shutting down")

atexit.register(cleanup)


# ===========================================================================
# Project 1 routes (unchanged)
# ===========================================================================

@app.route('/')
def index():
    """Serve the main control page"""
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


@app.route('/stop', methods=['POST'])
def stop():
    try:
        robot.stop()
        return jsonify(status="ok")
    except Exception as e:
        print(f"Stop error: {e}")
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
# Project 2 dialog routes
# ===========================================================================

@app.route('/dialog', methods=['POST'])
def dialog():
    """
    Process a dialog turn.
    Expects JSON: {"text": "user input"}
    Returns: {"response": str|null, "state": str, "actions": list, "matched": bool}
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify(status="error", message="Missing text"), 400

        user_text = str(data['text']).strip()
        if not user_text:
            return jsonify(status="error", message="Empty text"), 400

        speak_text, actions, is_interrupt = engine.process(user_text)

        if is_interrupt:
            # Safety interrupt: cancel all actions and stop wheels
            action_runner.cancel()
            action_runner.resume()  # Ready for future actions
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
    """
    Load a new dialog script.
    Expects JSON: {"file": "path/to/script.txt"}
    """
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
    """Return current dialog engine state."""
    return jsonify(
        state=engine.state,
        scope_depth=engine.scope_depth,
        variables=engine.variables
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
