from ..screen import Screen
from .. import utils

class NetworkScreen(Screen):
    def __init__(self, robot, screen_manager):
        super().__init__(robot, screen_manager)
        self.ssid = ""
        self.ip = ""

    def show(self):
        self.update_info()
        self.update()

    def update_info(self):
        self.ssid = utils.get_wifi_ssid()
        self.ip = utils.get_ip_address()

    def update(self):
        self.robot.screen.text_lines(
            ["Network", f"SSID: {self.ssid}", f"IP: {self.ip}", " <- Back"],
            line_h=16
        )

    def handle_input(self, pressed_buttons):
        if pressed_buttons.get("bt4"):
            self.robot.buzzer.play([(600, 0.08)])
            self.screen_manager.pop_screen()
        elif any(pressed_buttons.values()):
            self.robot.buzzer.play([(600, 0.08)])
