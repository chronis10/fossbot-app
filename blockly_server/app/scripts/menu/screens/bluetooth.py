import threading
from ..screen import Screen
from .. import utils
from .bluetooth_device import BluetoothDeviceScreen

class BluetoothScreen(Screen):
    def __init__(self, robot, screen_manager):
        super().__init__(robot, screen_manager)
        self.devices = []
        self.selected_index = 0
        self.loading = True
        self.message = ""

    def show(self):
        self.loading = True
        self.update()
        threading.Thread(target=self.load_devices, daemon=True).start()

    def load_devices(self):
        self.message = "Scanning (10s)..."
        self.update()
        self.devices = utils.scan_bluetooth_devices(scan_time=10)
        self.loading = False
        self.message = ""
        self.update()

    def update(self):
        header = "Bluetooth"
        if self.loading:
            self.robot.screen.text_lines([header, self.message, "", "<- Back"], line_h=16)
            return

        if not self.devices:
            self.robot.screen.text_lines([header, "No devices found", "", "<- Back"], line_h=16)
            return

        idx = max(0, min(self.selected_index, len(self.devices) - 1))
        page_size = 2
        page_start = (idx // page_size) * page_size

        def fmt(i):
            if i >= len(self.devices):
                return ""
            dev = self.devices[i]
            name = dev["name"][:14]
            pfx = ">" if i == idx else " "
            return f"{pfx} {name}"

        line2 = fmt(page_start)
        line3 = fmt(page_start + 1)
        self.robot.screen.text_lines([header, line2, line3, "BT3 Sel BT4 Back"], line_h=16)

    def handle_input(self, pressed_buttons):
        if self.loading:
            if pressed_buttons.get("bt4"):
                self.robot.buzzer.play([(600, 0.08)])
                self.screen_manager.pop_screen()
            return

        if pressed_buttons.get("bt1"):
            self.robot.buzzer.play([(600, 0.08)])
            self.selected_index = (self.selected_index - 1) % len(self.devices)
            self.update()
        elif pressed_buttons.get("bt2"):
            self.robot.buzzer.play([(600, 0.08)])
            self.selected_index = (self.selected_index + 1) % len(self.devices)
            self.update()
        elif pressed_buttons.get("bt3"):
            if not self.devices:
                self.robot.buzzer.play([(900, 0.06)])
                return
            self.robot.buzzer.play([(600, 0.08)])
            selected_device = self.devices[self.selected_index]
            self.screen_manager.push_screen(BluetoothDeviceScreen(self.robot, self.screen_manager, selected_device))
        elif pressed_buttons.get("bt4"):
            self.robot.buzzer.play([(600, 0.08)])
            self.screen_manager.pop_screen()
