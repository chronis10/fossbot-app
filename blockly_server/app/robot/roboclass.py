import socketio
from fossbot_lib.parameters_parser.parser import load_parameters
from fossbot_lib.common.data_structures import configuration
from fossbot_lib.common.interfaces import robot_interface
from config import Config

if Config.ROBOT_MODE == 'physical':
    from fossbot_lib.real_robot.fossbot import FossBot
else:
    from fossbot_lib.coppeliasim_robot.fossbot import FossBot


class Communication():
    def __init__(self,namespace='/test'):
        self.namespace = namespace
        self.sio = socketio.Client()
        self.sio.connect(f'http://{Config.BROWSER_HOST}:{Config.PORT}')
        self.start_event_handlers()

    def start_event_handlers(self):
        self.sio.on('connect', self.connect, namespace=self.namespace)
        self.sio.on('connect_error', self.connect_error, namespace=self.namespace)
        self.sio.on('disconnect', self.disconnect, namespace=self.namespace)

    def transmit(self,message):
        self.sio.emit('terminal_msgs', {'data': message})
    
    def connect(self):
        print("I'm connected!")

    def connect_error(self,data):
        print("The connection failed!")

    def disconnect(self):
        print("I'm disconnected!")

 
class Agent():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Agent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.parameters = None

    def load_parameters(self):
        file_params = load_parameters(path=Config.ADMIN_PARAMS)
        common_params = {
            "sensor_distance": configuration.SensorDistance(**file_params["sensor_distance"]),
            "motor_left_speed": configuration.MotorLeftSpeed(**file_params["motor_left"]),
            "motor_right_speed": configuration.MotorRightSpeed(**file_params["motor_right"]),
            "default_step": configuration.DefaultStep(**file_params["step"]),
            "light_sensor": configuration.LightSensor(**file_params["light_sensor"]),
            "line_sensor_left": configuration.LineSensorLeft(**file_params["line_sensor_left"]),
            "line_sensor_center": configuration.LineSensorCenter(**file_params["line_sensor_center"]),
            "line_sensor_right": configuration.LineSensorRight(**file_params["line_sensor_right"]),
            "rotate_90": configuration.Rotate90(**file_params["rotate_90"])
        }

        if Config.ROBOT_MODE == 'coppelia':
            simulation_ids = configuration.SimRobotIds(**file_params["simulator_ids"])
            return configuration.SimRobotParameters(simulation=simulation_ids, **common_params)
        else:
            return configuration.RobotParameters(**common_params)
    

    def execute(self,code):
        parameters = self.load_parameters()
        robot = FossBot(parameters=parameters)      
        if Config.ROBOT_MODE != 'coppelia':
            param = load_parameters(path=Config.ADMIN_PARAMS)
            robot.rgb_led.anode = param['rgb_led_type']["value"]
        coms = Communication()
        transmit = coms.transmit
        exec(code)
        robot.exit()
    
    def stop(self):
        pass
     

if __name__ == '__main__':
    a = Agent()
    a.execute('print("hello")')
    a.reset()
    


