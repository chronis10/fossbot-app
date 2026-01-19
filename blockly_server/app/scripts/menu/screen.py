class Screen:
    def __init__(self, robot, screen_manager):
        self.robot = robot
        self.screen_manager = screen_manager

    def show(self):
        # This method should be implemented by each screen to display its content
        pass

    def update(self):
        # This method is for periodic updates on the screen
        pass

    def handle_input(self, pressed_buttons):
        # This method should be implemented by each screen to handle button presses
        pass
