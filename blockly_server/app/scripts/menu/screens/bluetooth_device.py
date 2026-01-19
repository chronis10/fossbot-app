from ..screen import Screen
from .. import utils
from .remote_control import RemoteControlScreen

class BluetoothDeviceScreen(Screen):
    def __init__(self, robot, screen_manager, device):
        super().__init__(robot, screen_manager)
        self.device = device
        self.menu_items = ["Pair", "Connect", "Trust"]
        self.current_item = 0
        self.message = ""

    def show(self):
        self.update()

    def update(self):
        device_name = self.device['name']
        
        lines = [f"{device_name[:16]}", ""]

        for i, item in enumerate(self.menu_items):
            prefix = ">" if i == self.current_item else " "
            lines.append(f"{prefix} {item}")
        
        if self.message:
            lines[-1] = self.message[:16]

        self.robot.screen.text_lines(lines, line_h=16)

    def handle_input(self, pressed_buttons):
        if pressed_buttons.get("bt1"):
            self.robot.buzzer.play([(600, 0.08)])
            self.current_item = (self.current_item - 1) % len(self.menu_items)
            self.message = ""
            self.update()
        elif pressed_buttons.get("bt2"):
            self.robot.buzzer.play([(600, 0.08)])
            self.current_item = (self.current_item + 1) % len(self.menu_items)
            self.message = ""
            self.update()
        elif pressed_buttons.get("bt3"):
            self.robot.buzzer.play([(600, 0.08)])
            selected = self.menu_items[self.current_item]
            mac = self.device['mac']
            
            self.message = f"{selected}ing..."
            self.update()

            ok, msg = False, "Not impl"
            
            if selected == "Pair":
                ok, msg = utils.pair_device(mac)
            elif selected == "Connect":
                ok, msg = utils.connect_device(mac)
                if ok:
                    self.screen_manager.push_screen(RemoteControlScreen(self.robot, self.screen_manager, self.device))
                    return
            elif selected == "Trust":
                ok, msg = utils.trust_device(mac)
            
            self.message = msg
            self.update()

        elif pressed_buttons.get("bt4"):
            self.robot.buzzer.play([(600, 0.08)])
            self.screen_manager.pop_screen()
