#!/usr/bin/env python3
"""Test the 2.5x multiplier implementation."""

import time
from robot import Robot

print("="*70)
print("TESTING 2.5x MULTIPLIER IMPLEMENTATION")
print("="*70)

robot = Robot()

print("\n[TEST 1] driveForward(0.3) - should now drive straight")
print("-"*70)
robot.driveForward(speed=0.3)
time.sleep(3)
robot.stop()

print("\n[TEST 2] setWheelSpeedsRaw(-0.3, 0.3) - left should get 2.5x boost")
print("-"*70)
robot.setWheelSpeedsRaw(-0.3, 0.3)
time.sleep(3)
robot.stop()

print("\n[TEST 3] Wall follower speeds")
print("-"*70)
print("Testing typical wall follower FORWARD speeds...")
robot.setWheelSpeedsRaw(-0.6, 0.6)
time.sleep(3)
robot.stop()

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nDid the robot drive straight in all tests?")
print("The left motor should now receive 2.5x the commanded speed.")
