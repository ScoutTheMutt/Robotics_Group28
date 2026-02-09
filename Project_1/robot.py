"""
Robot Class
Main robot controller that owns all hardware components
This is the ONLY class that talks to hardware
"""

from maestro import Controller
from motor import Motor
from servo import Servo
from head import Head
from speaker import Speaker

class Robot:
    def __init__(self):
        """Initialize robot with all components"""
        
        # Initialize Maestro controller
        self.maestro = Controller()
        
        # Initialize drive motors
        # Servo 0 = Forward/Backward (Left wheel)
        # Servo 1 = Left/Right (Right wheel)
        self.left_motor = Motor(self.maestro, channel=0)
        self.right_motor = Motor(self.maestro, channel=1)
        
        # Initialize waist rotation
        # Servo 2 = Body turn left/right
        self.waist = Servo(self.maestro, channel=2)
        
        # Initialize head
        # Servo 3 = Head up/down (tilt)
        # Servo 4 = Head left/right (pan)
        self.head = Head(
            tilt_servo=Servo(self.maestro, channel=3),
            pan_servo=Servo(self.maestro, channel=4)
        )
        
        # Initialize speaker
        self.speaker = Speaker()
        
        # Set initial safe state
        self.stop()
        
    def driveForward(self, speed=0.5):
        """
        Drive robot forward
        
        Args:
            speed: Speed 0.0 to 1.0
        """
        speed = max(0.0, min(1.0, speed))
        self.left_motor.setSpeed(speed)
        self.right_motor.setSpeed(speed)
        
    def driveBackward(self, speed=0.5):
        """
        Drive robot backward
        
        Args:
            speed: Speed 0.0 to 1.0
        """
        speed = max(0.0, min(1.0, speed))
        self.left_motor.setSpeed(-speed)
        self.right_motor.setSpeed(-speed)
        
    def turnLeft(self, speed=0.3):
        """
        Turn robot left (differential drive)
        
        Args:
            speed: Turn speed 0.0 to 1.0
        """
        speed = max(0.0, min(1.0, speed))
        self.left_motor.setSpeed(-speed)
        self.right_motor.setSpeed(speed)
        
    def turnRight(self, speed=0.3):
        """
        Turn robot right (differential drive)
        
        Args:
            speed: Turn speed 0.0 to 1.0
        """
        speed = max(0.0, min(1.0, speed))
        self.left_motor.setSpeed(speed)
        self.right_motor.setSpeed(-speed)
        
    def setWheelSpeeds(self, left_speed, right_speed):
        """
        Set individual wheel speeds for precise control
        
        Args:
            left_speed: Left wheel speed -1.0 to 1.0
            right_speed: Right wheel speed -1.0 to 1.0
        """
        self.left_motor.setSpeed(left_speed)
        self.right_motor.setSpeed(right_speed)
        
    def stop(self):
        """EMERGENCY STOP - halt all motion"""
        self.left_motor.stop()
        self.right_motor.stop()
        
    def setHeadPan(self, angle):
        """
        Set head pan angle
        
        Args:
            angle: Angle in degrees -90 to 90
        """
        self.head.setPan(angle)
        
    def setHeadTilt(self, angle):
        """
        Set head tilt angle
        
        Args:
            angle: Angle in degrees -90 to 90
        """
        self.head.setTilt(angle)
        
    def setWaistRotation(self, angle):
        """
        Set waist rotation angle
        
        Args:
            angle: Angle in degrees -90 to 90
        """
        self.waist.setAngle(angle)
        
    def speak(self, text):
        """
        Speak text (non-blocking)
        
        Args:
            text: Text to speak
        """
        self.speaker.say(text)
        
    def centerAll(self):
        """Return all servos to center position and stop motors"""
        self.stop()
        self.head.center()
        self.waist.center()
