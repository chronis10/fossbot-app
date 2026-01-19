from ..screen import Screen

class BatteryScreen(Screen):
    def __init__(self, robot, screen_manager, battery_monitor):
        super().__init__(robot, screen_manager)
        self.battery_monitor = battery_monitor

    def show(self):
        self.update()

    def update(self):
        info = self.battery_monitor.get()
        v = info.get("v")
        pct = info.get("pct")

        if v is None or pct is None:
            line2 = "Voltage: --.-V"
            line3 = "Level: --%"
        else:
            line2 = f"Voltage: {v:.2f}V"
            line3 = f"Level: {pct:.0f}%"

        self.robot.screen.text_lines(["Battery", line2[:16], line3[:16], " <- Back"], line_h=16)

    def handle_input(self, pressed_buttons):
        if pressed_buttons.get("bt4"):
            self.robot.buzzer.play([(600, 0.08)])
            self.screen_manager.pop_screen()
        elif any(pressed_buttons.values()):
            self.robot.buzzer.play([(600, 0.08)])
