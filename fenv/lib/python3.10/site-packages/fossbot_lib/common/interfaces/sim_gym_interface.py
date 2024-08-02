'''Gym interface for simulated environment.'''

from abc import ABC, abstractmethod
from fossbot_lib.common.interfaces import robot_interface

# used only in simulation robot:
class EnvironmentInterface(ABC):
    """
    Interface for Environment control.
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
    @abstractmethod
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

    @abstractmethod
    def draw_path_auto(self, robot: robot_interface.FossBotInterface, path_to_file: str) -> None:
        '''
        Changes the path of the scene and scales it automatically on the floor.
        Param: robot: an instance of fossbot.
               path_to_file: the path to the image for the
               path in simulation to be changed to.
        '''

    @abstractmethod
    def clear_path(self, robot: robot_interface.FossBotInterface) -> None:
        '''
        Clears the path of the scene.
        Param: robot: an instance of fossbot.
        '''

    @abstractmethod
    def change_brightness(
            self, robot: robot_interface.FossBotInterface,
            brightness: int = 50) -> None:
        '''
        Changes scene's brightness.
        Param: robot: an instance of fossbot.
               brightness: the percentage of the brightness to be changed to
               (default brightness == 50%).
        '''

    @abstractmethod
    def default_brightness(self, robot: robot_interface.FossBotInterface) -> None:
        '''
        Sets scene's brightness to default brightness (50%).
        Param: robot: an instance of fossbot.
        '''

    @abstractmethod
    def get_simulation_time(self, robot: robot_interface.FossBotInterface) -> float:
        '''
        Returns current time of simulation.
        Param: robot: an instance of fossbot.
        '''

    # fossbot teleport
    @abstractmethod
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

    @abstractmethod
    def teleport_random(
            self, robot: robot_interface.FossBotInterface,
            in_bounds: bool = True) -> None:
        '''
        Teleports fossbot to random location.
        Param: robot: the instance of fossbot to be teleported.
               in_bounds: if True, fossbot teleports within the floor bounds.
        '''

    @abstractmethod
    def teleport_empty_space(
            self, robot: robot_interface.FossBotInterface,
            time_diff: int = 0.5) -> None:
        '''
        Teleports fossbot to location with no obstacles (on the floor).
        Param: robot: the instance of fossbot to be teleported.
               time_diff: the time to check successfull teleportation.
        '''

    @abstractmethod
    def change_floor_size(
            self, robot: robot_interface.FossBotInterface,
            x_size: float = 5.0, y_size: float = 5.0) -> None:
        '''
        Changes floor size.
        Param: robot: an instance of fossbot.
               x_size: the x scale to change the floor size to.
               y_size: the y scale to change the floor size to.
        '''

    @abstractmethod
    def save_curr_floor_size(self, robot: robot_interface.FossBotInterface) -> None:
        '''Saves current floor size.'''
