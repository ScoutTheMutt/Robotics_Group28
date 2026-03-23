"""
LidarMonitor
Continuously reads RPLIDAR scan data in a background thread.
Updates front_blocked and rear_blocked flags used by the safety system.

Detection zones:
  Front: 330-360 degrees OR 0-30 degrees  (60-deg arc at robot nose)
  Rear:  150-210 degrees                  (60-deg arc at robot back)
  Stop distance: 800 mm

The lidar orientation is mounted so that angle 0 points directly forward.
"""

import threading
import time

# --- Zone configuration (degrees) ---
FRONT_MIN1 = 330
FRONT_MAX1 = 360
FRONT_MIN2 = 0
FRONT_MAX2 = 30
REAR_MIN = 150
REAR_MAX = 210
STOP_DISTANCE_MM = 800   # Stop if obstacle closer than this


def _in_front_zone(angle):
    return (FRONT_MIN1 <= angle <= FRONT_MAX1) or (FRONT_MIN2 <= angle <= FRONT_MAX2)


def _in_rear_zone(angle):
    return REAR_MIN <= angle <= REAR_MAX


class LidarMonitor:
    """Thread-safe RPLIDAR monitor that exposes front_blocked / rear_blocked flags."""

    def __init__(self, port='/dev/ttyUSB0'):
        self.port = port
        self._lock = threading.Lock()
        self._front_blocked = False
        self._rear_blocked = False
        self._running = False
        self._thread = None
        self._lidar = None

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

    def start(self):
        """Start the background scanning thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[LIDAR] Monitor started on {self.port}")

    def stop(self):
        """Signal the background thread to stop and disconnect the sensor."""
        self._running = False
        if self._lidar:
            try:
                self._lidar.stop()
                self._lidar.stop_motor()
                self._lidar.disconnect()
            except Exception:
                pass

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
                print("[LIDAR] Connected — scanning...")

                for scan in self._lidar.iter_scans():
                    if not self._running:
                        break

                    new_front = False
                    new_rear = False

                    for (quality, angle, distance) in scan:
                        # Skip low-quality or zero readings
                        if quality == 0 or distance == 0:
                            continue

                        if _in_front_zone(angle) and distance < STOP_DISTANCE_MM:
                            new_front = True

                        if _in_rear_zone(angle) and distance < STOP_DISTANCE_MM:
                            new_rear = True

                    with self._lock:
                        prev_front = self._front_blocked
                        prev_rear = self._rear_blocked
                        self._front_blocked = new_front
                        self._rear_blocked = new_rear

                    # Only print on state change to reduce noise
                    if new_front != prev_front:
                        label = "BLOCKED" if new_front else "CLEAR"
                        print(f"[LIDAR] FRONT -> {label}")
                    if new_rear != prev_rear:
                        label = "BLOCKED" if new_rear else "CLEAR"
                        print(f"[LIDAR] REAR  -> {label}")

            except Exception as e:
                print(f"[LIDAR] Error: {e} — retrying in 2s...")
                with self._lock:
                    self._front_blocked = False
                    self._rear_blocked = False
                if self._lidar:
                    try:
                        self._lidar.disconnect()
                    except Exception:
                        pass
                    self._lidar = None
                time.sleep(2)
