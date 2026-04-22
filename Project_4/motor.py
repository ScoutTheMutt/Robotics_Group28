"""
Motor Component Class
Controls drive motors through servo channels
"""

class Motor:
    def __init__(self, maestro, channel, stop_position=6000, min_position=4000, max_position=8000, speed_multiplier=1.0):
        """
        Initialize a motor controller

        Args:
            maestro: Maestro controller instance
            channel: Servo channel for this motor
            stop_position: Position that stops the motor
            min_position: Full reverse position
            max_position: Full forward position
            speed_multiplier: Multiplier for speed compensation (default 1.0)
        """
        self.maestro = maestro
        self.channel = channel
        self.stop_position = stop_position
        self.min_position = min_position
        self.max_position = max_position
        self.speed_multiplier = speed_multiplier
        self.current_speed = 0
        
    def setSpeed(self, speed):
        """
        Set motor speed

        Args:
            speed: Speed from -1.0 (full reverse) to 1.0 (full forward)
        """
        # Store original speed before multiplier
        self.current_speed = speed

        # Apply speed multiplier for motor compensation
        speed = speed * self.speed_multiplier

        # Clamp speed after multiplication
        speed = max(-1.0, min(1.0, speed))

        # Map speed to position
        if speed >= 0:
            # Forward
            position = int(self.stop_position + speed * (self.max_position - self.stop_position))
        else:
            # Reverse
            position = int(self.stop_position + speed * (self.stop_position - self.min_position))

        print(f"[MOTOR-DEBUG] Channel {self.channel}: speed={self.current_speed:.2f} x{self.speed_multiplier} = {speed:.2f} → position={position}")
        self.maestro.setTarget(self.channel, position)
        
    def stop(self):
        """Stop the motor"""
        self.setSpeed(0)
        
    def getSpeed(self):
        """Return current speed"""
        return self.current_speed
