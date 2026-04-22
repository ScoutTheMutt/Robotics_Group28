#!/usr/bin/env python3
"""
Direct motor diagnostic - shows exactly what's being sent to each motor.
"""

import time
from robot import Robot

print("="*70)
print("MOTOR DIAGNOSTIC - DIRECT HARDWARE TEST")
print("="*70)

robot = Robot()

print("\n[TEST 1] Testing driveForward() method")
print("-"*70)
print("Calling robot.driveForward(speed=0.3) for 2 seconds...")
robot.driveForward(speed=0.3)
time.sleep(2)
robot.stop()
print("Stopped.\n")

time.sleep(1)

print("[TEST 2] Testing setWheelSpeedsRaw() directly")
print("-"*70)
print("Calling robot.setWheelSpeedsRaw(-0.3, 0.3) for 2 seconds...")
print("  Left motor (Ch0): -0.3 (should go forward)")
print("  Right motor (Ch1): 0.3 (should go forward)")
robot.setWheelSpeedsRaw(-0.3, 0.3)
time.sleep(2)
robot.stop()
print("Stopped.\n")

time.sleep(1)

print("[TEST 3] Testing each motor individually")
print("-"*70)

print("\nLeft motor ONLY at -0.5 for 2 seconds...")
robot.setWheelSpeedsRaw(-0.5, 0)
time.sleep(2)
robot.stop()
time.sleep(1)

print("Right motor ONLY at 0.5 for 2 seconds...")
robot.setWheelSpeedsRaw(0, 0.5)
time.sleep(2)
robot.stop()
time.sleep(1)

print("\n[TEST 4] Testing higher left motor speed")
print("-"*70)
print("Trying left=-0.6, right=0.3 for 2 seconds...")
robot.setWheelSpeedsRaw(-0.6, 0.3)
time.sleep(2)
robot.stop()
time.sleep(1)

print("\n[TEST 5] Checking motor position calculations")
print("-"*70)
from motor import Motor

# Create test motor instances
left = Motor(robot.maestro, channel=0)
right = Motor(robot.maestro, channel=1)

print("\nLeft motor position calculations:")
for speed in [-0.3, -0.5, -0.7]:
    if speed >= 0:
        position = int(6000 + speed * (8000 - 6000))
    else:
        position = int(6000 + speed * (6000 - 4000))
    print(f"  Speed {speed:5.1f} → Position {position}")

print("\nRight motor position calculations:")
for speed in [0.3, 0.5, 0.7]:
    if speed >= 0:
        position = int(6000 + speed * (8000 - 6000))
    else:
        position = int(6000 + speed * (6000 - 4000))
    print(f"  Speed {speed:5.1f} → Position {position}")

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)
print("\nDid BOTH wheels move in all tests?")
print("If left wheel barely moved, it might need:")
print("  1. Higher speed values (try multiplier)")
print("  2. Different position range calibration")
print("  3. Hardware check (connection, motor health)")
