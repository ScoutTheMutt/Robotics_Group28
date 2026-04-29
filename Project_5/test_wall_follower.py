"""
test_wall_follower.py — Offline tests for WallFollower decision logic.

Run with:  python test_wall_follower.py

Does NOT require hardware — uses a mock lidar and robot.
"""

from wall_follower import WallFollower, WALL_TARGET_MM, WALL_LOWER_MM, WALL_UPPER_MM, WALL_LOST_MM, FRONT_STOP_MM


# ---------------------------------------------------------------------------
# Minimal mocks
# ---------------------------------------------------------------------------

class MockLidar:
    def __init__(self, front=None, right=None, fr=None):
        self.front_dist = front
        self.right_dist = right
        self.front_right_dist = fr


class MockRobot:
    def __init__(self):
        self.last_call = None
        self.last_speeds = None

    def setWheelSpeeds(self, l, r):
        self.last_call = 'setWheelSpeeds'
        self.last_speeds = (l, r)

    def turnLeft(self, speed=0.15):
        self.last_call = 'turnLeft'

    def turnRight(self, speed=0.15):
        self.last_call = 'turnRight'

    def stop(self):
        self.last_call = 'stop'


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _decide(front=None, right=None, fr=None):
    lidar = MockLidar(front=front, right=right, fr=fr)
    robot = MockRobot()
    wf = WallFollower(robot, lidar)
    return wf._decide(front, right, fr)


def check(label, got, expected):
    status = "PASS" if got == expected else "FAIL"
    print(f"  [{status}] {label}: got={got!r}, expected={expected!r}")
    return got == expected


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_obstacle_in_front():
    print("test_obstacle_in_front")
    check("close front blocks", _decide(front=200, right=WALL_TARGET_MM), 'OBSTACLE_AVOID')
    check("borderline front blocks", _decide(front=FRONT_STOP_MM - 1, right=WALL_TARGET_MM), 'OBSTACLE_AVOID')
    check("front just clear", _decide(front=FRONT_STOP_MM + 1, right=WALL_TARGET_MM), 'FORWARD')
    check("no front reading with good wall", _decide(front=None, right=WALL_TARGET_MM), 'FORWARD')


def test_wall_lost():
    print("test_wall_lost")
    check("no right reading", _decide(front=None, right=None), 'SEARCH')
    check("right too far", _decide(front=None, right=WALL_LOST_MM + 1), 'SEARCH')
    check("right at lost boundary (still detected, steers toward)", _decide(front=None, right=WALL_LOST_MM), 'STEER_TOWARD')


def test_wall_too_close():
    print("test_wall_too_close")
    check("right too close", _decide(front=None, right=WALL_LOWER_MM - 1), 'STEER_AWAY')
    check("fr too close triggers steer away", _decide(front=None, right=WALL_TARGET_MM, fr=WALL_LOWER_MM - 1), 'STEER_AWAY')


def test_wall_too_far():
    print("test_wall_too_far")
    check("right too far but not lost", _decide(front=None, right=WALL_UPPER_MM + 1), 'STEER_TOWARD')
    check("right at upper boundary", _decide(front=None, right=WALL_UPPER_MM), 'FORWARD')


def test_forward():
    print("test_forward")
    check("target distance", _decide(front=None, right=WALL_TARGET_MM), 'FORWARD')
    check("lower boundary ok", _decide(front=None, right=WALL_LOWER_MM), 'FORWARD')
    check("upper boundary ok", _decide(front=None, right=WALL_UPPER_MM), 'FORWARD')


def test_obstacle_overrides_wall():
    print("test_obstacle_overrides_wall")
    check("front obstacle beats wall-too-close", _decide(front=100, right=100), 'OBSTACLE_AVOID')
    check("front obstacle beats wall-lost", _decide(front=100, right=None), 'OBSTACLE_AVOID')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    tests = [
        test_forward,
        test_wall_too_close,
        test_wall_too_far,
        test_wall_lost,
        test_obstacle_in_front,
        test_obstacle_overrides_wall,
    ]

    passed = 0
    failed = 0

    for t in tests:
        t()
        print()

    print("Done — review output above for any FAIL lines.")
