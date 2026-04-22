"""
HumanDetector — Uses LIDAR front zone to detect approaching humans.

A human is detected when the front distance suddenly decreases below
a threshold (indicating approach). Once detected, enters cooldown to
avoid rapid re-triggers.
"""

import threading
import time

DETECTION_THRESHOLD_MM = 1500  # human detected within this range
COOLDOWN_SECONDS = 3.0         # ignore detections for this duration after trigger

class HumanDetector:
    """Detects humans approaching from the front using LIDAR."""

    def __init__(self, lidar):
        """
        Args:
            lidar: LidarMonitor instance
        """
        self._lidar = lidar
        self._lock = threading.Lock()
        self._last_detection_time = 0
        self._detected = False

    @property
    def detected(self):
        """True if human detected and not in cooldown."""
        with self._lock:
            now = time.time()
            if now - self._last_detection_time > COOLDOWN_SECONDS:
                return False
            return self._detected

    def check(self):
        """
        Call periodically to update detection state.
        Returns True if newly detected (first time this frame).
        """
        front = self._lidar.front_dist
        
        with self._lock:
            now = time.time()
            in_cooldown = (now - self._last_detection_time) < COOLDOWN_SECONDS
            
            # Detect if front is close and not in cooldown
            if front is not None and front < DETECTION_THRESHOLD_MM and not in_cooldown:
                if not self._detected:
                    self._detected = True
                    self._last_detection_time = now
                    return True  # newly detected
            
            return False
