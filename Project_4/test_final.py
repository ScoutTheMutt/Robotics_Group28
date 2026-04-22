#!/usr/bin/env python3
"""Final test: verify robot drives straight with 2.5x multiplier."""

import time
from robot import Robot

print("="*70)
print("FINAL DRIVE TEST - 2.5x Multiplier Active")
print("="*70)

robot = Robot()

print("\n1. Testing driveForward(0.2)")
robot.driveForward(0.2)
time.sleep(2)
robot.stop()
time.sleep(1)

print("\n2. Testing driveForward(0.3)")
robot.driveForward(0.3)
time.sleep(2)
robot.stop()
time.sleep(1)

print("\n3. Testing driveForward(0.4)")
robot.driveForward(0.4)
time.sleep(2)
robot.stop()
time.sleep(1)

print("\n4. Testing turnLeft()")
robot.turnLeft(0.15)
time.sleep(2)
robot.stop()
time.sleep(1)

print("\n5. Testing turnRight()")
robot.turnRight(0.15)
time.sleep(2)
robot.stop()

print("\n" + "="*70)
print("If robot drove straight forward in tests 1-3, the fix is working!")
print("="*70)
