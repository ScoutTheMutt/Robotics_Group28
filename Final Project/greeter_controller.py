"""
GreeterController — Orchestrates the full greeting & navigation sequence.

States:
  IDLE           — waiting for human detection
  GREETING       — human detected, greeting them
  LISTENING      — awaiting destination request
  NAVIGATING     — following wall to destination
  ARRIVED        — at destination, announcing arrival
  COMPLETED      — mission complete (manual reset required)
"""

import threading
import time
from human_detector import HumanDetector
from speech_recognizer import SpeechRecognizer

# Navigation parameters (in mm for distances)
HALLWAY_INTERSECTION_MM = 1500  # distance to intersection from start
DESTINATION_OFFSET_MM   = 1500  # additional distance after turning to destination

class GreeterController:
    """Orchestrates greeter sequence."""

    def __init__(self, robot, lidar, wall_follower):
        """
        Args:
            robot: Robot instance
            lidar: LidarMonitor instance
            wall_follower: WallFollower instance
        """
        self._robot = robot
        self._lidar = lidar
        self._wall_follower = wall_follower
        self._human_detector = HumanDetector(lidar)
        self._speech_recognizer = SpeechRecognizer()

        self._lock = threading.Lock()
        self._state = 'IDLE'
        self._destination = None  # 'bathroom' or 'lab'
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
        """Start the greeter controller in background thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._state = 'IDLE'

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("[GREETER] Controller started")

    def stop(self):
        """Stop the greeter controller."""
        with self._lock:
            self._running = False
            self._state = 'IDLE'
        self._wall_follower.stop()
        self._robot.stop()
        print("[GREETER] Controller stopped")

    def reset(self):
        """Reset to IDLE for next greeting."""
        with self._lock:
            self._state = 'IDLE'
            self._destination = None

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def _run(self):
        while True:
            with self._lock:
                if not self._running:
                    break
                current_state = self._state
                current_dest = self._destination

            self._update(current_state, current_dest)
            time.sleep(0.2)  # 5 Hz update rate

        self._robot.stop()

    def _update(self, state, dest):
        """State machine logic."""
        if state == 'IDLE':
            if self._human_detector.check():
                with self._lock:
                    self._state = 'GREETING'
                print("[GREETER] Human detected!")

        elif state == 'GREETING':
            self._robot.speak("Hello! How can I help you today?")
            with self._lock:
                self._state = 'LISTENING'
            time.sleep(1)

        elif state == 'LISTENING':
            dest = self._speech_recognizer.recognize_destination(timeout_seconds=5)
            if dest:
                with self._lock:
                    self._destination = dest
                    self._state = 'NAVIGATING'
                self._robot.speak("Follow me.")
                time.sleep(1)
            else:
                self._robot.speak("I didn't understand. Please say bathroom or robot lab.")
                with self._lock:
                    self._state = 'LISTENING'

        elif state == 'NAVIGATING':
            self._execute_navigation(dest)

        elif state == 'ARRIVED':
            location_name = "bathroom" if dest == 'bathroom' else "robot lab"
            self._robot.speak(f"We have arrived at the {location_name}.")
            with self._lock:
                self._state = 'COMPLETED'
            time.sleep(2)

        elif state == 'COMPLETED':
            print("[GREETER] Mission complete — awaiting reset")
            time.sleep(1)

    # ------------------------------------------------------------------
    # Navigation substeps
    # ------------------------------------------------------------------

    def _execute_navigation(self, destination):
        """Navigate from start to destination."""
        print(f"[GREETER] Navigating to {destination}")
        
        # Step 1: Turn around (face the hallway)
        self._robot.speak("Let me turn around.")
        self._turn_around()
        time.sleep(1)

        # Step 2: Follow wall to intersection
        print("[GREETER] Following wall to intersection...")
        self._robot.speak("Following the hallway.")
        self._wall_follower.start()
        # Wait for wall follower to bring us to approximate intersection
        time.sleep(10)  # Adjust based on hallway length

        # Step 3: Stop and turn toward destination
        self._wall_follower.stop()
        self._robot.stop()
        time.sleep(0.5)

        if destination == 'bathroom':
            print("[GREETER] Turning left toward bathroom...")
            self._turn_left_90()
        else:
            print("[GREETER] Turning right toward robot lab...")
            self._turn_right_90()
        
        time.sleep(1)

        # Step 4: Drive to destination
        print(f"[GREETER] Driving {DESTINATION_OFFSET_MM}mm to {destination}...")
        self._robot.speak(f"Heading to the {destination}.")
        self._drive_forward_distance(DESTINATION_OFFSET_MM)
        
        with self._lock:
            self._state = 'ARRIVED'

    # ------------------------------------------------------------------
    # Movement primitives
    # ------------------------------------------------------------------

    def _turn_around(self):
        """Execute 180° turn."""
        for _ in range(100):  # ~10 seconds at 10 Hz
            self._robot.turnLeft(speed=0.1)
            time.sleep(0.1)
        self._robot.stop()

    def _turn_left_90(self):
        """Execute 90° left turn."""
        for _ in range(50):
            self._robot.turnLeft(speed=0.1)
            time.sleep(0.1)
        self._robot.stop()

    def _turn_right_90(self):
        """Execute 90° right turn."""
        for _ in range(50):
            self._robot.turnRight(speed=0.1)
            time.sleep(0.1)
        self._robot.stop()

    def _drive_forward_distance(self, distance_mm):
        """
        Drive forward approximately distance_mm.
        Rough estimate: adjust based on calibration.
        """
        # Typical robot: ~1 sec ≈ 300mm at BASE_SPEED
        seconds_needed = distance_mm / 300.0
        steps = int(seconds_needed * 10)  # 10 Hz
        
        for _ in range(steps):
            self._robot.driveForward(speed=0.3)
            time.sleep(0.1)
        self._robot.stop()
