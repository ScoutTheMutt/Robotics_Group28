"""
Head Component Class
Controls head tilt and pan servos
"""

class Head:
    def __init__(self, tilt_servo, pan_servo):
        """
        Initialize head controller
        
        Args:
            tilt_servo: Servo object for tilt (up/down)
            pan_servo: Servo object for pan (left/right)
        """
        self.tilt = tilt_servo
        self.pan = pan_servo
        
    def setPan(self, angle):
        """
        Set head pan position
        
        Args:
            angle: Angle in degrees (-90 to 90)
        """
        self.pan.setAngle(angle)
        
    def setTilt(self, angle):
        """
        Set head tilt position
        
        Args:
            angle: Angle in degrees (-90 to 90)
        """
        self.tilt.setAngle(angle)
        
    def lookLeft(self):
        """Turn head left"""
        self.pan.setAngle(-45)
        
    def lookRight(self):
        """Turn head right"""
        self.pan.setAngle(45)
        
    def lookUp(self):
        """Tilt head up"""
        self.tilt.setAngle(30)
        
    def lookDown(self):
        """Tilt head down"""
        self.tilt.setAngle(-30)
        
    def center(self):
        """Return head to center position"""
        self.pan.center()
        self.tilt.center()
