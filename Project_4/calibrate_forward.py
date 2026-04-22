#!/usr/bin/env python3
"""
Interactive forward speed calibration tool.
Quickly test different left and right wheel speeds to find the perfect balance.
"""

import time
from robot import Robot

print("="*70)
print("INTERACTIVE FORWARD SPEED CALIBRATION")
print("="*70)
print("\nThis tool lets you calibrate both left and right wheel speeds.")
print("Left wheel has ×2.5 multiplier applied automatically.")
print("\nCommands:")
print("  r+  / r-  : adjust right wheel by 0.01")
print("  r++ / r-- : adjust right wheel by 0.05")
print("  l+  / l-  : adjust left wheel by 0.01")
print("  l++ / l-- : adjust left wheel by 0.05")
print("  t         : test current speeds for 3 seconds")
print("  s         : save values and update wall_follower.py")
print("  q         : quit without saving")
print("="*70)

robot = Robot()
left_speed = -0.5   # Starting value (current setting)
right_speed = 0.4   # Starting value (current setting)

def test_speeds():
    """Drive forward for 3 seconds with current speeds."""
    actual_left = left_speed * 2.5
    clamped_left = max(-1.0, min(1.0, actual_left))
    print(f"\n>>> Testing: Left={left_speed:.2f} (×2.5={actual_left:.2f}→{clamped_left:.2f}), Right={right_speed:.2f}")
    print(">>> Driving for 3 seconds... watch the wheels!")
    robot.setWheelSpeedsRaw(left_speed, right_speed)
    time.sleep(3)
    robot.stop()
    print(">>> Stopped.\n")

def save_to_file():
    """Update wall_follower.py with the calibrated values."""
    filename = 'wall_follower.py'

    # Read the file
    with open(filename, 'r') as f:
        content = f.read()

    # Replace the FORWARD setWheelSpeedsRaw line
    if 'setWheelSpeedsRaw' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'if state == \'FORWARD\'' in line or 'if state == "FORWARD"' in line:
                # Found FORWARD block, now find the setWheelSpeedsRaw line
                for j in range(i, min(i+5, len(lines))):
                    if 'setWheelSpeedsRaw' in lines[j]:
                        lines[j] = f'            self._robot.setWheelSpeedsRaw({left_speed:.2f}, {right_speed:.2f})'
                        break
                break

        with open(filename, 'w') as f:
            f.write('\n'.join(lines))

        actual_left = left_speed * 2.5
        clamped_left = max(-1.0, min(1.0, actual_left))
        print(f"\n✓ Saved to {filename}:")
        print(f"  setWheelSpeedsRaw({left_speed:.2f}, {right_speed:.2f})")
        print(f"  Actual speeds: Left={clamped_left:.2f}, Right={right_speed:.2f}")
        return True
    else:
        print(f"\n✗ Could not find FORWARD section in {filename}")
        return False

# Initial test
test_speeds()

try:
    while True:
        actual_left = left_speed * 2.5
        clamped_left = max(-1.0, min(1.0, actual_left))
        cmd = input(f"Left={left_speed:.2f}(×2.5={clamped_left:.2f}) Right={right_speed:.2f} | Command: ").strip().lower()

        if cmd == 'r+':
            new_val = right_speed + 0.01
            if new_val <= 1.0:
                right_speed = round(new_val, 2)
                print(f"Right wheel increased to {right_speed:.2f}")
                test_speeds()
            else:
                print("⚠ Right wheel at maximum (1.0)")

        elif cmd == 'r++':
            new_val = right_speed + 0.05
            if new_val <= 1.0:
                right_speed = round(new_val, 2)
                print(f"Right wheel increased to {right_speed:.2f}")
                test_speeds()
            else:
                print("⚠ Right wheel at maximum (1.0)")

        elif cmd == 'r-':
            new_val = right_speed - 0.01
            if new_val >= 0.0:
                right_speed = round(new_val, 2)
                print(f"Right wheel decreased to {right_speed:.2f}")
                test_speeds()
            else:
                print("⚠ Right wheel at minimum (0.0)")

        elif cmd == 'r--':
            new_val = right_speed - 0.05
            if new_val >= 0.0:
                right_speed = round(new_val, 2)
                print(f"Right wheel decreased to {right_speed:.2f}")
                test_speeds()
            else:
                print("⚠ Right wheel at minimum (0.0)")

        elif cmd == 'l+':
            new_val = left_speed + 0.01
            if new_val <= 0.0:
                left_speed = round(new_val, 2)
                print(f"Left wheel increased to {left_speed:.2f} (less negative = slower)")
                test_speeds()
            else:
                print("⚠ Left wheel at maximum (0.0 = stopped)")

        elif cmd == 'l++':
            new_val = left_speed + 0.05
            if new_val <= 0.0:
                left_speed = round(new_val, 2)
                print(f"Left wheel increased to {left_speed:.2f} (less negative = slower)")
                test_speeds()
            else:
                print("⚠ Left wheel at maximum (0.0 = stopped)")

        elif cmd == 'l-':
            new_val = left_speed - 0.01
            if new_val >= -1.0:
                left_speed = round(new_val, 2)
                print(f"Left wheel decreased to {left_speed:.2f} (more negative = faster)")
                test_speeds()
            else:
                print("⚠ Left wheel at minimum (-1.0, but ×2.5 will clamp)")

        elif cmd == 'l--':
            new_val = left_speed - 0.05
            if new_val >= -1.0:
                left_speed = round(new_val, 2)
                print(f"Left wheel decreased to {left_speed:.2f} (more negative = faster)")
                test_speeds()
            else:
                print("⚠ Left wheel at minimum (-1.0, but ×2.5 will clamp)")

        elif cmd == 't':
            test_speeds()

        elif cmd == 's':
            if save_to_file():
                print(f"\n{'='*70}")
                print(f"CALIBRATION COMPLETE!")
                print(f"Final speeds: Left={left_speed:.2f} (×2.5={clamped_left:.2f}), Right={right_speed:.2f}")
                print(f"{'='*70}\n")
                break
            else:
                print("Save failed. Try again or quit with 'q'.")

        elif cmd == 'q':
            print("\nQuitting without saving.")
            break

        else:
            print("Unknown command. Use r+/r-/l+/l-/r++/r--/l++/l--/t/s/q")

except KeyboardInterrupt:
    print("\n\nInterrupted. Stopping motors.")

finally:
    robot.stop()
    print("Motors stopped.")
