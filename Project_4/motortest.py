from maestro import Controller
from motor import Motor
import time

m = Controller()
left = Motor(m, 0)
right = Motor(m, 1)

print('Left -0.6')
left.setSpeed(-0.6)
time.sleep(2)
left.setSpeed(0)
time.sleep(1)

print('Left +0.6')
left.setSpeed(0.6)
time.sleep(2)
left.setSpeed(0)
time.sleep(1)

print('Right -0.6')
right.setSpeed(-0.6)
time.sleep(2)
right.setSpeed(0)
time.sleep(1)

print('Right +0.6')
right.setSpeed(0.6)
time.sleep(2)
right.setSpeed(0)
m.close()
