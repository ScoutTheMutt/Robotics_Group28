#!/usr/bin/env python3
"""Live wall follower hardware test - runs the actual wall follower."""

import time
from robot import Robot
from lidar import LidarMonitor
from wall_follower import WallFollower

print("="*60)
print("LIVE WALL FOLLOWER TEST")
print("="*60)

print("\nInitializing robot and LIDAR...")
robot = Robot()
lidar = LidarMonitor(port='/dev/ttyUSB0')
robot.set_lidar(lidar)
lidar.start()

wall_follower = WallFollower(robot, lidar)

try:
    print("\n" + "="*60)
    print("STARTING WALL FOLLOWER IN 3 SECONDS...")
    print("Place robot near a wall on the RIGHT side")
    print("Press Ctrl+C to stop")
    print("="*60)
    time.sleep(3)

    wall_follower.start()
    print("\n[RUNNING] Wall follower active. Watch the robot move!\n")

    # Run until interrupted
    while True:
        time.sleep(0.5)
        # Print status
        print(f"\rState: {wall_follower.state:15s}  "
              f"Front: {lidar.front_dist or 'None':>6}  "
              f"Right: {lidar.right_dist or 'None':>6}  "
              f"FR: {lidar.front_right_dist or 'None':>6}", end='', flush=True)

except KeyboardInterrupt:
    print("\n\n[STOPPING] Interrupted by user...")
finally:
    wall_follower.stop()
    robot.stop()
    lidar.stop()
    print("[DONE] Test complete. Robot stopped.")
