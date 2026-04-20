"""
LidarMonitor
Continuously reads RPLIDAR scan data in a background thread.
Updates front_blocked and rear_blocked flags used by the safety system,
and exposes per-zone minimum distances for the wall follower.

Safety zones (used for blocked flags):
  Front: 330-360 OR 0-20 degrees  (50-deg arc at robot nose)
  Rear:  150-210 degrees          (60-deg arc at robot back)
  Stop distance: 800 mm

Wall-follower zones (right-wall mode, 0° = physical front):
  front:       340-360 OR 0-20 degrees
  front-right: 290-340 degrees
  right:       250-290 degrees

The lidar orientation is mounted so that angle 0 points directly forward.
"""

import threading
import time

# --- Safety zone configuration (degrees) ---
FRONT_MIN1 = 330
FRONT_MAX1 = 360
FRONT_MIN2 = 0
FRONT_MAX2 = 20
REAR_MIN = 150
REAR_MAX = 210
STOP_DISTANCE_MM = 800  # Stop if obstacle closer than this

# --- Wall-follower zone configuration (degrees) ---
WF_FRONT_MIN1    = 320
WF_FRONT_MAX1    = 360
WF_FRONT_MIN2    = 0
WF_FRONT_MAX2    = 20
WF_FRONT_RIGHT_MIN = 290
WF_FRONT_RIGHT_MAX = 340
WF_RIGHT_MIN       = 220
WF_RIGHT_MAX       = 310
WF_REAR_RIGHT_MIN  = 200
WF_REAR_RIGHT_MAX  = 250
MAX_VALID_DIST_MM = 6000  # discard spurious long-range readings


def _in_front_zone(angle):
    return (FRONT_MIN1 <= angle <= FRONT_MAX1) or (FRONT_MIN2 <= angle <= FRONT_MAX2)


def _in_rear_zone(angle):
    return REAR_MIN <= angle <= REAR_MAX


def _in_wf_front_zone(angle):
    return (WF_FRONT_MIN1 <= angle <= WF_FRONT_MAX1) or (WF_FRONT_MIN2 <= angle <= WF_FRONT_MAX2)


def _in_wf_front_right_zone(angle):
    return WF_FRONT_RIGHT_MIN <= angle <= WF_FRONT_RIGHT_MAX


def _in_wf_right_zone(angle):
    return WF_RIGHT_MIN <= angle <= WF_RIGHT_MAX

def _in_wf_rear_right_zone(angle):
    return WF_REAR_RIGHT_MIN <= angle <= WF_REAR_RIGHT_MAX


class LidarMonitor:
    """Thread-safe RPLIDAR monitor that exposes front_blocked / rear_blocked flags.

    Safety locks:
      front_lock — held by LiDAR thread when front is blocked; released when clear.
      rear_lock  — held by LiDAR thread when rear is blocked; released when clear.
    Motor code tries acquire(blocking=False): if it fails, the direction is blocked.
    """

    def __init__(self, port='/dev/ttyUSB0'):
        self.port = port
        self._lock = threading.Lock()        # protects all shared state
        self._front_blocked = False
        self._rear_blocked = False
        self._running = False
        self._thread = None
        self._lidar = None

        # Safety locks — held by LiDAR thread when direction is blocked
        self.front_lock = threading.Lock()
        self.rear_lock = threading.Lock()
        self._front_lock_held = False
        self._rear_lock_held = False

        # Wall-follower zone distances (min mm in zone, or None if no reading)
        self._front_dist = None
        self._right_dist = None
        self._front_right_dist = None
        self._rear_right_dist = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def front_blocked(self):
        with self._lock:
            return self._front_blocked

    @property
    def rear_blocked(self):
        with self._lock:
            return self._rear_blocked

    @property
    def front_dist(self):
        """Minimum distance (mm) in front zone, or None if no valid reading."""
        with self._lock:
            return self._front_dist

    @property
    def right_dist(self):
        """Minimum distance (mm) in right zone (250-290°), or None if no valid reading."""
        with self._lock:
            return self._right_dist

    @property
    def front_right_dist(self):
        """Minimum distance (mm) in front-right zone (290-340°), or None if no valid reading."""
        with self._lock:
            return self._front_right_dist

    @property
    def rear_right_dist(self):
        """Minimum distance (mm) in rear-right zone (200-250°), or None if no valid reading."""
        with self._lock:
            return self._rear_right_dist

    def start(self):
        """Start the background scanning thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[LIDAR] Monitor started on {self.port}")

    def stop(self):
        """Signal the background thread to stop and disconnect the sensor."""
        self._running = False
        self._release_safety_locks()
        if self._lidar:
            try:
                self._lidar.stop()
                self._lidar.stop_motor()
                self._lidar.disconnect()
            except Exception:
                pass

    def _release_safety_locks(self):
        """Release any held safety locks so motors are not left permanently blocked."""
        if self._front_lock_held:
            self.front_lock.release()
            self._front_lock_held = False
        if self._rear_lock_held:
            self.rear_lock.release()
            self._rear_lock_held = False

    # ------------------------------------------------------------------
    # Background thread
    # ------------------------------------------------------------------

    def _run(self):
        """Connect to the RPLIDAR and scan continuously, updating flags."""
        try:
            from rplidar import RPLidar
        except ImportError:
            print("[LIDAR] ERROR: rplidar library not installed.")
            print("[LIDAR]   Run: pip install rplidar-roboticia")
            return

        while self._running:
            try:
                self._lidar = RPLidar(self.port)
                time.sleep(1)                    # 2. Wait 1 second for reset to complete
                print("[LIDAR] Connected — scanning...")

                for scan in self._lidar.iter_scans():
                    if not self._running:
                        break

                    new_front = False
                    new_rear = False
                    wf_front_readings = []
                    wf_right_readings = []
                    wf_fr_readings = []
                    wf_rr_readings = []

                    for (quality, angle, distance) in scan:
                        # Skip low-quality, zero, or out-of-range readings
                        if quality == 0 or distance == 0 or distance > MAX_VALID_DIST_MM:
                            continue

                        # Lidar is mounted flipped — mirror+rotate to match physical frame
                        angle = (180 - angle) % 360

                        if _in_front_zone(angle) and distance < STOP_DISTANCE_MM:
                            new_front = True

                        if _in_rear_zone(angle) and distance < STOP_DISTANCE_MM:
                            new_rear = True

                        # Wall-follower zone accumulation
                        if _in_wf_front_zone(angle):
                            wf_front_readings.append(distance)
                        if _in_wf_front_right_zone(angle):
                            wf_fr_readings.append(distance)
                        if _in_wf_right_zone(angle):
                            wf_right_readings.append(distance)
                        if _in_wf_rear_right_zone(angle):
                            wf_rr_readings.append(distance)

                    # --- Update wall-follower zone distances ---
                    new_front_dist = min(wf_front_readings) if wf_front_readings else None
                    new_right_dist = min(wf_right_readings) if wf_right_readings else None
                    new_fr_dist    = min(wf_fr_readings)    if wf_fr_readings    else None
                    new_rr_dist    = min(wf_rr_readings)    if wf_rr_readings    else None

                    # --- Update front safety lock ---
                    if new_front and not self._front_lock_held:
                        self.front_lock.acquire()
                        self._front_lock_held = True
                    elif not new_front and self._front_lock_held:
                        self.front_lock.release()
                        self._front_lock_held = False

                    # --- Update rear safety lock ---
                    if new_rear and not self._rear_lock_held:
                        self.rear_lock.acquire()
                        self._rear_lock_held = True
                    elif not new_rear and self._rear_lock_held:
                        self.rear_lock.release()
                        self._rear_lock_held = False

                    # --- Update boolean flags and zone distances ---
                    with self._lock:
                        prev_front = self._front_blocked
                        prev_rear = self._rear_blocked
                        self._front_blocked = new_front
                        self._rear_blocked = new_rear
                        self._front_dist = new_front_dist
                        self._right_dist = new_right_dist
                        self._front_right_dist = new_fr_dist
                        self._rear_right_dist = new_rr_dist

                    # Only print on state change to reduce noise
                    if new_front != prev_front:
                        label = "BLOCKED" if new_front else "CLEAR"
                        print(f"[LIDAR] FRONT -> {label}")
                    if new_rear != prev_rear:
                        label = "BLOCKED" if new_rear else "CLEAR"
                        print(f"[LIDAR] REAR  -> {label}")

            except Exception as e:
                print(f"[LIDAR] Error: {e} — retrying in 2s...")
                self._release_safety_locks()
                with self._lock:
                    self._front_blocked = False
                    self._rear_blocked = False
                    self._front_dist = None
                    self._right_dist = None
                    self._front_right_dist = None
                    self._rear_right_dist = None
                if self._lidar:
                    try:
                        self._lidar.stop()        # ← stop scanning
                        self._lidar.stop_motor()  # ← stop the motor
                        time.sleep(1)             # ← let it spin down before disconnect
                        self._lidar.disconnect()
                    except Exception:
                        pass
                    self._lidar = None
                    time.sleep(2)