"""
Action Runner
Executes robot action sequences in a background thread queue.
All actions respect the cancel flag and enforce hard time caps.
"""

import queue
import threading
import time


class ActionRunner:
    # Hard time caps (seconds) per action
    CAPS = {
        'head_yes': 3.0,
        'head_no': 3.0,
        'arm_raise': 4.0,
        'dance90': 6.0,
    }

    def __init__(self, robot):
        self.robot = robot
        self.q = queue.Queue()
        self._cancel = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def enqueue(self, actions):
        """Add a list of action names to the queue."""
        if actions:
            self.q.put(list(actions))

    def cancel(self):
        """Cancel all pending and in-progress actions and stop wheels."""
        self._cancel.set()
        # Drain queue
        while not self.q.empty():
            try:
                self.q.get_nowait()
                self.q.task_done()
            except queue.Empty:
                break
        self.robot.stop()

    def resume(self):
        """Clear cancel flag so new actions can run."""
        self._cancel.clear()

    # ------------------------------------------------------------------
    # Worker loop
    # ------------------------------------------------------------------

    def _run(self):
        """Background worker: get action lists, execute each action."""
        while True:
            action_list = self.q.get()
            for action_name in action_list:
                if self._cancel.is_set():
                    break
                self._dispatch(action_name)
            self.q.task_done()

    def _dispatch(self, action_name):
        """Dispatch a single action with a hard cap timeout."""
        handler = {
            'head_yes': self._head_yes,
            'head_no': self._head_no,
            'arm_raise': self._arm_raise,
            'dance90': self._dance90,
        }.get(action_name)

        if handler is None:
            print(f"[WARNING] Unknown action dispatched: {action_name}")
            return

        cap = self.CAPS.get(action_name, 5.0)
        print(f"[ACTION] START {action_name}")

        # Watchdog timer cancels if action exceeds cap
        watchdog = threading.Timer(cap, self._timeout_cancel, args=(action_name,))
        watchdog.daemon = True
        watchdog.start()
        try:
            handler()
        finally:
            watchdog.cancel()
            print(f"[ACTION] END {action_name}")

    def _timeout_cancel(self, action_name):
        print(f"[ACTION] TIMEOUT {action_name} — cancelling")
        self.cancel()

    # ------------------------------------------------------------------
    # Action implementations
    # ------------------------------------------------------------------

    def _sleep(self, duration):
        """Sleep in small increments, checking cancel flag."""
        end = time.time() + duration
        while time.time() < end:
            if self._cancel.is_set():
                return
            time.sleep(min(0.05, end - time.time()))

    def _head_yes(self):
        """Nod head up and down."""
        if self._cancel.is_set():
            return
        self.robot.setHeadTilt(-25)
        self._sleep(0.5)
        if self._cancel.is_set():
            return
        self.robot.setHeadTilt(25)
        self._sleep(0.5)
        if self._cancel.is_set():
            return
        self.robot.setHeadTilt(0)
        self._sleep(0.3)

    def _head_no(self):
        """Shake head left and right."""
        if self._cancel.is_set():
            return
        self.robot.setHeadPan(-45)
        self._sleep(0.5)
        if self._cancel.is_set():
            return
        self.robot.setHeadPan(45)
        self._sleep(0.5)
        if self._cancel.is_set():
            return
        self.robot.setHeadPan(0)
        self._sleep(0.3)

    def _arm_raise(self):
        """Raise left arm and lower it."""
        if self._cancel.is_set():
            return
        self.robot.setArmAngle(-90)
        self.robot.setElbowAngle(-45)
        self._sleep(2.5)
        if self._cancel.is_set():
            return
        self.robot.setArmAngle(0)
        self.robot.setElbowAngle(0)
        self._sleep(0.5)

    def _dance90(self):
        """Spin ~90 degrees using timed differential drive."""
        flag = True
        try:
            if self._cancel.is_set():
                return
            while flag==True:
                self.robot.setWheelSpeeds(0.55, -0.55)
                self._sleep(1)
                flag = False
            if self._cancel.is_set():
                return
            self.robot.stop()
            self._sleep(0.1)
            if self._cancel.is_set():
                return
            while flag==False:
                self.robot.setWheelSpeeds(-0.55, 0.55)
                self._sleep(1)
                flag = True
            if self._cancel.is_set():
                return
            self.robot.stop()
            self._sleep(0.1)
            if self._cancel.is_set():
                return
            while flag==True:
                self.robot.setWheelSpeeds(0.55, -0.55)
                self._sleep(1)
                flag = False
            if self._cancel.is_set():
                return
            self.robot.stop()
            self._sleep(0.1)
            if self._cancel.is_set():
                return
            while flag==False:
                self.robot.setWheelSpeeds(-0.55, 0.55)
                self._sleep(.75)
                flag = True
        finally:
            self.robot.stop()
