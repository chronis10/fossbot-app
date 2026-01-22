import time
from fossbot_lib.real_robot.fossbot import FossBot
from ..screen import Screen

def _test_accelerometer_gyroscope(robot: FossBot) -> None:
    robot.screen.text_lines(["Accelerometer", "& Gyroscope", "Press bt4 to exit"], line_h=16)
    while not robot.bt4.is_pressed():
        accel = robot.get_acceleration("x"), robot.get_acceleration("y"), robot.get_acceleration("z")
        gyro = robot.get_gyroscope("x"), robot.get_gyroscope("y"), robot.get_gyroscope("z")
        robot.screen.text_lines([
            f"Accel: {accel[0]:.2f} {accel[1]:.2f} {accel[2]:.2f}",
            f"Gyro: {gyro[0]:.2f} {gyro[1]:.2f} {gyro[2]:.2f}",
            "",
            "Press bt4 to exit"
        ], line_h=16)
        time.sleep(0.1)

def _test_motors(robot: FossBot) -> None:
    for motor_name in ["motor_left", "motor_right"]:
        for direction in ["forward", "reverse"]:
            robot.screen.text_lines([f"Test {motor_name}", f"Direction: {direction}", "Press bt4 to stop"], line_h=16)
            motor = getattr(robot, motor_name)
            motor.move(direction=direction)
            while not robot.bt4.is_pressed():
                time.sleep(0.1)
            motor.stop()
            time.sleep(0.5)

def _test_light_sensor(robot: FossBot) -> None:
    robot.screen.text_lines(["Light Sensor", "Press bt4 to exit"], line_h=16)
    while not robot.bt4.is_pressed():
        light_value = robot.get_light_sensor()
        robot.screen.text_lines([f"Light: {light_value}", "", "", "Press bt4 to exit"], line_h=16)
        time.sleep(0.1)

def _test_power_sensor(robot: FossBot) -> None:
    robot.screen.text_lines(["Power Sensor", "Press bt4 to exit"], line_h=16)
    while not robot.bt4.is_pressed():
        power_value = robot.get_power_sensor()
        robot.screen.text_lines([f"Power: {power_value}", "", "", "Press bt4 to exit"], line_h=16)
        time.sleep(0.1)

def _test_line_sensors(robot: FossBot) -> None:
    robot.screen.text_lines(["Line Sensors", "Press bt4 to exit"], line_h=16)
    while not robot.bt4.is_pressed():
        left = robot.get_floor_sensor(3)
        center = robot.get_floor_sensor(1)
        right = robot.get_floor_sensor(2)
        robot.screen.text_lines([f"Left: {left}", f"Center: {center}", f"Right: {right}", "Press bt4 to exit"], line_h=16)
        time.sleep(0.1)

def _test_obstacle_sensors(robot: FossBot) -> None:
    robot.screen.text_lines(["Obstacle Sensors", "Press bt4 to exit"], line_h=16)
    while not robot.bt4.is_pressed():
        front_left = robot.get_obstacle_sensor(0)
        front_right = robot.get_obstacle_sensor(1)
        back_left = robot.get_obstacle_sensor(2)
        back_right = robot.get_obstacle_sensor(3)
        robot.screen.text_lines([f"FL: {front_left} FR: {front_right}", f"BL: {back_left} BR: {back_right}", "", "Press bt4 to exit"], line_h=16)
        time.sleep(0.1)

def _test_rgb_led(robot: FossBot) -> None:
    for color in ["red", "green", "blue"]:
        robot.screen.text_lines(["RGB LED Test", f"Color: {color}", "Press bt4 to next"], line_h=16)
        robot.rgb_set_color(color)
        while not robot.bt4.is_pressed():
            time.sleep(0.1)
        robot.rgb_set_color("off")
        time.sleep(0.5)

def _test_odometers(robot: FossBot) -> None:
    robot.screen.text_lines(["Odometers Test", "Press bt4 to exit"], line_h=16)
    while not robot.bt4.is_pressed():
        left = robot.odometer_left.get_distance()
        right = robot.odometer_right.get_distance()
        robot.screen.text_lines([f"Left: {left:.2f} cm", f"Right: {right:.2f} cm", "", "Press bt4 to exit"], line_h=16)
        time.sleep(0.1)

def _test_ultrasonic_sensor(robot: FossBot) -> None:
    robot.screen.text_lines(["Ultrasonic Sensor", "Press bt4 to exit"], line_h=16)
    while not robot.bt4.is_pressed():
        distance = robot.get_distance()
        robot.screen.text_lines([f"Distance: {distance:.2f} cm", "", "", "Press bt4 to exit"], line_h=16)
        time.sleep(0.1)

def _test_noise_sensor(robot: FossBot) -> None:
    robot.screen.text_lines(["Noise Sensor", "Press bt4 to exit"], line_h=16)
    while not robot.bt4.is_pressed():
        noise = robot.get_noise_detection()
        robot.screen.text_lines([f"Noise detected: {noise}", "", "", "Press bt4 to exit"], line_h=16)
        time.sleep(0.1)

class DiagnosticsScreen(Screen):
    DIAGNOSTICS_MENU = [
        ("Accelerometer", _test_accelerometer_gyroscope),
        ("Motors", _test_motors),
        ("Light Sensor", _test_light_sensor),
        ("Line Sensors", _test_line_sensors),
        ("RGB LED", _test_rgb_led),
        ("Odometers", _test_odometers),
        ("Ultrasonic", _test_ultrasonic_sensor),
        ("Noise Sensor", _test_noise_sensor),
        ("Power Sensor", _test_power_sensor),
        ("Obstacle Sens", _test_obstacle_sensors),
    ]

    def __init__(self, robot, screen_manager):
        super().__init__(robot, screen_manager)
        self.selected_idx = 0
        self.menu_view_start_idx = 0

    def show(self):
        self._show_menu()

    def _show_menu(self):
        menu_len = len(self.DIAGNOSTICS_MENU)
        max_start = max(0, menu_len - 4)

        if self.selected_idx < self.menu_view_start_idx:
            self.menu_view_start_idx = self.selected_idx
        elif self.selected_idx > self.menu_view_start_idx + 3:
            self.menu_view_start_idx = self.selected_idx - 3

        self.menu_view_start_idx = max(0, min(self.menu_view_start_idx, max_start))

        lines = []
        for i in range(self.menu_view_start_idx, min(menu_len, self.menu_view_start_idx + 4)):
            prefix = "> " if i == self.selected_idx else "  "
            lines.append(f"{prefix}{self.DIAGNOSTICS_MENU[i][0]}")
        self.robot.screen.text_lines(lines, line_h=16)

    def handle_input(self, pressed_buttons):
        if pressed_buttons.get("bt1"):  # Up
            self.robot.buzzer.play([(600, 0.08)])
            self.selected_idx = (self.selected_idx - 1) % len(self.DIAGNOSTICS_MENU)
            self._show_menu()
        elif pressed_buttons.get("bt2"):  # Down
            self.robot.buzzer.play([(600, 0.08)])
            self.selected_idx = (self.selected_idx + 1) % len(self.DIAGNOSTICS_MENU)
            self._show_menu()
        elif pressed_buttons.get("bt3"):  # Select
            self.robot.buzzer.play([(600, 0.08)])
            test_name, test_func = self.DIAGNOSTICS_MENU[self.selected_idx]
            self.robot.screen.text_lines([f"Running:", f"{test_name}", "...", ""], line_h=16)
            time.sleep(1)
            test_func(self.robot)
            self.show()
        elif pressed_buttons.get("bt4"):  # Back
            self.robot.buzzer.play([(600, 0.08)])
            self.screen_manager.pop_screen()

    def update(self):
        pass
