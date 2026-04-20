"""
Servo Component Class
Wraps Maestro servo control with safe limits and clear interface
"""

class Servo:
    def __init__(self, maestro, channel, min_position=4000, max_position=8000, default_position=6000):
        """
        Initialize a servo controller
        
        Args:
            maestro: Maestro controller instance
            channel: Servo channel number (0-16)
            min_position: Minimum safe position (quarter-microseconds)
            max_position: Maximum safe position (quarter-microseconds)
            default_position: Neutral/center position
        """
        self.maestro = maestro
        self.channel = channel
        self.min_position = min_position
        self.max_position = max_position
        self.default_position = default_position
        self.current_position = default_position
        
    def setPosition(self, position):
        """
        Set servo to specific position with safety limits
        
        Args:
            position: Target position in quarter-microseconds
        """
        # Enforce safety limits
        safe_position = max(self.min_position, min(self.max_position, position))
        
        self.maestro.setTarget(self.channel, safe_position)
        self.current_position = safe_position
        
    def setAngle(self, angle):
        """
        Set servo position by angle (-90 to 90 degrees)
        Maps angle to position range
        
        Args:
            angle: Angle in degrees (-90 to 90)
        """
        # Clamp angle
        angle = max(-90, min(90, angle))
        
        # Map angle to position range
        position_range = self.max_position - self.min_position
        position = self.default_position + int((angle / 90.0) * (position_range / 2))
        
        self.setPosition(position)
        
    def center(self):
        """Move servo to center/neutral position"""
        self.setPosition(self.default_position)
        
    def getPosition(self):
        """Return current position"""
        return self.current_position
