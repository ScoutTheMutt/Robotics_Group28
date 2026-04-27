"""
WallFollower — Autonomous right-wall following controller.

Uses LidarMonitor zone distances to implement closed-loop wall following.

States:
  FORWARD        — wall in target range, driving straight
  STEER_AWAY     — wall too close, curving left
  STEER_TOWARD   — wall too far, curving right
  OBSTACLE_AVOID — front blocked, turning left in place until clear
  SEARCH         — wall lost, turning right gently to find it
  STOPPED        — not running

Tunable constants at the top of the file — adjust after testing.
"""

import threading
import time

# ---------------------------------------------------------------------------
# Tunable parameters — adjust these during testing
# ---------------------------------------------------------------------------

WALL_TARGET_MM   = 800   # desired distance from the right wall (mm)
WALL_LOWER_MM    = 600   # too close — steer away below this
WALL_UPPER_MM    = 1000   # too far  — steer toward above this
WALL_LOST_MM     = 2001  # wall considered lost beyond this distance

FRONT_STOP_MM    = 450   # stop forward motion if front closer than this

BASE_SPEED       = 0.16  # nominal forward speed (0.0 – 1.0) — reduced to 40%
STEER_ADJUST     = 0.08  # differential applied to each wheel for gentle steering
TURN_SPEED       = 0.06  # speed when turning in place — reduced to 40%

LOOP_HZ          = 10    # control loop rate


class WallFollower:
    """Closed-loop right-wall follower driven by LIDAR zone distances."""

    def __init__(self, robot, lidar):
        """
        Args:
            robot: Robot instance (from robot.py)
            lidar: LidarMonitor instance (from lidar.py) — must expose
                   front_dist, right_dist, front_right_dist properties
        """
        self._robot = robot
        self._lidar = lidar
        self._running = False
        self._thread = None
        self._state = 'STOPPED'
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def state(self):
        with self._lock:
            return self._state

    def start(self):
        """Start the wall-following loop in a background thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._state = 'FORWARD'

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print("[WALL] Wall follower started")

    def stop(self):
        """Stop the wall follower and halt the robot."""
        with self._lock:
            self._running = False
            self._state = 'STOPPED'
        self._robot.stop()
        print("[WALL] Wall follower stopped")

    # ------------------------------------------------------------------
    # Control loop
    # ------------------------------------------------------------------

    def _loop(self):
        interval = 1.0 / LOOP_HZ

        while True:
            with self._lock:
                if not self._running:
                    break

            front = self._lidar.front_dist
            right = self._lidar.right_dist
            fr    = self._lidar.front_right_dist
            helper = self._lidar.rear_dist

            new_state = self._decide(front, right, fr)

            with self._lock:
                old_state = self._state
                self._state = new_state

            if new_state != old_state:
                print(f"[WALL] {old_state} -> {new_state}  "
                      f"front={_fmt(front)}  right={_fmt(right)}  fr={_fmt(fr)}")

            self._execute(new_state)
            time.sleep(interval)

        self._robot.stop()

    # ------------------------------------------------------------------
    # Decision logic
    # ------------------------------------------------------------------

    def _decide(self, front, right, fr):
        # Case 1: obstacle in front — highest priority
        if front is not None and front < FRONT_STOP_MM:
            return 'OBSTACLE_AVOID'

        # Case 4: wall lost
        if right is None or right > WALL_LOST_MM:
            return 'SEARCH'

        # Case 2: too close
        if right < WALL_LOWER_MM or fr < WALL_TARGET_MM or fr < WALL_LOWER_MM:
            return 'STEER_AWAY'

        # Case 3: too far
        if right > WALL_UPPER_MM and fr > WALL_UPPER_MM:
            return 'STEER_TOWARD'

        return 'FORWARD'

    # ------------------------------------------------------------------
    # Motor commands
    # ------------------------------------------------------------------

    def _execute(self, state):
        if state == 'FORWARD':
            # Both wheels forward - left needs higher speed for calibration
            self._robot.setWheelSpeedsRaw(.14, 0.12)

        elif state == 'STEER_AWAY':
            # Curve left (away from wall): left slower, right faster
            left_speed = BASE_SPEED + STEER_ADJUST  # 0.16 - 0.08 = 0.08
            right_speed = BASE_SPEED - STEER_ADJUST  # 0.16 + 0.08 = 0.24
            time.sleep(1)            
            self._robot.setWheelSpeedsRaw(0.18,-.29)

        elif state == 'STEER_TOWARD':
            # Curve right (toward wall): left faster, right slower
            left_speed = BASE_SPEED + STEER_ADJUST  # 0.16 + 0.08 = 0.24
            right_speed = BASE_SPEED - STEER_ADJUST  # 0.16 - 0.08 = 0.08
            time.sleep(1)            
            self._robot.setWheelSpeedsRaw(0.18,.22)
        elif state == 'OBSTACLE_AVOID':
            # Turn left in place until front clears
            self._robot.stop()
        elif state == 'SEARCH':
            # Arc right to find the wall: left faster, right slower
            time.sleep(1)
            self._robot.setWheelSpeedsRaw(0.18, .4)

        # STOPPED — no motor command; robot.stop() was already called


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _fmt(dist):
    return f"{dist:.0f}mm" if dist is not None else "None"
