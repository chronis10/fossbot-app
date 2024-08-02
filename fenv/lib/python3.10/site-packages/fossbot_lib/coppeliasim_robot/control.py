"""
Implementation of simulated control.
"""

import math
import time
from datetime import datetime
from fossbot_lib.common.interfaces import control_interfaces
from fossbot_lib.common.data_structures import configuration
from fossbot_lib.coppeliasim_robot import sim

# General Functions
def init_component(client_id: int, component_name: str) -> int:
    '''
    Initializes a component (like motors, sensors etc) of the simulation.
    Param: component_name: the name of the component (example: 'left_motor').
    Returns: the component in the simulation.
    '''
    _, component = sim.simxGetObjectHandle(client_id, component_name, sim.simx_opmode_blocking)
    return component


def exec_vrep_script(client_id: int, script_component_name: str, script_function_name: str,
                     in_ints: list = [], in_floats: list = [], in_strings: list = [],
                     in_buffer: bytearray = bytearray()) -> tuple:
    '''
    Executes a function of a lua script in vrep.
    Param: client_id: the client's id.
           script_component_name: the name of the object that has the script in the scene.
           script_function_name: the name of the function inside the script to be executed.
           in_ints: list of input integers used for the function (can be [ ]).
           in_floats: list of input floats used for the function (can be [ ]).
           in_strings: list of input strings used for the function (can be [ ]).
           in_buffer: input bytearray used for the function.
    Returns: returnCode: to show if function has been executed correctly
             => (successful execution: sim.simx_return_ok).
             out_ints: list of integer values returned by the function.
             out_floats: list of float values returned by the function.
             out_strings: list of string values returned by the function.
             out_buffer: bytearray returned by the function.
    '''
    # print(f'Called {script_component_name}/{script_function_name}')
    return sim.simxCallScriptFunction(
        client_id, script_component_name, sim.sim_scripttype_childscript,
        script_function_name, in_ints, in_floats, in_strings, in_buffer,
        sim.simx_opmode_blocking)


def get_object_children(client_id: int, object_name: str = '/', print_all=False) -> tuple:
    '''
    Retrieves handles of all the children of an object.
    Default object_name: '/': retrieves all the objects handles in the scene.
    Recommended object_name: 'fossbot': retrieves all children of fossbot.
    Param: client_id: the client id.
           object_name: the object's name in the scene.
           print_all: prints all the handles and their corresponding object's path in the scene.
    Returns: object_children_list: a list of all the childrens handles of the requested object.
             object_children_dict: a dictionary with keys the handles and values the
                                   corresponding path in the scene of the requested object.
    '''
    sim.simxGetObjectGroupData(client_id, sim.sim_appobj_object_type, 21, sim.simx_opmode_streaming)
    time.sleep(0.1)
    _, handle, _, _, name = sim.simxGetObjectGroupData(
        client_id, sim.sim_appobj_object_type,
        21, sim.simx_opmode_blocking)

    object_children_list = []
    object_children_dict = {}

    if not object_name.startswith('/'):
        object_name = '/' + object_name

    for tmp_h in handle:
        if print_all:
            print(f'Handle: {tmp_h}, Path: {name[tmp_h]}')
        if object_name in name[tmp_h]:
            object_children_list.append(tmp_h)
            object_children_dict[tmp_h] = name[tmp_h]

    if len(object_children_list) == 0:
        print(f'There is no robot named {object_name[1:]} in scene.')
        raise ModuleNotFoundError

    return object_children_list, object_children_dict


class Timer(control_interfaces.TimerInterface):
    '''
    Class timer()
    Functions:
    stop_timer() Stops a timer.
    start_timer() Starts a timer.
    elapsed() Prints elapsed time from start.
    get_elapsed() Returns the elapsed time between start time and that moment in sec.
    '''
    def __init__(self):
        self.start = 0

    def stop_timer(self) -> None:
        '''Stops timer.'''
        self.start = 0

    def start_timer(self) -> None:
        '''Starts timer.'''
        self.start = datetime.now()

    def elapsed(self) -> None:
        '''Prints elapsed time from start.'''
        if self.start == 0:
            print("Timer not started")
        else:
            dif = datetime.now() - self.start
            print(f'The elapsed time in sec is {dif}')

    def get_elapsed(self) -> int:
        '''Returns the elapsed time in seconds.'''
        if self.start == 0:
            return 0
        else:
            format_data = "%d/%m/%y %H:%M:%S"
            start_time = datetime.strptime(self.start.strftime(format_data), format_data)
            now_time = datetime.now().strftime(format_data)
            now_time = datetime.strptime(now_time, format_data)
            elapsed = now_time - start_time
            elapsed = elapsed.total_seconds()
            elapsed = int(elapsed)
            return elapsed


class Motor(control_interfaces.MotorInterface):
    """
    Motor(sim_param,motor_joint_name,def_speed) -> Motor control.
    Functions:
    dir_control(direction) Change motor direction to input direction.
    move(direction) Start moving motor with default speed towards input direction.
    set_speed(speed) Set speed immediately 0-100 range.
    stop() Stops the motor.
    """
    def __init__(self, sim_param: configuration.SimRobotParameters, motor_joint_name: str, def_speed: int) -> None:
        self.client_id = sim_param.simulation.client_id
        self.param = sim_param
        self.motor_name = motor_joint_name
        self.def_speed = def_speed
        self.direction = 'forward'

    def __change_motor_velocity(self, velocity: float) -> int:
        '''
        Changes a motor's velocity.
        Param: motor: the motor of the simulation to change its velocity (example 'left_motor').
               velocity: the velocity to be changed to.
        Returns: a return code of the API function.
        '''
        while True:
            res, _, _, _, _ = exec_vrep_script(
                self.client_id, self.motor_name,
                'change_vel', in_floats=[velocity])
            if res == sim.simx_return_ok:
                return res

    def dir_control(self, direction: str) -> None:
        '''
        Change motor direction to input direction.
        Param: direction: the direction to be headed to.
        '''
        if direction not in ['forward', 'reverse']:
            print("Motor accepts only forward and reverse values")
        else:
            self.direction = direction

    def move(self, direction: str = "forward") -> None:
        '''
        Start moving motor with default speed towards input direction.
        Param: direction: the direction to be headed to.
        '''
        if direction == 'forward':
            self.dir_control(direction)
            self.__change_motor_velocity(-self.def_speed)
        elif direction == "reverse":
            self.dir_control(direction)
            self.__change_motor_velocity(self.def_speed)
        else:
            print("Motor accepts only forward and reverse values")

    def set_speed(self, speed: int) -> None:
        '''
        Set speed immediately 0-100 range.
        Param: speed: the range 0 - 100 that speed will be changed to.
        '''
        if speed < 0 or speed > 100:
            print("The motor speed is a percentage of total motor power. Accepted values 0-100.")
        else:
            self.def_speed = speed / 100
            self.move(self.direction)

    def stop(self) -> None:
        '''Stops the motor.'''
        self.__change_motor_velocity(0)


class Odometer(control_interfaces.OdometerInterface):
    '''
    Class Odometer(sim_param, motor_name) -> Odometer control.
    Functions:
    count_revolutions() Increases the counter of revolutions.
    get_revolutions() Returns the number of revolutions.
    get_distance() Returns the traveled distance in cm.
    reset() Resets the steps counter.
    '''
    def __init__(self, sim_param: configuration.SimRobotParameters, motor_name: str) -> None:
        self.sensor_disc = 20   #by default 20 lines sensor disc
        self.steps = 0
        self.wheel_diameter = 6.65  #by default the wheel diameter is 6.6
        self.precision = 2  #by default the distance is rounded in 2 digits
        self.client_id = sim_param.simulation.client_id
        self.param = sim_param
        self.motor_name = motor_name

    def count_revolutions(self) -> None:
        '''Increase total steps by one.'''
        while True:
            res, steps, _, _, _ = exec_vrep_script(
                self.client_id, self.motor_name,
                'count_revolutions')
            if res == sim.simx_return_ok and len(steps)>=1:
                self.steps = steps[0]
                break

    def get_steps(self) -> int:
        ''' Returns total number of steps. '''
        while True:
            res, steps, _, _, _ = exec_vrep_script(self.client_id, self.motor_name, 'get_steps')
            if res == sim.simx_return_ok and len(steps)>=1:
                self.steps = steps[0]
                return self.steps

    def get_revolutions(self) -> float:
        ''' Returns total number of revolutions. '''
        self.steps = self.get_steps()
        return self.steps / self.sensor_disc

    def __print_distance(self, distance) -> None:
        ''' Prints distance traveled (used for debugging). '''
        if self.motor_name == self.param.simulation.right_motor_name:
            print(f'Distance: {distance}')

    def get_distance(self) -> float:
        ''' Return the total distance traveled so far (in cm). '''
        self.steps = self.get_steps()
        circumference = self.wheel_diameter * math.pi
        revolutions = self.steps / self.sensor_disc
        distance = revolutions * circumference
        #self.__print_distance(distance) # used only for debugging
        return round(distance, self.precision)

    def reset(self) -> None:
        ''' Reset the total traveled distance and revolutions. '''
        while True:
            res, _, _, _, _ = exec_vrep_script(self.client_id, self.motor_name, 'reset_steps')
            if res == sim.simx_return_ok:
                break
        self.steps = 0

class UltrasonicSensor(control_interfaces.UltrasonicSensorInterface):
    '''
    Class UltrasonicSensor(sim_param) -> Ultrasonic sensor control.
    Functions:
    get_distance() return distance in cm.
    '''
    def __init__(self, sim_param: configuration.SimRobotParameters) -> None:
        self.client_id = sim_param.simulation.client_id
        self.param = sim_param
        self.precision = 2  #by default the distance is rounded in 2 digits

    def get_distance(self) -> float:
        '''
        Gets the distance to the closest obstacle.
        Returns: the distance to the closest obstacle (in cm).
        If no obstacle detected => returns 999.9
        '''
        max_dist = 999.9
        ultrasonic_name = self.param.simulation.ultrasonic_name
        while True:
            res, handle, distance, _, _ = exec_vrep_script(
                self.client_id, ultrasonic_name,
                'get_distance')
            if res == sim.simx_return_ok and len(distance)>=1:
                break
        #Detected Handle: handle[0], Distance (in meters): distance[0]
        if distance[0] >= 1:
            return max_dist
        return round(distance[0]*100, self.precision)

class Accelerometer(control_interfaces.AccelerometerInterface):
    '''
    Class Accelerometer(sim_param) -> Handles accelerometer and gyroscope.
    Functions:
    get_acceleration(dimension) Returns the acceleration for a specific dimension.
    get_gyro(dimension) Returns the gyroscope for a specific dimension.
    '''
    def __init__(self, sim_param: configuration.SimRobotParameters) -> None:
        self.client_id = sim_param.simulation.client_id
        self.param = sim_param

    def __create_force_dict(self, force_list: list) -> dict:
        '''
        Creates dictionary out of list of x, y, z forces.
        Param: force_list: the list of x, y, z forces.
        Returns: the dictionary of x, y, z forces.
        '''
        return {'x': force_list[0], 'y': force_list[1], 'z': force_list[2]}

    def get_acceleration(self, dimension: str) -> float:
        '''
        Gets the acceleration for a specific dimension.
        Param: dimension: the dimension requested.
        Returns: the acceleration for a specific dimension.
        '''
        accel_name = self.param.simulation.accelerometer_name
        while True:
            # res_1 -> function executed correctly
            # res_2 -> data was successfully collected
            res_1, res_2, accel_data, _, _ = exec_vrep_script(
                self.client_id, accel_name, 'get_accel')
            if res_1 == sim.simx_return_ok and len(accel_data) == 3 and len(res_2)>=1 and res_2[0] == sim.simx_return_ok:
                break
        accel_data = self.__create_force_dict(accel_data)
        if dimension in ('x', 'y', 'z'):
            return accel_data[dimension]
        print("Dimension not recognized!!")
        return 0.0

    def get_gyro(self, dimension: str) -> float:
        '''
        Gets gyroscope for a specific dimension.
        Param: dimension: the dimension requested.
        Returns: the gyroscope for a specific dimension.
        '''
        gyro_name = self.param.simulation.gyroscope_name
        while True:
            res, _, gyro_data, _, _ = exec_vrep_script(self.client_id, gyro_name, 'get_gyro')
            if res == sim.simx_return_ok and len(gyro_data) == 3:
                break
        gyro_data = self.__create_force_dict(gyro_data)
        if dimension in ('x', 'y', 'z'):
            return gyro_data[dimension]
        print("Dimension not recognized!!")
        return 0.0


class AnalogueReadings(control_interfaces.AnalogueReadingsInterface):
    '''
    Class AnalogueReadings(sim_param) -> Handles Analogue Readings.
    Functions:
    get_reading(pin) Gets reading of a specific sensor specified by input pin.
    '''
    def __init__(self, sim_param: configuration.SimRobotParameters) -> None:
        self.client_id = sim_param.simulation.client_id
        self.param = sim_param

    def __get_line_data(self, line_sensor_name: str) -> float:
        '''
        Retrieves image data of requested line sensor.
        Param: line_sensor_name: the name of the wanted line sensor.
        Returns: image data of requested line_sensor.
        '''
        while True:
            res, _, image, _, _ = exec_vrep_script(
                self.client_id, line_sensor_name,
                'get_color')
            if res == sim.simx_return_ok and len(image)>=1:
                return image[0]

    def __get_light_data(self) -> float:
        '''
        Returns light opacity from light sensor.
        '''
        light_sensor = self.param.simulation.light_sensor_name
        while True:
            res, _, light_opacity, _, _ = exec_vrep_script(
                self.client_id, light_sensor, 'get_light')
            if res == sim.simx_return_ok and len(light_opacity)>=1:
                return light_opacity[0]

    def get_reading(self, pin: int) -> float:
        '''
        Gets reading of a specific sensor specified by input pin.
        Param: pin: the pin of the sensor.
        Returns: the reading of the requested sensor.
        '''
        if pin == self.param.simulation.light_sensor_id:
            return self.__get_light_data()
        if pin == self.param.simulation.sensor_middle_id:
            mid_sensor_name = self.param.simulation.sensor_middle_name
            return self.__get_line_data(mid_sensor_name)
        if pin == self.param.simulation.sensor_right_id:
            right_sensor_name = self.param.simulation.sensor_right_name
            return self.__get_line_data(right_sensor_name)
        if pin == self.param.simulation.sensor_left_id:
            left_sensor_name = self.param.simulation.sensor_left_name
            return self.__get_line_data(left_sensor_name)


class Noise(control_interfaces.NoiseInterface):
    '''
    Class Noise() -> Handles Noise Detection.
    Functions:
    detect_noise() Returns True only if noise is detected.
    '''
    def __init__(self, sim_param: configuration.SimRobotParameters) -> None:
        self.client_id = sim_param.simulation.client_id
        self.gui_name = sim_param.simulation.foss_gui

    def detect_noise(self) -> bool:
        '''
        Returns True only if noise was detected.
        '''
        for i in range(10):
            res, noise_made, _, _, _ = exec_vrep_script(self.client_id, self.gui_name, 'get_noise_gui')
            if res == sim.simx_return_ok and len(noise_made) >= 1:
                return bool(noise_made[0])
        return False

# Hardware section
class GenInput(control_interfaces.GenInputInterface):
    '''
    Class GenInput(pin).
    Default pin 4.
    Functions:
    get_state(): Returns state 0 or 1.
    '''
    def get_state(self) -> int:
        '''
        Returns state 0 or 1
        '''
        raise NotImplementedError

class GenOutput(control_interfaces.GenOutputInterface):
    '''
    Class GenOutput(pin).
    Deafult pin 5.
    Functions:
    set_on() set High the output pin.
    set_off() set Low the output pin.
    '''
    def set_on(self) -> None:
        '''
        Set High the output pin
        '''
        raise NotImplementedError

    def set_off(self) -> None:
        '''
        Set Low the output pin
        '''
        raise NotImplementedError


class LedRGB(control_interfaces.LedRGBInterface):
    '''
    Class LedRGB(sim_param) -> Led control.
    Functions:
    set_on(color): sets led to input color.
    '''
    def __init__(self, sim_param: configuration.SimRobotParameters) -> None:
        self.client_id = sim_param.simulation.client_id
        self.param = sim_param

    def set_on(self, color: str) -> None:
        '''
        Changes the color of a led.
        Param: color: the wanted color.
        For closing the led, use color == 'closed'.
        '''
        color_rbg = [0, 0, 0]   #red, blue, green
        if color == 'red':
            color_rbg = [1, 0, 0]
        elif color == 'green':
            color_rbg = [0, 1, 0]
        elif color == 'blue':
            color_rbg = [0, 0, 1]
        elif color == 'white':
            color_rbg = [1, 1, 1]
        elif color == 'violet':
            color_rbg = [1, 1, 0]
        elif color == 'cyan':
            color_rbg = [0, 1, 1]
        elif color == 'yellow':
            color_rbg = [1, 0, 1]
        elif color == 'closed':
            color_rbg = [0, 0, 0]
        else:
            print('Uknown color!')
            raise RuntimeError

        led_name = self.param.simulation.led_name
        while True:
            res, _, _, _, _ = exec_vrep_script(
                                self.client_id, led_name,
                                'set_color_led', in_floats=color_rbg)
            if res == sim.simx_return_ok:
                break
