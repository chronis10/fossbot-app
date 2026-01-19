import time

class Input:
    def __init__(self, robot, debounce_s=0.18, poll_dt=0.05):
        self.robot = robot
        self.debounce_s = debounce_s
        self.poll_dt = poll_dt
        self.last_action_t = 0.0
        self.last_state = self.get_raw_state()

    def get_raw_state(self):
        return {
            "bt1": self.robot.bt1.is_pressed(),
            "bt2": self.robot.bt2.is_pressed(),
            "bt3": self.robot.bt3.is_pressed(),
            "bt4": self.robot.bt4.is_pressed(),
        }

    def get_pressed_buttons(self):
        now = time.monotonic()
        can_act = (now - self.last_action_t) >= self.debounce_s

        if not can_act:
            self.last_state = self.get_raw_state()
            return {}

        current_state = self.get_raw_state()
        pressed = {k: (current_state[k] and not self.last_state[k]) for k in current_state.keys()}
        
        if any(pressed.values()):
            self.last_action_t = now
            
        self.last_state = current_state
        return pressed

    def poll(self):
        time.sleep(self.poll_dt)
