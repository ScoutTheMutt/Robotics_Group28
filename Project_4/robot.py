"""
Robot Class — Project 3
Extends Project 2 with LIDAR-based safety stops.
setWheelSpeeds() checks front_blocked / rear_blocked before moving.
Flask NEVER touches hardware directly — only calls Robot methods.
"""

from maestro import Controller
from motor import Motor
from servo import Servo
from head import Head
from speaker import Speaker

# Minimum average speed to trigger a directional safety check.
# Keeps pure turns (left<0, right>0 or vice versa) from being blocked.
_SPEED_THRESHOLD = 0.05


class Robot:
    def __init__(self):
        """Initialize robot with all components."""

        self.maestro = Controller()

        # Drive motors: ch0 = left, ch1 = right
        self.left_motor = Motor(self.maestro, channel=0)
        self.right_motor = Motor(self.maestro, channel=1)

        # Waist rotation (hardware center is -35°)
        waist_center = 6000 - int((35.0 / 90.0) * 2000)
        self.waist = Servo(self.maestro, channel=2, default_position=waist_center)

        # Head: ch3 = tilt, ch4 = pan
        self.head = Head(
            tilt_servo=Servo(self.maestro, channel=3),
            pan_servo=Servo(self.maestro, channel=4)
        )

        # Arm servos
        self.arm = Servo(self.maestro, channel=11)
        self.elbow = Servo(self.maestro, channel=13)
        self.wristRotation = Servo(self.maestro, channel=15)

        self.speaker = Speaker()

        # Lidar monitor — attached after construction via set_lidar()
        self._lidar = None

        self.stop()

    # ------------------------------------------------------------------
    # Lidar integration
    # ------------------------------------------------------------------

    def set_lidar(self, lidar_monitor):
        """Attach a LidarMonitor so setWheelSpeeds can enforce safety stops."""
        self._lidar = lidar_monitor

    # ------------------------------------------------------------------
    # Motion — all wheel commands funnel through setWheelSpeeds
    # ------------------------------------------------------------------

    def setWheelSpeeds(self, left_speed, right_speed):
        """
        Set individual wheel speeds with LIDAR safety enforcement.

        Forward intent  (avg > threshold): blocked when front_blocked is True.
        Backward intent (avg < -threshold): blocked when rear_blocked is True.
        Pure turns (opposite signs): always allowed.

        Args:
            left_speed:  -1.0 to 1.0
            right_speed: -1.0 to 1.0
        """
        if self._lidar is not None:
            avg = (left_speed + right_speed) / 2.0

            if avg > _SPEED_THRESHOLD:
                # Forward intent — check front blocked flag
                if self._lidar.front_blocked:
                    print("[SAFETY] FRONT LOCKED — forward command ignored")
                    self.stop()
                    return

            elif avg < -_SPEED_THRESHOLD:
                # Backward intent — check rear blocked flag
                if self._lidar.rear_blocked:
                    print("[SAFETY] REAR LOCKED — backward command ignored")
                    self.stop()
                    return

        self.left_motor.setSpeed(left_speed)
        self.right_motor.setSpeed(right_speed)

    def setWheelSpeedsRaw(self, left_speed, right_speed):
        """Set wheel speeds without any safety checks (for testing)."""
        self.left_motor.setSpeed(left_speed)
        self.right_motor.setSpeed(right_speed)

    def driveForward(self, speed=0.45):
        speed = max(0.0, min(0.75, speed))
        self.setWheelSpeedsRaw(speed, speed)

    def driveBackward(self, speed=0.15):
        speed = max(0.0, min(0.75, speed))
        self.setWheelSpeeds(-speed, -speed)

    def turnLeft(self, speed=0.05):
        speed = max(0.0, min(0.75, speed))
        self.setWheelSpeeds(-speed, speed)

    def turnRight(self, speed=0.05):
        speed = max(0.0, min(0.75, speed))
        self.setWheelSpeeds(speed, -speed)

    def stop(self):
        """EMERGENCY STOP — halt all wheel motion."""
        self.left_motor.stop()
        self.right_motor.stop()

    # ------------------------------------------------------------------
    # Head / body / speech
    # ------------------------------------------------------------------

    def setHeadPan(self, angle):
        self.head.setPan(angle)

    def setHeadTilt(self, angle):
        self.head.setTilt(angle)

    def setWaistRotation(self, angle):
        self.waist.setAngle(angle)

    def setArmAngle(self, angle):
        self.arm.setAngle(angle)

    def setElbowAngle(self, angle):
        self.elbow.setAngle(angle)

    def setWristRotation(self, angle):
        self.wristRotation.setAngle(angle)

    def speak(self, text):
        self.speaker.say(text)

    def centerAll(self):
        self.stop()
        self.head.center()
        self.waist.center()
