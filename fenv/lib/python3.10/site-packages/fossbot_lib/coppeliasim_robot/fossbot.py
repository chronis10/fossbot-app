"""
Simulated robot implementation.
"""

import time
import os
import pygame
from fossbot_lib.common.data_structures import configuration
from fossbot_lib.common.interfaces import robot_interface
from fossbot_lib.coppeliasim_robot import control

try:
    from fossbot_lib.coppeliasim_robot import sim
except FileNotFoundError:
    print('--------------------------------------------------------------')
    print('"sim.py" could not be imported. This means very probably that')
    print('either "sim.py" or the remoteApi library could not be found.')
    print('Make sure both are in the same folder as this file,')
    print('or appropriately adjust the file "sim.py"')
    print('--------------------------------------------------------------')
    print('')

class FossBot(robot_interface.FossBotInterface):
    """ Sim robot """
    def __init__(self, parameters: configuration.SimRobotParameters) -> None:
        self.client_id = self.__connect_vrep()
        if self.client_id == -1:
            print('Failed connecting to remote API server')
            raise ConnectionError
        print('Connected to remote API server')
        self.parameters = self.__load_fossbot_paths(parameters)
        self.parameters.simulation.client_id = self.client_id
        self.motor_left = control.Motor(
            self.parameters, self.parameters.simulation.left_motor_name,
            self.parameters.motor_left_speed.value / 100)
        self.motor_right = control.Motor(
            self.parameters, self.parameters.simulation.right_motor_name,
            self.parameters.motor_right_speed.value / 100)
        self.ultrasonic = control.UltrasonicSensor(self.parameters)
        self.odometer_right = control.Odometer(
            self.parameters, self.parameters.simulation.right_motor_name)
        self.odometer_left = control.Odometer(
            self.parameters, self.parameters.simulation.left_motor_name)
        self.analogue_reader = control.AnalogueReadings(self.parameters)
        self.accelerometer = control.Accelerometer(self.parameters)
        self.rgb_led = control.LedRGB(self.parameters)
        self.noise = control.Noise(self.parameters)
        self.timer = control.Timer()
        pygame.init()
        pygame.mixer.init()

    def __connect_vrep(self) -> int:
        '''
        Connects to Coppelia Server.
        Returns: the client's id.
        '''
        print('Program started')
        sim.simxFinish(-1) # just in case, close all opened connections
        return sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5) # Connect to CoppeliaSim

    def __load_fossbot_paths(
        self, parameters: configuration.SimRobotParameters) -> configuration.SimRobotParameters:
        '''
        Loads paramameters (paths) to match paths in scene.
        Param: parameters: the simulation parameters.
        Returns: the parameters match paths in scene.
        '''
        fossbot_name = parameters.simulation.fossbot_name
        body_name = parameters.simulation.body_name
        parameters.simulation.accelerometer_name = f'{fossbot_name}/{body_name}/{parameters.simulation.accelerometer_name}'
        parameters.simulation.left_motor_name = f'{fossbot_name}/{parameters.simulation.left_motor_name}'
        parameters.simulation.right_motor_name = f'{fossbot_name}/{parameters.simulation.right_motor_name}'
        parameters.simulation.light_sensor_name = f'{fossbot_name}/{body_name}/{parameters.simulation.light_sensor_name}'
        parameters.simulation.sensor_middle_name = f'{fossbot_name}/{parameters.simulation.sensor_middle_name}'
        parameters.simulation.sensor_right_name = f'{fossbot_name}/{parameters.simulation.sensor_right_name}'
        parameters.simulation.sensor_left_name = f'{fossbot_name}/{parameters.simulation.sensor_left_name}'
        parameters.simulation.ultrasonic_name = f'{fossbot_name}/{parameters.simulation.ultrasonic_shape}/{parameters.simulation.ultrasonic_name}'
        parameters.simulation.gyroscope_name = f'{fossbot_name}/{body_name}/{parameters.simulation.gyroscope_name}'
        parameters.simulation.led_name = f'{fossbot_name}/{body_name}/{parameters.simulation.led_name}'
        parameters.simulation.rot_name = f'{fossbot_name}/{body_name}/{parameters.simulation.rot_name}'
        parameters.simulation.body_name = f'{fossbot_name}/{parameters.simulation.body_name}'
        parameters.simulation.col_detector_name = f'{fossbot_name}/{body_name}/{parameters.simulation.col_detector_name}'
        return parameters

    # movement
    def just_move(self, direction: str = "forward") -> None:
        """
        Move forward/backwards.
        Param: direction: the direction to be headed to.
        """
        self.odometer_right.reset()
        self.odometer_left.reset()
        self.motor_right.move(direction=direction)
        self.motor_left.move(direction=direction)

    def move_distance(self, dist: float, direction: str = "forward") -> None:
        '''
        Moves to input direction (default == forward) a specified - input distance (cm).
        Param: dist: the distance to be moved (in cm).
               direction: the direction to be moved towards.
        '''
        if dist == 0:
            return
        self.just_move(direction=direction)
        dis_run_r = self.odometer_right.get_distance()
        dis_run_l = self.odometer_left.get_distance()
        while dis_run_r < dist and dis_run_l < dist:
            dis_run_r = self.odometer_right.get_distance()
            dis_run_l = self.odometer_left.get_distance()
        self.stop()

    def reset_dir(self) -> None:
        '''
        Resets all motors direction to default (forward).
        '''
        self.motor_left.dir_control("forward")
        self.motor_right.dir_control("forward")

    def stop(self) -> None:
        """ Stop moving. """
        self.motor_left.stop()
        self.motor_right.stop()
        #print('stop')
        self.odometer_right.reset()
        self.odometer_left.reset()

    def wait(self, time_s: int) -> None:
        '''
        Waits (sleeps) for an amount of time.
        Param: time_s: the time (seconds) of sleep.
        '''
        time.sleep(time_s)

    # moving forward
    def move_forward_distance(self, dist: float) -> None:
        '''
        Moves robot forward input distance.
        Param: dist: the distance (cm) to be moved by robot.
        '''
        self.move_distance(dist)

    def move_forward_default(self) -> None:
        '''
        Moves robot forward default distance.
        '''
        self.move_distance(self.parameters.default_step.value)

    def move_forward(self) -> None:
        '''
        Moves robot forwards.
        '''
        self.just_move()

    # moving reverse
    def move_reverse_distance(self, dist: float) -> None:
        '''
        Moves robot input distance in reverse.
        Param: dist: the distance (cm) to be moved by robot.
        '''
        self.move_distance(dist, direction="reverse")

    def move_reverse_default(self) -> None:
        '''
        Moves robot default distance in reverse.
        '''
        self.move_distance(self.parameters.default_step.value, direction="reverse")

    def move_reverse(self) -> None:
        '''
        Moves robot in reverse.
        '''
        self.just_move(direction="reverse")

    # rotation
    def just_rotate(self, dir_id: int) -> None:
        '''
        Rotates fossbot towards the specified dir_id.
        Param: dir_id: the direction id to rotate to:
                - counterclockwise: dir_id == 0
                - clockwise: dir_id == 1
        '''
        if dir_id not in [0, 1]:
            print('Uknown Direction!')
            raise RuntimeError
        self.odometer_right.reset()
        self.odometer_left.reset()
        left_dir = "forward" if dir_id == 1 else "reverse"
        right_dir = "forward" if dir_id == 0 else "reverse"
        self.motor_left.move(direction=left_dir)
        self.motor_right.move(direction=right_dir)

    def __get_degrees(self) -> float:
        '''Returns degrees of fossbot.'''
        while True:
            res, _, deg, _, _ = control.exec_vrep_script(self.client_id, self.parameters.simulation.rot_name, 'get_degrees')
            if res == sim.simx_return_ok and len(deg)>=1 and deg[0] != -1:
                return deg[0]

    def rotate_90(self, dir_id: int) -> None:
        '''
        Rotates fossbot 90 degrees towards the specified dir_id.
        Param: dir_id: the direction id to rotate 90 degrees:
                - counterclockwise: dir_id == 0
                - clockwise: dir_id == 1
        '''
        self.just_rotate(dir_id)
        rotations = self.parameters.rotate_90.value
        init = self.__get_degrees()
        d = 0
        tar_pos = 90 / max(rotations, 1)
        diff = abs(tar_pos - d)
        while diff >= 1.5:
            curr = self.__get_degrees()
            if dir_id == 1:
                if init > curr:
                    d = init - curr
                else:
                    n_init = 180 + init
                    n_cur = 180 - curr
                    d = n_init + n_cur
            elif dir_id == 0:
                if curr > init:
                    d = curr - init
                else:
                    n_init = 180 - init
                    n_cur = 180 + curr
                    d = n_init + n_cur
            else:
                raise RuntimeError
            diff = abs(tar_pos - d)
        self.stop()

    def rotate_clockwise(self) -> None:
        '''
        Rotates robot clockwise.
        '''
        self.just_rotate(1)

    def rotate_counterclockwise(self) -> None:
        '''
        Rotates robot counterclockwise.
        '''
        self.just_rotate(0)

    def rotate_clockwise_90(self) -> None:
        '''
        Rotates robot 90 degrees clockwise.
        '''
        self.rotate_90(1)

    def rotate_counterclockwise_90(self) -> None:
        '''
        Rotates robot 90 degrees counterclockwise.
        '''
        self.rotate_90(0)

    # ultrasonic sensor
    def get_distance(self) -> float:
        '''Returns distance of nearest obstacle in cm.'''
        return self.ultrasonic.get_distance()

    def check_for_obstacle(self) -> bool:
        '''Returns True only if an obstacle is detected.'''
        i = self.ultrasonic.get_distance()
        if i <= self.parameters.sensor_distance.value:
            return True
        return False

    # sound
    def play_sound(self, audio_path: str) -> None:
        '''
        Plays mp3 file specified by input audio_path.
        Param: audio_path: the path to the wanted mp3 file.
        '''
        audio_path = os.path.normpath(audio_path)
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    # floor sensors
    def get_floor_sensor(self, sensor_id: int) -> float:
        '''
        Gets reading of a floor - line sensor specified by sensor_id.
        Param: sensor_id: the id of the wanted floor - line sensor.
        Returns: the reading of input floor - line sensor.
        '''
        mid_id = self.parameters.simulation.sensor_middle_id
        left_id = self.parameters.simulation.sensor_left_id
        right_id = self.parameters.simulation.sensor_right_id
        if sensor_id not in [mid_id, left_id, right_id]:
            print(f'Sensor id {sensor_id} is out of bounds.')
            return 0.0
        return self.analogue_reader.get_reading(sensor_id)

    def check_on_line(self, sensor_id: int) -> bool:
        '''
        Checks if line sensor (specified by sensor_id) is on black line.
        Param: sensor_id: the id of the wanted floor - line sensor.
        Returns: True if sensor is on line, else False.
        '''
        mid_id = self.parameters.simulation.sensor_middle_id
        left_id = self.parameters.simulation.sensor_left_id
        right_id = self.parameters.simulation.sensor_right_id

        if sensor_id not in [mid_id, left_id, right_id]:
            print(f'Sensor id {sensor_id} is out of bounds.')
            return False

        read = self.analogue_reader.get_reading(sensor_id)
        #print(read)
        if sensor_id == mid_id:
            if read <= self.parameters.line_sensor_center.value / 100:
                return True
        elif sensor_id == left_id:
            if read <= self.parameters.line_sensor_left.value / 100:
                return True
        elif sensor_id == right_id:
            if read <= self.parameters.line_sensor_right.value / 100:
                return True
        return False

    # accelerometer
    def get_acceleration(self, axis: str) -> float:
        '''
        Gets acceleration of specified axis.
        Param: axis: the axis to get the acceleration from.
        Returns: the acceleration of specified axis.
        '''
        value = self.accelerometer.get_acceleration(dimension=axis)
        print(value)
        return value

    def get_gyroscope(self, axis: str) -> float:
        '''
        Gets gyroscope of specified axis.
        Param: axis: the axis to get the gyroscope from.
        Returns: the gyroscope of specified axis.
        '''
        value = self.accelerometer.get_gyro(dimension=axis)
        print(value)
        return value

    # rgb
    def rgb_set_color(self, color: str) -> None:
        '''
        Sets a led to input color.
        Param: color: the wanted color.
        '''
        self.rgb_led.set_on(color)

    # light sensor
    def __transf_1024(self, value: float) -> float:
        '''
        Transforms a value from (initial) range [0, 1] to range [0, 1024].
        Param: value: the value to be transformed (has range [0, 1]).
        Returns: the transformed value (now has range [0, 1024]).
        '''
        return value * 1024

    def get_light_sensor(self) -> float:
        '''
        Returns the reading of the light sensor.
        '''
        light_id = self.parameters.simulation.light_sensor_id
        return self.__transf_1024(self.analogue_reader.get_reading(light_id))

    def check_for_dark(self) -> bool:
        '''
        Returns True only if light sensor detects dark.
        '''
        light_id = self.parameters.simulation.light_sensor_id
        # grey == 50%, white == 100%, black <= 10%
        grey_color = self.parameters.light_sensor.value / 1024
        value = self.analogue_reader.get_reading(light_id)
        print(self.__transf_1024(value))
        return bool(value < grey_color)

    # noise detection
    def get_noise_detection(self) -> bool:
        """ Returns True only if noise is detected """
        state = self.noise.detect_noise()
        print(state)
        return state

    # exit
    def exit(self) -> None:
        """ Exits. """
        self.stop()
        self.rgb_set_color('closed')
        sim.simxFinish(self.client_id)
        print('Program ended.')

    def __del__(self) -> None:
        #self.exit()
        print('Program ended.')

    # implemented only in simulation
    def check_collision(self) -> bool:
        '''
        Returns True if robot collides with other (collidable) object.
        '''
        while True:
            res, collision, _, _, _ = control.exec_vrep_script(
                self.client_id, self.parameters.simulation.col_detector_name,
                'check_collision')
            if res == sim.simx_return_ok and len(collision)>=1 and collision[0] != -1:
                return bool(collision[0])

    def check_in_bounds(self) -> bool:
        '''Returns True only if fossbot is on the floor.'''
        floor_path = '/' + self.parameters.simulation.floor_name
        while True:
            res, in_bounds, _, _, _ = control.exec_vrep_script(
                self.client_id, self.parameters.simulation.fossbot_name,
                'check_in_bounds', in_strings=[floor_path])
            if res == sim.simx_return_ok and len(in_bounds)>=1:
                return bool(in_bounds[0])

    def check_orientation(self) -> bool:
        '''Returns True only if fossbot has its initial orientation.'''
        while True:
            res, check_orient, _, _, _ = control.exec_vrep_script(
                self.client_id, self.parameters.simulation.fossbot_name,
                'check_orientation')
            if res == sim.simx_return_ok and len(check_orient)>=1:
                return bool(check_orient[0])

    def reset_orientation(self) -> None:
        '''Resets fossbot orientation (if it has flipped etc).'''
        while True:
            res, _, _, _, _ = control.exec_vrep_script(
                self.client_id, self.parameters.simulation.fossbot_name,
                'reset_orientation')
            if res == sim.simx_return_ok:
                break

    # timer:
    def stop_timer(self) -> None:
        '''Stops the timer.'''
        self.timer.stop_timer()

    def start_timer(self) -> None:
        '''Starts the timer.'''
        self.timer.start_timer()

    def get_elapsed(self) -> int:
        '''Returns the time from start.'''
        value = self.timer.get_elapsed()
        print('elapsed time in sec:', value)
        return value
