from ..screen import Screen
import evdev
import threading
import time

class RemoteControlScreen(Screen):
    def __init__(self, robot, screen_manager, device):
        super().__init__(robot, screen_manager)
        self.device = device
        self.controller = None
        self.message = "Initializing..."
        self.running = False
        self.left_y = 0
        self.left_x = 0
        self.x_axis_info = None
        self.y_axis_info = None

    def show(self):
        self.running = True
        self.update()
        threading.Thread(target=self.find_device, daemon=True).start()
        threading.Thread(target=self.update_loop, daemon=True).start()

    def find_device(self):
        self.message = "Finding device..."
        self.update()
        time.sleep(2)  # Give time for device to be ready
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if self.device['name'] in device.name:
                self.controller = device
                self.message = "Controller found!"

                abs_capabilities = self.controller.capabilities().get(evdev.ecodes.EV_ABS, [])
                for code, info in abs_capabilities:
                    if code == evdev.ecodes.ABS_X:
                        self.x_axis_info = info
                        self.left_x = info.value
                    elif code == evdev.ecodes.ABS_Y:
                        self.y_axis_info = info
                        self.left_y = info.value

                self.update()
                threading.Thread(target=self.control_loop, daemon=True).start()
                return
        self.message = "Controller not found"
        self.update()

    def update_loop(self):
        while self.running:
            self.update_motors()
            self.update()
            time.sleep(0.05)

    def control_loop(self):
        try:
            for event in self.controller.read_loop():
                if not self.running:
                    break
                
                print(f"Event type: {event.type}, code: {event.code}, value: {event.value}")

                if event.type == evdev.ecodes.EV_ABS:
                    if event.code == evdev.ecodes.ABS_Y:
                        self.left_y = event.value
                    elif event.code == evdev.ecodes.ABS_X:
                        self.left_x = event.value
                
        except Exception as e:
            self.message = str(e)[:16]

    def update_motors(self):
        if not self.x_axis_info or not self.y_axis_info:
            return

        # Normalize to -1.0 to 1.0
        x_center = (self.x_axis_info.min + self.x_axis_info.max) / 2
        y_center = (self.y_axis_info.min + self.y_axis_info.max) / 2
        
        x_range = (self.x_axis_info.max - self.x_axis_info.min) / 2
        y_range = (self.y_axis_info.max - self.y_axis_info.min) / 2

        if x_range == 0: x_range = 1
        if y_range == 0: y_range = 1

        y = - (self.left_y - y_center) / y_range
        x = (self.left_x - x_center) / x_range

        x = x * 0.3 # Reduce turning speed

        # Simple mixing
        left_speed = y + x
        right_speed = y - x

        # Clamp to -1.0 to 1.0
        left_speed = max(-1.0, min(1.0, left_speed))
        right_speed = max(-1.0, min(1.0, right_speed))

        # Motor control
        # Left motor
        left_motor_speed_value = int(abs(left_speed) * 50)
        if hasattr(self.robot.motor_left, 'set_speed'):
            self.robot.motor_left.set_speed(left_motor_speed_value)
        
        if left_speed > 0.15: # Deadzone
            self.robot.motor_left.move(direction="forward")
        elif left_speed < -0.15:
            self.robot.motor_left.move(direction="reverse")
        else:
            self.robot.motor_left.stop()

        # Right motor
        right_motor_speed_value = int(abs(right_speed) * 50)
        if hasattr(self.robot.motor_right, 'set_speed'):
            self.robot.motor_right.set_speed(right_motor_speed_value)

        if right_speed > 0.15: # Deadzone
            self.robot.motor_right.move(direction="forward")
        elif right_speed < -0.15:
            self.robot.motor_right.move(direction="reverse")
        else:
            self.robot.motor_right.stop()

    def update(self):
        if not self.controller:
            self.robot.screen.text_lines(["Remote Control", self.message, "", "<- Back"], line_h=16)
            return

        line2 = f"X: {self.left_x}  Y: {self.left_y}"
        self.robot.screen.text_lines(["Remote Control", "Controller Ready", line2, "<- Back"], line_h=16)

    def handle_input(self, pressed_buttons):
        if pressed_buttons.get("bt4"):
            self.robot.buzzer.play([(600, 0.08)])
            self.running = False
            self.robot.motor_left.stop()
            self.robot.motor_right.stop()
            self.screen_manager.pop_screen()

