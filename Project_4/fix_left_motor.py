#!/usr/bin/env python3
"""
Attempt to compensate for weak left motor with a multiplier.
This is a SOFTWARE workaround for a HARDWARE issue.
"""

from maestro import Controller
import time

maestro = Controller()

print("="*70)
print("LEFT MOTOR COMPENSATION TEST")
print("="*70)
print("\nThis test tries different multipliers for the left motor")
print("to compensate for it being weaker than the right motor.\n")

def test_with_multiplier(left_mult):
    """Test driving 'forward' with a multiplier on the left motor."""
    base_speed = 0.3

    # Calculate positions
    # Left: negative speed, with multiplier
    left_speed = -base_speed * left_mult
    left_speed = max(-1.0, min(1.0, left_speed))  # clamp
    if left_speed >= 0:
        left_pos = int(6000 + left_speed * (8000 - 6000))
    else:
        left_pos = int(6000 + left_speed * (6000 - 4000))

    # Right: positive speed, no multiplier
    right_speed = base_speed
    right_pos = int(6000 + right_speed * (8000 - 6000))

    print(f"\nMultiplier: {left_mult:.1f}")
    print(f"  Left:  speed={left_speed:+.2f} → position={left_pos}")
    print(f"  Right: speed={right_speed:+.2f} → position={right_pos}")
    print(f"  Driving for 2 seconds...")

    maestro.setTarget(0, left_pos)
    maestro.setTarget(1, right_pos)
    time.sleep(2)

    # Stop
    maestro.setTarget(0, 6000)
    maestro.setTarget(1, 6000)
    time.sleep(0.5)

# Test different multipliers
for mult in [1.0, 1.5, 2.0, 2.5, 3.0]:
    test_with_multiplier(mult)

    response = input(f"\n>>> Multiplier {mult}: Did robot drive STRAIGHT? (y/n/q): ").strip().lower()
    if response == 'y':
        print(f"\n{'='*70}")
        print(f"SOLUTION FOUND: Use multiplier {mult} for left motor")
        print(f"{'='*70}")
        print(f"\nTo implement this:")
        print(f"  1. Edit motor.py to add a speed_multiplier parameter")
        print(f"  2. Or edit wall_follower.py to multiply left motor commands by {mult}")
        print(f"  3. Or fix the hardware issue (preferred!)")
        break
    elif response == 'q':
        break

print("\n" + "="*70)
print("IMPORTANT: This is a SOFTWARE WORKAROUND for a HARDWARE PROBLEM")
print("="*70)
print("\nThe ROOT CAUSE is likely one of these:")
print("  1. Maestro Control Center has SPEED LIMIT set too low on channel 0")
print("  2. Maestro Control Center has ACCELERATION set too low on channel 0")
print("  3. Loose wire connection on channel 0")
print("  4. Weak/damaged left motor")
print("  5. Insufficient power supply current")
print("\nTo check Maestro settings:")
print("  - Install 'Pololu Maestro Control Center' on your computer")
print("  - Connect via USB")
print("  - Check Channel Settings tab for channels 0 and 1")
print("  - Ensure Speed and Acceleration are the SAME for both channels")
print("  - Default should be 0 (unlimited) or very high values")
