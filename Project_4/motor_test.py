#!/usr/bin/env python3
"""
Motor Diagnostic Test
Tests each motor individually to find the right power multiplier.
"""

import time
import sys
from robot import Robot

def test_individual_motors(robot, speed=0.3):
    """Test each motor individually at the same speed."""
    print(f"\n{'='*60}")
    print(f"Testing motors at speed {speed}")
    print(f"{'='*60}\n")

    # Test left motor only
    print(f"[TEST] Left motor ONLY at speed {speed}")
    print("[TEST] Watch if left wheel moves. Press Ctrl+C to stop...")
    try:
        robot.setWheelSpeedsRaw(-speed, 0)  # Left forward, right stopped
        time.sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
        robot.stop()
        time.sleep(1)

    # Test right motor only
    print(f"\n[TEST] Right motor ONLY at speed {speed}")
    print("[TEST] Watch if right wheel moves. Press Ctrl+C to stop...")
    try:
        robot.setWheelSpeedsRaw(0, speed)  # Left stopped, right forward
        time.sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
        robot.stop()
        time.sleep(1)


def test_multiplier(robot, base_speed=0.3, multiplier=1.5):
    """Test driving forward with a multiplier on the left motor."""
    print(f"\n{'='*60}")
    print(f"Testing FORWARD with left motor multiplier: {multiplier}")
    print(f"Left speed: {-base_speed * multiplier:.2f}, Right speed: {base_speed:.2f}")
    print(f"{'='*60}\n")

    print("[TEST] Both motors forward with multiplier. Press Ctrl+C to stop...")
    try:
        robot.setWheelSpeedsRaw(-base_speed * multiplier, base_speed)
        time.sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
        robot.stop()
        time.sleep(1)


def main():
    print("\n" + "="*60)
    print("MOTOR DIAGNOSTIC TEST")
    print("="*60)

    robot = Robot()

    try:
        # Step 1: Test each motor individually
        test_individual_motors(robot, speed=0.3)
        test_individual_motors(robot, speed=0.5)

        # Step 2: Test different multipliers
        print("\n" + "="*60)
        print("Now testing different multipliers for the left motor")
        print("="*60)

        for mult in [1.0, 1.5, 2.0, 2.5, 3.0]:
            test_multiplier(robot, base_speed=0.3, multiplier=mult)

            response = input(f"\nMultiplier {mult}: Did robot drive straight? (y/n/q to quit): ").strip().lower()
            if response == 'y':
                print(f"\n*** OPTIMAL MULTIPLIER FOUND: {mult} ***")
                print(f"Update robot.py or wall_follower.py to use this multiplier for the left motor")
                break
            elif response == 'q':
                break

    except KeyboardInterrupt:
        print("\n[TEST] Interrupted by user")
    finally:
        robot.stop()
        print("\n[TEST] Motors stopped. Test complete.")


if __name__ == '__main__':
    main()
