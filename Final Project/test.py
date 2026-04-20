from rplidar import RPLidar
import time

lidar = RPLidar('/dev/ttyUSB0')  # adjust port if needed
lidar.reset()
time.sleep(1)
# flush stale bytes if possible; use getattr to avoid static attribute access errors
serial_obj = getattr(lidar, "_serial", None) or getattr(lidar, "serial", None)
if serial_obj is not None:
    try:
        serial_obj.reset_input_buffer()
    except Exception:
        # ignore flush errors and continue
        pass

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