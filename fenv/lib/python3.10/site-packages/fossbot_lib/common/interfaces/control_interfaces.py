"""
Interfaces for control parts.
"""

from abc import ABC, abstractmethod

class TimerInterface(ABC):
    '''
    Class timer()
    Functions:
    stop_timer() Stops a timer.
    start_timer() Starts a timer.
    elapsed() Prints elapsed time from start.
    get_elapsed() Returns the elapsed time between start time and that moment in sec.
    '''

    @abstractmethod
    def stop_timer(self) -> None:
        '''Stops timer.'''

    @abstractmethod
    def start_timer(self) -> None:
        '''Starts timer.'''

    @abstractmethod
    def elapsed(self) -> None:
        '''Prints elapsed time from start.'''

    @abstractmethod
    def get_elapsed(self) -> int:
        '''Returns the elapsed time in seconds.'''

class MotorInterface(ABC):
    """
    Interface for Motor control.
    Functions:
    dir_control(direction) Change motor direction to input direction.
    move(direction) Start moving motor with default speed towards input direction.
    set_speed(speed) Set speed immediately 0-100 range.
    stop() Stops the motor.
    """

    @abstractmethod
    def set_speed(self, speed: int) -> None:
        '''
        Set speed immediately 0-100 range.
        Param: speed: the range 0 - 100 that speed will be changed to.
        '''

    @abstractmethod
    def dir_control(self, direction: str) -> None:
        '''
        Change motor direction to input direction.
        Param: direction: the direction to be headed to.
        '''

    @abstractmethod
    def move(self, direction: str = "forward") -> None:
        '''
        Start moving motor with default speed towards input direction.
        Param: direction: the direction to be headed to.
        '''

    @abstractmethod
    def stop(self) -> None:
        '''Stops the motor.'''


class OdometerInterface(ABC):
    '''
    Interface for Odometer control.
    Functions:
    count_revolutions() Increases the counter of revolutions.
    get_revolutions() Returns the number of revolutions.
    get_distance() Returns the traveled distance in cm.
    reset() Resets the steps counter.
    '''

    @abstractmethod
    def count_revolutions(self) -> None:
        '''Increase total steps by one.'''

    @abstractmethod
    def get_steps(self) -> int:
        ''' Returns total number of steps. '''

    @abstractmethod
    def get_revolutions(self) -> float:
        ''' Returns total number of revolutions. '''

    @abstractmethod
    def get_distance(self) -> float:
        ''' Return the total distance traveled so far (in cm). '''

    @abstractmethod
    def reset(self) -> None:
        ''' Reset the total traveled distance and revolutions. '''


class UltrasonicSensorInterface(ABC):
    '''
    Interface for Ultrasonic sensor control.
    Functions:
    get_distance() return distance in cm.
    '''

    def get_distance(self) -> float:
        '''
        Gets the distance to the closest obstacle.
        Returns: the distance to the closest obstacle (in cm).
        '''


class AccelerometerInterface(ABC):
    '''
    Interface for accelerometer and gyroscope.
    Functions:
    get_acceleration(dimension) Returns the acceleration for a specific dimension.
    get_gyro(dimension) Returns the gyroscope for a specific dimension.
    '''

    @abstractmethod
    def get_acceleration(self, dimension: str) -> float:
        '''
        Gets the acceleration for a specific dimension.
        Param: dimension: the dimension requested.
        Returns: the acceleration for a specific dimension.
        '''

    @abstractmethod
    def get_gyro(self, dimension: str) -> float:
        '''
        Gets gyroscope for a specific dimension.
        Param: dimension: the dimension requested.
        Returns: the gyroscope for a specific dimension.
        '''


class AnalogueReadingsInterface(ABC):
    '''
    Interface for Analogue Readings.
    Functions:
    get_reading(pin) Gets reading of a specific sensor specified by input pin.
    '''

    @abstractmethod
    def get_reading(self, pin: int) -> float:
        '''
        Gets reading of a specific sensor specified by input pin.
        Param: pin: the pin of the sensor.
        Returns: the reading of the requested sensor.
        '''

class NoiseInterface(ABC):
    '''
    Interface for noise (detection).
    Functions:
    detect_noise(): Returns True only if noise is detected.
    '''
    @abstractmethod
    def detect_noise(self) -> bool:
        '''
        Returns True only if noise was detected.
        '''

# Hardware section
class GenInputInterface(ABC):
    '''
    Interface for GenInput.
    Functions:
    get_state(): Returns state 0 or 1.
    '''
    @abstractmethod
    def get_state(self) -> int:
        '''
        Returns state 0 or 1
        '''

class GenOutputInterface(ABC):
    '''
    Interface for GenOutput.
    Functions:
    set_on() set High the output pin
    set_off() set Low the output pin
    '''
    @abstractmethod
    def set_on(self) -> None:
        '''
        Set High the output pin
        '''

    @abstractmethod
    def set_off(self) -> None:
        '''
        Set Low the output pin
        '''

class LedRGBInterface(ABC):
    '''
    Interface for Led control.
    Functions:
    set_on(color): sets led to input color.
    '''

    @abstractmethod
    def set_on(self, color: str) -> None:
        '''
        Changes the color of a led
        Param: color: the wanted color
        For closing the led, use color == 'closed'
        '''
