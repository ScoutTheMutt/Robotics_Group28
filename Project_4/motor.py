"""
Motor Component Class
Controls drive motors through servo channels
"""

class Motor:
    def __init__(self, maestro, channel, stop_position=6000, min_position=4000, max_position=8000):
        """
        Initialize a motor controller
        
        Args:
            maestro: Maestro controller instance
            channel: Servo channel for this motor
            stop_position: Position that stops the motor
            min_position: Full reverse position
            max_position: Full forward position
        """
        self.maestro = maestro
        self.channel = channel
        self.stop_position = stop_position
        self.min_position = min_position
        self.max_position = max_position
        self.current_speed = 0
        
    def setSpeed(self, speed):
        """
        Set motor speed
        
        Args:
            speed: Speed from -1.0 (full reverse) to 1.0 (full forward)
        """
        # Clamp speed
        speed = max(-1.0, min(1.0, speed))
        
        # Map speed to position
        if speed >= 0:
            # Forward
            position = int(self.stop_position + speed * (self.max_position - self.stop_position))
        else:
            # Reverse
            position = int(self.stop_position + speed * (self.stop_position - self.min_position))
            
        self.maestro.setTarget(self.channel, position)
        self.current_speed = speed
        
    def stop(self):
        """Stop the motor"""
        self.setSpeed(0)
        
    def getSpeed(self):
        """Return current speed"""
        return self.current_speed
