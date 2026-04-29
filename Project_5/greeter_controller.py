"""
GreeterController — Final Project autonomous greeter FSM.

State machine:
  WAITING               → human detected within range
  GREETING              → speaks greeting, transitions immediately
  LISTENING             → waits for speech (or keyboard command injected via inject_destination())
  TURNING_AROUND        → executes 180° turn in place
  ALIGNING_TO_HALLWAY   → drives forward until walls appear on both sides
  MOVING_TO_T           → drives straight until front wall is detected
  TURNING_TO_DESTINATION → executes 90° turn (RIGHT command=bathroom, LEFT command=lab)
  FINAL_MOVEMENT        → drives straight ~5 seconds to destination
  STOPPED               → announces arrival; awaits reset

Obstacle avoidance:
  - Forward-motion states use robot.setWheelSpeeds() safety checks. The T-intersection
    approach stops early when front_dist is below T_FRONT_MM.

Layout after robot turns around and drives toward the T-intersection:
  Bathroom  = turn right command, which physically turns left on this robot
  Robot Lab = turn left command, which physically turns right on this robot
"""

import threading
import time

# ---------------------------------------------------------------------------
# Tunable — adjust after testing on hardware
# ---------------------------------------------------------------------------
HUMAN_DETECT_MM   = 1500   # front distance that triggers human detection
TURN_180_SECS     = 4.0    # seconds for a 180° in-place turn
TURN_90_SECS      = 4.0    # seconds for a 90° in-place turn
TURN_SPEED        = 0.21   # wheel speed during turns
TURN_LEFT_WHEELS  = (0.1, 0.4)  # raw wheel speeds for a left-command turn
TURN_RIGHT_WHEELS = (0.1, -0.4)  # raw wheel speeds for a right-command turn
ALIGN_FORWARD_SPD = 0.15   # speed during ALIGNING_TO_HALLWAY
ALIGN_WALL_MM     = 800    # right+left dist < this → considered "in hallway"
ALIGN_TIMEOUT_S   = 6.0    # give up aligning after this many seconds
T_FRONT_MM        = 1500   # front dist < this → wall in front at T
T_OPEN_MM         = 900    # right/left dist > this → side open at T
FINAL_MOVE_SECS   = 5.0    # seconds to drive after turning at T
FINAL_SPEED       = 0.15   # speed during final approach


class GreeterController:
    """Orchestrates the full greeting + navigation FSM."""

    def __init__(self, robot, lidar, wall_follower):
        self._robot = robot
        self._lidar = lidar
        self._wall_follower = wall_follower

        self._lock = threading.Lock()
        self._state = 'WAITING'
        self._destination = None   # 'bathroom' or 'lab'
        self._thread = None
        self._running = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def state(self):
        with self._lock:
            return self._state

    @property
    def destination(self):
        with self._lock:
            return self._destination

    def start(self):
        """Start the greeter FSM in a background daemon thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._state = 'WAITING'
            self._destination = None

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("[GREETER] Started — state: WAITING")

    def stop(self):
        """Stop the FSM and halt the robot."""
        with self._lock:
            self._running = False
        self._wall_follower.stop()
        self._robot.stop()
        self._set_state('STOPPED')
        print("[GREETER] Stopped by operator")

    def reset(self):
        """Reset to WAITING so the greeter can serve the next visitor."""
        self._wall_follower.stop()
        self._robot.stop()
        with self._lock:
            self._destination = None
        self._set_state('WAITING')
        print("[GREETER] Reset — state: WAITING")

    def inject_destination(self, destination):
        """
        Keyboard-fallback: inject 'bathroom' or 'lab' while in LISTENING state.
        Called by the /greeter/command Flask route.
        """
        with self._lock:
            if self._state == 'LISTENING':
                self._destination = destination
                print(f"[GREETER] Destination injected: {destination}")
                return True
        return False

    # ------------------------------------------------------------------
    # Main FSM loop
    # ------------------------------------------------------------------

    def _run(self):
        while True:
            with self._lock:
                if not self._running:
                    break
                state = self._state

            # Dispatch to state handler
            if state == 'WAITING':
                self._state_waiting()
            elif state == 'GREETING':
                self._state_greeting()
            elif state == 'LISTENING':
                self._state_listening()
            elif state == 'TURNING_AROUND':
                self._state_turning_around()
            elif state == 'ALIGNING_TO_HALLWAY':
                self._state_aligning()
            elif state == 'MOVING_TO_T':
                self._state_moving_to_t()
            elif state == 'TURNING_TO_DESTINATION':
                self._state_turning_to_dest()
            elif state == 'FINAL_MOVEMENT':
                self._state_final_movement()
            elif state == 'STOPPED':
                time.sleep(0.5)
            else:
                time.sleep(0.2)

        self._robot.stop()
        print("[GREETER] Thread exited")

    # ------------------------------------------------------------------
    # State handlers
    # ------------------------------------------------------------------

    def _state_waiting(self):
        """Poll LIDAR until a human is detected in front."""
        front = self._lidar.front_dist
        if front is not None and front < HUMAN_DETECT_MM:
            print(f"[GREETER] Human detected at {front:.0f}mm")
            self._set_state('GREETING')
        else:
            time.sleep(0.2)

    def _state_greeting(self):
        """Greet the human, then move to LISTENING."""
        self._robot.speak("Hello, how can I help you?")
        time.sleep(1.5)
        self._set_state('LISTENING')

    def _state_listening(self):
        """
        Listen for a spoken destination request.
        Falls back to keyboard injection via inject_destination().
        Retries if speech is not understood.
        """
        try:
            from speech_recognizer import SpeechRecognizer
            sr = SpeechRecognizer()
            print("[GREETER] Listening for destination (say 'bathroom' or 'robot lab')...")
            dest = sr.recognize_destination(timeout_seconds=8)
        except Exception as e:
            print(f"[GREETER] Speech error: {e}")
            dest = None

        # Check if a destination was injected via keyboard while we were listening
        with self._lock:
            injected = self._destination
        if injected:
            dest = injected

        if dest in ('bathroom', 'lab'):
            with self._lock:
                self._destination = dest
            name = "bathroom" if dest == 'bathroom' else "robot lab"
            self._robot.speak(f"Follow me to the {name}.")
            time.sleep(1.5)
            self._set_state('TURNING_AROUND')
        else:
            self._robot.speak("I didn't understand. Please say bathroom or robot lab.")
            time.sleep(1.0)
            # Stay in LISTENING — loop will call us again

    def _state_turning_around(self):
        """Turn 180° in place (turn left)."""
        print("[GREETER] Turning 180°...")
        self._timed_turn('left', TURN_180_SECS)
        self._set_state('ALIGNING_TO_HALLWAY')

    def _state_aligning(self):
        """
        Drive forward slowly until LIDAR detects walls on both sides,
        confirming the robot is centered in the hallway.
        Timeout after ALIGN_TIMEOUT_S and proceed anyway.
        """
        print("[GREETER] Aligning to hallway — driving forward until walls detected...")
        start = time.time()
        while self._is_running():
            right = self._lidar.right_dist
            left  = self._lidar.left_dist
            elapsed = time.time() - start

            both_walls = (
                right is not None and right < ALIGN_WALL_MM and
                left  is not None and left  < ALIGN_WALL_MM
            )
            if both_walls or elapsed > ALIGN_TIMEOUT_S:
                reason = "walls detected" if both_walls else "timeout"
                print(f"[GREETER] Hallway aligned ({reason}) — right={_fmt(right)} left={_fmt(left)}")
                self._robot.stop()
                self._set_state('MOVING_TO_T')
                return

            self._robot.driveForward(speed=ALIGN_FORWARD_SPD)
            time.sleep(0.1)

        self._robot.stop()

    def _state_moving_to_t(self):
        """
        Drive straight to the T-intersection.
        T detected when the front wall is within T_FRONT_MM.
        """
        print("[GREETER] Moving straight to T-intersection...")

        while self._is_running():
            front = self._lidar.front_dist
            if self._is_t_intersection():
                print(f"[GREETER] Front wall detected at T-intersection: {_fmt(front)}")
                self._robot.stop()
                time.sleep(0.3)
                self._set_state('TURNING_TO_DESTINATION')
                return
            self._robot.driveForward(speed=ALIGN_FORWARD_SPD)
            time.sleep(0.1)

        self._robot.stop()

    def _state_turning_to_dest(self):
        """
        Turn 90° toward the destination.
        Bathroom uses the right command because this robot physically turns left
        for that command. Robot Lab uses the left command for the opposite turn.
        """
        dest = self.destination
        if dest == 'bathroom':
            print("[GREETER] Turning RIGHT command toward bathroom...")
            self._timed_turn('right', TURN_90_SECS)
        else:
            print("[GREETER] Turning LEFT command toward robot lab...")
            self._timed_turn('left', TURN_90_SECS)
        self._set_state('FINAL_MOVEMENT')

    def _state_final_movement(self):
        """Drive straight for FINAL_MOVE_SECS seconds to reach destination."""
        dest = self.destination
        name = "bathroom" if dest == 'bathroom' else "robot lab"
        print(f"[GREETER] Final approach to {name} ({FINAL_MOVE_SECS}s)...")

        start = time.time()
        while self._is_running() and (time.time() - start) < FINAL_MOVE_SECS:
            self._robot.driveForward(speed=FINAL_SPEED)
            time.sleep(0.1)

        self._robot.stop()
        time.sleep(0.3)
        self._robot.speak(f"We have arrived at the {name}.")
        print(f"[GREETER] Arrived at {name}.")
        self._set_state('STOPPED')

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_state(self, new_state):
        with self._lock:
            old = self._state
            self._state = new_state
        if old != new_state:
            print(f"[GREETER] {old} → {new_state}")

    def _is_running(self):
        with self._lock:
            return self._running

    def _is_t_intersection(self):
        """
        T-intersection: front wall close enough to make the destination turn.
        """
        front = self._lidar.front_dist

        return front is not None and front < T_FRONT_MM

    def _timed_turn(self, direction, seconds):
        """Turn in place for a fixed duration."""
        steps = int(seconds * 10)
        left_speed, right_speed = (
            TURN_LEFT_WHEELS if direction == 'left' else TURN_RIGHT_WHEELS
        )
        for _ in range(steps):
            if not self._is_running():
                break
            self._robot.setWheelSpeedsRaw(left_speed, right_speed)
            time.sleep(0.1)
        self._robot.stop()
        time.sleep(0.2)


def _fmt(v):
    return f"{v:.0f}mm" if v is not None else "None"
