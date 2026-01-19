import os
import signal
import time
from fossbot_lib.real_robot.fossbot import FossBot
from menu.utils import exit_when_parent_dies, BatteryMonitor
from menu.input import Input
from menu.screen_manager import ScreenManager
from menu.screens.main import MainMenuScreen

def main():
    exit_when_parent_dies()

    robot = FossBot()
    batt = BatteryMonitor(robot)
    input_handler = Input(robot)
    
    initial_screen = MainMenuScreen(robot, None, batt)
    screen_manager = ScreenManager(initial_screen)
    initial_screen.screen_manager = screen_manager

    def _cleanup_and_exit(signum, frame):
        try:
            batt.stop()
        except Exception:
            pass
        try:
            robot.screen.text_lines(["", "", "", ""], line_h=16)
        except Exception:
            pass
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _cleanup_and_exit)
    signal.signal(signal.SIGINT, _cleanup_and_exit)

    last_info_refresh_t = 0.0
    INFO_REFRESH_S = 0.5
    
    initial_screen.show()

    while True:
        # Input handling
        pressed_buttons = input_handler.get_pressed_buttons()
        if pressed_buttons:
            screen_manager.handle_input(pressed_buttons)

        # Periodic update
        now = time.monotonic()
        if (now - last_info_refresh_t) >= INFO_REFRESH_S:
            screen_manager.update()
            last_info_refresh_t = now

        input_handler.poll()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            r = FossBot()
            r.screen.text_lines(["", "", "", ""], line_h=16)
        except Exception:
            pass
    except SystemExit:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")
        try:
            r = FossBot()
            r.screen.text_lines(["Menu Error!", "", str(e)[:20], ""], line_h=16)
        except Exception:
            pass