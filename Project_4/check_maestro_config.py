#!/usr/bin/env python3
"""
Check Maestro configuration for both motor channels.
Speed and acceleration limits can cause one motor to respond slower than the other.
"""

from maestro import Controller
import time

maestro = Controller()

print("="*70)
print("MAESTRO CONFIGURATION CHECK")
print("="*70)

print("\nChecking channel 0 (left motor) and channel 1 (right motor)")
print("-"*70)

# Try to read position for both channels
try:
    left_pos = maestro.getPosition(0)
    right_pos = maestro.getPosition(1)
    print(f"Channel 0 (left) current position:  {left_pos}")
    print(f"Channel 1 (right) current position: {right_pos}")
except Exception as e:
    print(f"Could not read positions: {e}")

print("\n" + "-"*70)
print("Testing with VERY HIGH position values to rule out range issues")
print("-"*70)

# Test with more extreme values
print("\nSending LEFT motor to position 4000 (minimum) for 2 seconds...")
maestro.setTarget(0, 4000)
time.sleep(2)
maestro.setTarget(0, 6000)  # back to center

print("Sending RIGHT motor to position 8000 (maximum) for 2 seconds...")
maestro.setTarget(1, 8000)
time.sleep(2)
maestro.setTarget(1, 6000)  # back to center

print("\n" + "-"*70)
print("Testing both motors at FULL SPEED difference from center")
print("-"*70)

print("\nBoth motors to MAXIMUM deflection for 2 seconds...")
print("  Left:  position 4000 (full reverse/forward)")
print("  Right: position 8000 (full forward)")
maestro.setTarget(0, 4000)
maestro.setTarget(1, 8000)
time.sleep(2)

# Stop
maestro.setTarget(0, 6000)
maestro.setTarget(1, 6000)

print("\n" + "="*70)
print("MAESTRO TEST COMPLETE")
print("="*70)
print("\nDid the left motor move during these tests?")
print("\nIf LEFT motor still barely moves, check:")
print("  1. Maestro Control Center - channel 0 speed/acceleration limits")
print("  2. Physical connections - is channel 0 wire loose?")
print("  3. Motor health - try swapping motor connections")
print("  4. Power supply - is there enough current for both motors?")
