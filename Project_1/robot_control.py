"""
Example Robot Control Layer
This is a template showing how to structure your robot control code.
Replace the placeholder functions with actual hardware control.
"""

class RobotController:
    """
    Robot control layer that interfaces with hardware.
    Independent of Flask - can be used standalone or from web server.
    """
    
    def __init__(self):
        """Initialize robot hardware connections"""
        # TODO: Initialize your Maestro controller or other hardware
        # Example:
        # from maestro import Controller
        # self.maestro = Controller('/dev/ttyACM0')
        
        # Define servo channels (adjust for your setup)
        self.CHANNELS = {
            'left_wheel': 0,
            'right_wheel': 1,
            'head_tilt': 2,
            'head_pan': 3,
            'waist': 4,
            'left_arm': 5,
            'right_arm': 6
        }
        
        # Define safe limits for each servo (in microseconds or degrees)
        self.LIMITS = {
            'wheel_speed': (-100, 100),
            'head_tilt': (4000, 8000),    # Example servo pulse widths
            'head_pan': (4000, 8000),
            'waist': (4000, 8000)
        }
        
        # Current positions for safety checking
        self.current_state = {
            'left_wheel': 0,
            'right_wheel': 0,
            'head_tilt': 6000,  # neutral
            'head_pan': 6000,   # neutral
            'waist': 6000       # neutral
        }
        
        print("Robot Controller initialized")
        self.stop_all()
    
    def _clamp(self, value, min_val, max_val):
        """Ensure value is within safe limits"""
        return max(min_val, min(max_val, value))
    
    def _degrees_to_pulse(self, degrees):
        """
        Convert degrees (0-180) to servo pulse width (microseconds)
        Standard servo: 0° = 4000μs, 90° = 6000μs, 180° = 8000μs
        Adjust this formula for your specific servos
        """
        pulse = 4000 + (degrees / 180.0) * 4000
        return int(pulse)
    
    def _speed_to_pulse(self, speed):
        """
        Convert speed percentage (-100 to 100) to continuous rotation servo pulse
        Adjust for your motor controller
        """
        # Example: continuous rotation servo
        # -100 = full reverse (4000), 0 = stop (6000), 100 = full forward (8000)
        pulse = 6000 + (speed / 100.0) * 2000
        return int(pulse)
    
    # ==================== DRIVE CONTROL ====================
    
    def set_wheel_speeds(self, left_speed, right_speed):
        """
        Set left and right wheel speeds
        Args:
            left_speed: -100 (full reverse) to 100 (full forward)
            right_speed: -100 (full reverse) to 100 (full forward)
        """
        # Clamp to safe limits
        left_speed = self._clamp(left_speed, 
                                 self.LIMITS['wheel_speed'][0],
                                 self.LIMITS['wheel_speed'][1])
        right_speed = self._clamp(right_speed,
                                  self.LIMITS['wheel_speed'][0],
                                  self.LIMITS['wheel_speed'][1])
        
        # Update state
        self.current_state['left_wheel'] = left_speed
        self.current_state['right_wheel'] = right_speed
        
        # TODO: Send commands to actual hardware
        # Example with Maestro:
        # left_pulse = self._speed_to_pulse(left_speed)
        # right_pulse = self._speed_to_pulse(right_speed)
        # self.maestro.setTarget(self.CHANNELS['left_wheel'], left_pulse)
        # self.maestro.setTarget(self.CHANNELS['right_wheel'], right_pulse)
        
        print(f"Wheels: L={left_speed:.1f}%, R={right_speed:.1f}%")
    
    def drive_forward(self, speed=50):
        """Drive forward at specified speed"""
        self.set_wheel_speeds(speed, speed)
    
    def drive_backward(self, speed=50):
        """Drive backward at specified speed"""
        self.set_wheel_speeds(-speed, -speed)
    
    def turn_left(self, speed=50):
        """Turn left by rotating wheels in opposite directions"""
        self.set_wheel_speeds(-speed, speed)
    
    def turn_right(self, speed=50):
        """Turn right by rotating wheels in opposite directions"""
        self.set_wheel_speeds(speed, -speed)
    
    # ==================== HEAD CONTROL ====================
    
    def set_head_tilt(self, angle):
        """
        Set head tilt angle
        Args:
            angle: 0 (down) to 180 (up) degrees
        """
        # Clamp to safe limits
        angle = self._clamp(angle, 0, 180)
        
        # Update state
        self.current_state['head_tilt'] = angle
        
        # TODO: Send to hardware
        # pulse = self._degrees_to_pulse(angle)
        # pulse = self._clamp(pulse, self.LIMITS['head_tilt'][0], self.LIMITS['head_tilt'][1])
        # self.maestro.setTarget(self.CHANNELS['head_tilt'], pulse)
        
        print(f"Head tilt: {angle}°")
    
    def set_head_pan(self, angle):
        """
        Set head pan angle
        Args:
            angle: 0 (left) to 180 (right) degrees
        """
        # Clamp to safe limits
        angle = self._clamp(angle, 0, 180)
        
        # Update state
        self.current_state['head_pan'] = angle
        
        # TODO: Send to hardware
        # pulse = self._degrees_to_pulse(angle)
        # pulse = self._clamp(pulse, self.LIMITS['head_pan'][0], self.LIMITS['head_pan'][1])
        # self.maestro.setTarget(self.CHANNELS['head_pan'], pulse)
        
        print(f"Head pan: {angle}°")
    
    def center_head(self):
        """Center the head (tilt and pan at 90°)"""
        self.set_head_tilt(90)
        self.set_head_pan(90)
    
    # ==================== WAIST CONTROL ====================
    
    def set_waist_rotation(self, angle):
        """
        Set waist rotation angle
        Args:
            angle: 0 to 180 degrees
        """
        # Clamp to safe limits
        angle = self._clamp(angle, 0, 180)
        
        # Update state
        self.current_state['waist'] = angle
        
        # TODO: Send to hardware
        # pulse = self._degrees_to_pulse(angle)
        # pulse = self._clamp(pulse, self.LIMITS['waist'][0], self.LIMITS['waist'][1])
        # self.maestro.setTarget(self.CHANNELS['waist'], pulse)
        
        print(f"Waist rotation: {angle}°")
    
    # ==================== VOICE OUTPUT ====================
    
    def speak(self, text):
        """
        Text-to-speech output
        Args:
            text: String to speak
        """
        # TODO: Implement TTS
        # Options:
        # 1. Use pyttsx3 (offline)
        # 2. Use espeak (Linux)
        # 3. Use Google TTS API
        # 4. Use festival
        
        # Example with espeak:
        # import os
        # os.system(f'espeak "{text}"')
        
        # Example with pyttsx3:
        # import pyttsx3
        # engine = pyttsx3.init()
        # engine.say(text)
        # engine.runAndWait()
        
        print(f"Speaking: '{text}'")
    
    # ==================== SAFETY & CONTROL ====================
    
    def stop_all(self):
        """Emergency stop - set all motors to neutral/stopped state"""
        print("EMERGENCY STOP ACTIVATED")
        
        # Stop wheels
        self.set_wheel_speeds(0, 0)
        
        # Optionally center head and waist
        # self.center_head()
        # self.set_waist_rotation(90)
        
        print("All motors stopped")
    
    def get_state(self):
        """Return current robot state"""
        return self.current_state.copy()
    
    def test_all_components(self):
        """
        Test all robot components sequentially
        Use this for hardware verification (Step A)
        """
        print("\n" + "="*50)
        print("ROBOT COMPONENT TEST")
        print("="*50)
        
        import time
        
        # Test wheels
        print("\n1. Testing wheels...")
        print("   Forward...")
        self.drive_forward(30)
        time.sleep(2)
        print("   Backward...")
        self.drive_backward(30)
        time.sleep(2)
        print("   Turn left...")
        self.turn_left(30)
        time.sleep(2)
        print("   Turn right...")
        self.turn_right(30)
        time.sleep(2)
        self.stop_all()
        time.sleep(1)
        
        # Test head tilt
        print("\n2. Testing head tilt...")
        for angle in [0, 90, 180, 90]:
            self.set_head_tilt(angle)
            time.sleep(1)
        
        # Test head pan
        print("\n3. Testing head pan...")
        for angle in [0, 90, 180, 90]:
            self.set_head_pan(angle)
            time.sleep(1)
        
        # Test waist
        print("\n4. Testing waist rotation...")
        for angle in [0, 90, 180, 90]:
            self.set_waist_rotation(angle)
            time.sleep(1)
        
        # Test voice
        print("\n5. Testing voice output...")
        self.speak("Robot test complete")
        
        print("\n" + "="*50)
        print("TEST COMPLETE")
        print("="*50 + "\n")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.stop_all()
            print("Robot controller shutdown")
        except:
            pass


# ==================== STANDALONE TESTING ====================

if __name__ == '__main__':
    """
    Run this file directly to test the robot control layer
    without the web interface
    """
    print("Starting robot control test...")
    
    try:
        robot = RobotController()
        
        # Option 1: Run full component test
        robot.test_all_components()
        
        # Option 2: Manual testing
        # robot.drive_forward(50)
        # import time
        # time.sleep(2)
        # robot.stop_all()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        robot.stop_all()
    except Exception as e:
        print(f"\nError during test: {e}")
        robot.stop_all()
