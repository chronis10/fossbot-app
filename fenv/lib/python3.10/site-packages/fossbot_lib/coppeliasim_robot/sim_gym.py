'''Gym for simulated environment.'''

import os
import random
import time
from fossbot_lib.coppeliasim_robot import control
from fossbot_lib.common.interfaces import robot_interface,sim_gym_interface

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

# used only in simulation robot:
class Environment(sim_gym_interface.EnvironmentInterface):
    """
    EnvironmentHandler() -> Environment control.
    Functions:
    draw_path(robot,file_name,scale_x,scale_y) Changes the path of the scene.
    draw_path_auto(robot,file_name) Changes the path of the scene and scales
                              it automatically on the floor.
    clear_path(robot): Clears the path of the scene.
    change_brightness(robot,brightness): Changes scene's brightness.
    default_brightness(robot): Sets scene's brightness to default brightness (50%).
    get_simulation_time(robot): Returns current time of simulation.
    teleport(robot,pos_x,pos_y,height,in_bounds): Teleports fossbot to input location.
    teleport_random(robot,in_bounds): Teleports fossbot to random location.
    teleport_empty_space(robot,time_diff): Teleports fossbot to location
                                           with no obstacles (on the floor).
    """
    # change path functions:
    def draw_path(
            self, robot: robot_interface.FossBotInterface, path_to_file: str,
            scale_x: float = 5.0, scale_y: float = 5.0) -> None:
        '''
        Changes the path of the scene.
        Param: robot: an instance of fossbot.
               path_to_file: the path to the image for the
               path in simulation to be changed to.
               scale_x: scale x for image on the floor.
               scale_y: scale y for image on the floor.
        '''
        client_id = robot.parameters.simulation.client_id
        parameters = robot.parameters
        path_draw = path_to_file
        if not os.path.exists(path_draw):
            print('Cannot find requested image.')
            raise FileNotFoundError
        while True:
            res, _, _, _, _ = control.exec_vrep_script(
                client_id, parameters.simulation.floor_name, 'draw_path',
                in_floats=[scale_x, scale_y], in_strings=[path_draw])
            if res == sim.simx_return_ok:
                break

    def draw_path_auto(self, robot: robot_interface.FossBotInterface, path_to_file: str) -> None:
        '''
        Changes the path of the scene and scales it automatically on the floor.
        Param: robot: an instance of fossbot.
               path_to_file: the path to the image for the
               path in simulation to be changed to.
        '''
        client_id = robot.parameters.simulation.client_id
        parameters = robot.parameters
        path_draw = path_to_file
        if not os.path.exists(path_draw):
            print('Cannot find requested image.')
            raise FileNotFoundError
        while True:
            res, _, _, _, _ = control.exec_vrep_script(
                client_id, parameters.simulation.floor_name, 'draw_path_auto',
                in_strings=[path_draw])
            if res == sim.simx_return_ok:
                break

    def clear_path(self, robot: robot_interface.FossBotInterface) -> None:
        '''
        Clears the path of the scene.
        Param: robot: an instance of fossbot.
        '''
        client_id = robot.parameters.simulation.client_id
        parameters = robot.parameters
        while True:
            res, _, _, _, _ = control.exec_vrep_script(
                client_id, parameters.simulation.floor_name,
                'clear_path')
            if res == sim.simx_return_ok:
                break

    def change_brightness(
            self, robot: robot_interface.FossBotInterface,
            brightness: int = 50) -> None:
        '''
        Changes scene's brightness.
        Param: robot: an instance of fossbot.
               brightness: the percentage of the brightness to be changed to
               (default brightness == 50%).
        '''
        client_id = robot.parameters.simulation.client_id
        parameters = robot.parameters
        if brightness < 0 or brightness > 100:
            print("The brightness is a percentage. Accepted values 0-100.")
        else:
            print('Changing brightness...')
            brightness = brightness / 100
            while True:
                res, _, _, _, _ = control.exec_vrep_script(
                    client_id, parameters.simulation.foss_gui,
                    'change_brightness', in_floats=[brightness, brightness, brightness])
                if res == sim.simx_return_ok:
                    break

    def default_brightness(self, robot: robot_interface.FossBotInterface) -> None:
        '''
        Sets scene's brightness to default brightness (50%).
        Param: robot: an instance of fossbot.
        '''
        self.change_brightness(robot, 50)

    def get_simulation_time(self, robot: robot_interface.FossBotInterface) -> float:
        '''
        Returns current time of simulation.
        Param: robot: an instance of fossbot.
        '''
        client_id = robot.parameters.simulation.client_id
        parameters = robot.parameters
        while True:
            res, _, sim_time, _, _ = control.exec_vrep_script(
                client_id, parameters.simulation.foss_gui,
                'get_sim_time')
            if res == sim.simx_return_ok and len(sim_time) >= 1:
                return sim_time[0]

    # fossbot teleport
    def teleport(
            self, robot: robot_interface.FossBotInterface,
            pos_x: float, pos_y: float, height: float = 0.19,
            in_bounds: bool = True) -> None:
        '''
        Teleports fossbot to input location.
        Param: robot: the instance of fossbot to be teleported.
               pos_x: the x position to teleport to.
               pos_y: the y position to teleport to.
               hegiht: the height to teleport to (default == 0.19).
               in_bounds: if True, fossbot teleports within the floor bounds.
        '''
        client_id = robot.parameters.simulation.client_id
        floor_path = '/' + robot.parameters.simulation.floor_name
        func_name = 'teleport'
        fossbot_name = robot.parameters.simulation.fossbot_name
        if in_bounds:
            func_name = 'teleport_inbounds'
        while True:
            res, _, _, _, _ = control.exec_vrep_script(
                client_id, fossbot_name,
                func_name, in_floats=[pos_x, pos_y, height],
                in_strings=[floor_path])
            if res == sim.simx_return_ok:
                break

    def teleport_random(
            self, robot: robot_interface.FossBotInterface,
            in_bounds: bool = True) -> None:
        '''
        Teleports fossbot to random location.
        Param: robot: the instance of fossbot to be teleported.
               in_bounds: if True, fossbot teleports within the floor bounds.
        '''
        client_id = robot.parameters.simulation.client_id
        floor_path = '/' + robot.parameters.simulation.floor_name
        fossbot_name = robot.parameters.simulation.fossbot_name
        if in_bounds:
            while True:
                res, _, limits, _, _ = control.exec_vrep_script(
                    client_id, fossbot_name, 'get_bounds',
                    in_strings=[floor_path])
                if res == sim.simx_return_ok and len(limits) >= 2:
                    pos_x = random.uniform(-limits[0], limits[0])
                    pos_y = random.uniform(-limits[1], limits[1])
                    break
        else:
            i = random.randint(0, 1000)
            pos_x = random.uniform(-i, i)
            pos_y = random.uniform(-i, i)
        self.teleport(robot, pos_x, pos_y, in_bounds=in_bounds)

    def teleport_empty_space(
            self, robot: robot_interface.FossBotInterface,
            time_diff: int = 0.5) -> None:
        '''
        Teleports fossbot to location with no obstacles (on the floor).
        Param: robot: the instance of fossbot to be teleported.
               time_diff: the time to check successfull teleportation.
        '''
        while True:
            print('Teleporting...')
            self.teleport_random(robot, in_bounds=True)
            target_time = self.get_simulation_time(robot) + time_diff
            while self.get_simulation_time(robot) < target_time:
                if robot.check_collision():
                    print('Teleporting...')
                    self.teleport_random(robot, in_bounds=True)
                    target_time = self.get_simulation_time(robot) + time_diff
            time.sleep(time_diff*0.5)
            robot.reset_orientation()
            if not robot.check_collision() and robot.check_in_bounds() and robot.check_orientation():
                break
        print('Teleport success.')

    def change_floor_size(
            self, robot: robot_interface.FossBotInterface,
            x_size: float = 5.0, y_size: float = 5.0) -> None:
        '''
        Changes floor size.
        Param: robot: an instance of fossbot.
               x_size: the x scale to change the floor size to.
               y_size: the y scale to change the floor size to.
        '''
        if x_size < 0 or y_size < 0:
            print('There is no negative scale!')
            raise RuntimeError
        client_id = robot.parameters.simulation.client_id
        parameters = robot.parameters
        while True:
            res, _, _, _, _ = control.exec_vrep_script(
                client_id, parameters.simulation.floor_name, 'change_floor_size',
                in_floats=[x_size, y_size])
            if res == sim.simx_return_ok:
                break

    def save_curr_floor_size(self, robot: robot_interface.FossBotInterface) -> None:
        '''Saves current floor size.'''
        client_id = robot.parameters.simulation.client_id
        parameters = robot.parameters
        while True:
            res, _, _, _, _ = control.exec_vrep_script(
                client_id, parameters.simulation.floor_name,
                'save_current_size_run')
            if res == sim.simx_return_ok:
                break
