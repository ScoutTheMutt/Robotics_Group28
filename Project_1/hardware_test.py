"""
Hardware Bring-Up and Verification Script (Step A)
Tests each component individually to verify hardware function
"""

from maestro import Controller
import time

def test_motors():
    """Test drive motors (forward/backward motion)"""
    print("\n=== Testing Drive Motors ===")
    print("Testing Servo 0 (Left wheel - Forward/Backward)")
    print("Testing Servo 1 (Right wheel - Left/Right)")
    
    maestro = Controller()
    
    # Neutral/stop position
    STOP = 6000
    
    print("\n1. Setting motors to STOP position...")
    maestro.setTarget(0, STOP)
    maestro.setTarget(1, STOP)
    time.sleep(2)
    
    print("2. Testing FORWARD motion (3 seconds)...")
    maestro.setTarget(0, 7000)  # Servo 0 forward
    maestro.setTarget(1, 7000)  # Servo 1 forward
    time.sleep(3)
    
    print("3. STOPPING...")
    maestro.setTarget(0, STOP)
    maestro.setTarget(1, STOP)
    time.sleep(2)
    
    print("4. Testing BACKWARD motion (3 seconds)...")
    maestro.setTarget(0, 5000)  # Servo 0 backward
    maestro.setTarget(1, 5000)  # Servo 1 backward
    time.sleep(3)
    
    print("5. STOPPING...")
    maestro.setTarget(0, STOP)
    maestro.setTarget(1, STOP)
    time.sleep(1)
    
    print("\n✓ Drive motor test complete")
    print("Direction notes:")
    print("  - Forward: position > 6000")
    print("  - Backward: position < 6000")
    print("  - Stop: position = 6000")
    print("  - Safe range: 4000 - 8000")


def test_head():
    """Test head tilt and pan"""
    print("\n=== Testing Head Movement ===")
    print("Testing Servo 3 (Head Tilt - Up/Down)")
    print("Testing Servo 4 (Head Pan - Left/Right)")
    
    maestro = Controller()
    CENTER = 6000
    
    print("\n1. Centering head...")
    maestro.setTarget(3, CENTER)  # Tilt center
    maestro.setTarget(4, CENTER)  # Pan center
    time.sleep(2)
    
    print("2. Testing PAN - Looking LEFT...")
    maestro.setTarget(4, 7500)
    time.sleep(2)
    
    print("3. Testing PAN - Looking RIGHT...")
    maestro.setTarget(4, 4500)
    time.sleep(2)
    
    print("4. Testing PAN - Back to CENTER...")
    maestro.setTarget(4, CENTER)
    time.sleep(2)
    
    print("5. Testing TILT - Looking UP...")
    maestro.setTarget(3, 7000)
    time.sleep(2)
    
    print("6. Testing TILT - Looking DOWN...")
    maestro.setTarget(3, 5000)
    time.sleep(2)
    
    print("7. Returning to CENTER...")
    maestro.setTarget(3, CENTER)
    maestro.setTarget(4, CENTER)
    time.sleep(1)
    
    print("\n✓ Head movement test complete")
    print("Direction notes:")
    print("  Pan (Servo 4):")
    print("    - Left: position > 6000")
    print("    - Right: position < 6000")
    print("  Tilt (Servo 3):")
    print("    - Up: position > 6000")
    print("    - Down: position < 6000")
    print("  - Center: position = 6000")
    print("  - Safe range: 4000 - 8000")


def test_waist():
    """Test waist rotation"""
    print("\n=== Testing Waist Rotation ===")
    print("Testing Servo 2 (Body Turn Left/Right)")
    
    maestro = Controller()
    CENTER = 6000
    
    print("\n1. Centering waist...")
    maestro.setTarget(2, CENTER)
    time.sleep(2)
    
    print("2. Rotating LEFT...")
    maestro.setTarget(2, 7500)
    time.sleep(3)
    
    print("3. Rotating RIGHT...")
    maestro.setTarget(2, 4500)
    time.sleep(3)
    
    print("4. Returning to CENTER...")
    maestro.setTarget(2, CENTER)
    time.sleep(2)
    
    print("\n✓ Waist rotation test complete")
    print("Direction notes:")
    print("  - Left rotation: position > 6000")
    print("  - Right rotation: position < 6000")
    print("  - Center: position = 6000")
    print("  - Safe range: 4000 - 8000")


def test_arms():
    """Test arm servos to identify broken components"""
    print("\n=== Testing Arms (Diagnostic Only) ===")
    print("Note: Servo 5 (Right arm lift) is marked as BROKEN")
    print("Testing other arm servos for functionality...")
    
    maestro = Controller()
    CENTER = 6000
    
    # Right arm servos (skip 5 - broken)
    right_arm_servos = {
        6: "Right arm in/out",
        7: "Right elbow up/down",
        8: "Right wrist up/down",
        9: "Right wrist rotate",
        10: "Right hand open/close"
    }
    
    # Left arm servos
    left_arm_servos = {
        11: "Left arm lift",
        12: "Left arm in/out",
        13: "Left elbow up/down",
        14: "Left wrist up/down",
        15: "Left wrist rotate",
        16: "Left hand open/close"
    }
    
    print("\nTesting RIGHT arm servos (excluding broken Servo 5)...")
    for channel, description in right_arm_servos.items():
        print(f"  Testing Servo {channel}: {description}")
        maestro.setTarget(channel, CENTER)
        time.sleep(0.5)
        maestro.setTarget(channel, 7000)
        time.sleep(1)
        maestro.setTarget(channel, CENTER)
        time.sleep(0.5)
    
    print("\nTesting LEFT arm servos...")
    for channel, description in left_arm_servos.items():
        print(f"  Testing Servo {channel}: {description}")
        maestro.setTarget(channel, CENTER)
        time.sleep(0.5)
        maestro.setTarget(channel, 7000)
        time.sleep(1)
        maestro.setTarget(channel, CENTER)
        time.sleep(0.5)
    
    print("\n✓ Arm diagnostic test complete")
    print("Known issues:")
    print("  - Servo 5 (Right arm lift): BROKEN - needs replacement")
    print("\nPlease note any additional broken servos found during testing.")


def main():
    """Run all hardware tests"""
    print("=" * 60)
    print("ROBOT HARDWARE BRING-UP AND VERIFICATION")
    print("=" * 60)
    print("\nThis script will test:")
    print("  ✓ Drive wheels (Servos 0, 1)")
    print("  ✓ Head tilt and pan (Servos 3, 4)")
    print("  ✓ Waist rotation (Servo 2)")
    print("  ✓ Arm servos (diagnostic - Servos 6-16, excluding broken #5)")
    print("\nWARNING: Ensure robot has clear space to move!")
    
    input("\nPress ENTER to begin tests...")
    
    try:
        # Run tests in order
        test_motors()
        time.sleep(2)
        
        test_head()
        time.sleep(2)
        
        test_waist()
        time.sleep(2)
        
        test_arms()
        
        print("\n" + "=" * 60)
        print("HARDWARE VERIFICATION COMPLETE")
        print("=" * 60)
        print("\nAll required components have been tested.")
        print("Document any additional hardware issues found.")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nERROR during testing: {e}")
        print("This may indicate a hardware or connection problem.")


if __name__ == "__main__":
    main()
