from rplidar import RPLidar
import time

lidar = RPLidar('/dev/ttyUSB0')  # adjust port if needed
lidar.reset()
time.sleep(1)
lidar._serial.reset_input_buffer()  # flush stale bytes (replaces clean_input_buf)

print("Health:", lidar.get_health())
print("Info:", lidar.get_info())

for i, scan in enumerate(lidar.iter_scans()):
    print(f"Scan {i}: {len(scan)} points")
    for quality, angle, distance in scan[:5]:  # first 5 points
        print(f"  q={quality} angle={angle:.1f} dist={distance:.0f}mm")
    if i >= 2:
        break

lidar.stop()
lidar.stop_motor()
lidar.disconnect()