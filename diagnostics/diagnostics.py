import sys
import os
import time
from fossbot_lib.parameters_parser.parser import load_parameters
from fossbot_lib.common.data_structures import configuration
from fossbot_lib.common.interfaces import robot_interface
from fossbot_lib.real_robot.fossbot import FossBot


def load_configuration():
    file_params = load_parameters()
    parameters = configuration.RobotParameters(
    sensor_distance=configuration.SensorDistance(**file_params["sensor_distance"]),
    motor_left_speed=configuration.MotorLeftSpeed(**file_params["motor_left"]),
    motor_right_speed=configuration.MotorRightSpeed(**file_params["motor_right"]),
    default_step=configuration.DefaultStep(**file_params["step"]),
    light_sensor=configuration.LightSensor(**file_params["light_sensor"]),
    line_sensor_left=configuration.LineSensorLeft(**file_params["line_sensor_left"]),
    line_sensor_center=configuration.LineSensorCenter(**file_params["line_sensor_center"]),
    line_sensor_right=configuration.LineSensorRight(**file_params["line_sensor_right"]),
    rotate_90=configuration.Rotate90(**file_params["rotate_90"]))
    return parameters


def _test_accelerometer_gyroscope(robot: FossBot) -> None:
    print("Accelerometer & Gyroscope test")
    print("Press Ctrl+C to stop")
    try:
        while True:
            print("Accelerometer:")
            print(f"{robot.get_acceleration('x')}, {robot.get_acceleration('y')}, {robot.get_acceleration('z')}")
            print("Gyroscope:")
            print(f"{robot.get_gyroscope('x')}, {robot.get_gyroscope('y')}, {robot.get_gyroscope('z')}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

def _test_motors(robot: FossBot) -> None:
    print("Motors test")
    print("Press Ctrl+C to stop")
    print("Left motor forward...")
    try:
        while True:
            robot.motor_left.move(direction="forward")
    except KeyboardInterrupt:
        pass
    finally:
        robot.motor_left.stop()
        print("Left motor stop")
    print("Left motor backward...")
    try:
        while True:
            robot.motor_left.move(direction="reverse")
    except KeyboardInterrupt:
        pass
    finally:
        robot.motor_left.stop()
        print("Left motor stop")
    print("Right motor forward...")
    try:
        while True:
            robot.motor_right.move(direction="forward")
    except KeyboardInterrupt:
        pass
    finally:
        robot.motor_right.stop()
        print("Right motor stop")
    print("Right motor backward...")
    try:
        while True:
            robot.motor_right.move(direction="reverse")
    except KeyboardInterrupt:
        pass
    finally:
        robot.motor_right.stop()
        print("Right motor stop")

def _test_light_sensor(robot: FossBot) -> None:
    print("Light sensor test")
    print("Press Ctrl+C to stop")
    try:
        while True:
            print(robot.get_light_sensor())
    except KeyboardInterrupt:
        pass
def _test_line_sensors(robot: FossBot) -> None:
    print("Line sensors test")
    print("Press Ctrl+C to stop")
    sensors = ["Center", "Right","Left"]
    for i in range(1,4):
        try:
            while True:
                print(f"{sensors[i-1]}: {robot.get_floor_sensor(i)}")
        except KeyboardInterrupt:
            pass

def _test_rgb_led(robot: FossBot) -> None:
    print("RGB LED test")
    print("Press Ctrl+C to stop")
    colors = ["red", "green", "blue"]
    for color in colors:
        try:
            print(f"{color}...")
            while True:
                robot.rgb_set_color(color)
        except KeyboardInterrupt:
            pass
        finally:
            robot.rgb_set_color("off")
            print("Off")

def _test_odometers(robot: FossBot) -> None:
    print("Odometers test")
    print("Press Ctrl+C to stop")
    try:
        while True:
            print(f"Left: {robot.odometer_left.get_distance()}, Right: {robot.odometer_right.get_distance()}")
    except KeyboardInterrupt:
        pass
def _test_speaker(robot: FossBot) -> None:
    print("Speaker test")
    print("Press Ctrl+C to stop")
    try:
        while True:
            print("Check the speaker")
            robot.play_sound("r2d2.mp3")
            input_user = input("Press any key to repeat the test.")
    except KeyboardInterrupt:
        pass
    
def _test_ultrasonic_sensor(robot: FossBot) -> None:
    print("Ultrasonic sensor test")
    print("Press Ctrl+C to stop")
    try:
        while True:
            print(robot.get_distance())
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

def _test_noise_sensor(robot: FossBot) -> None:
    print("Noise sensor test")
    print("Press Ctrl+C to stop")
    try:
        while True:
            print(robot.get_noise_detection())
    except KeyboardInterrupt:
        pass


def _options_menu() -> int:
    print("Options menu:")
    print("1. Test Accelerometer & Gyroscope")
    print("2. Test Left & Right motors")
    print("3. Test light sensor")
    print("4. Test line sensors")
    print("5. Test RGB LED")
    print("6. Test Odometers")
    print("7. Test Speaker")
    print("8. Test Ultrasonic sensor")
    print("9. Test Noise sensor")
    print("0. Exit")
    option = int(input("Select an option: "))
    return option


def _select_test(robot) -> None:
    option = _options_menu()
    while option != 0:
        if option == 1:
            _test_accelerometer_gyroscope(robot)
        elif option == 2:
            _test_motors(robot)
        elif option == 3:
            _test_light_sensor(robot)
        elif option == 4:
            _test_line_sensors(robot)
        elif option == 5:
            _test_rgb_led(robot)
        elif option == 6:
            _test_odometers(robot)
        elif option == 7:
            _test_speaker(robot)
        elif option == 8:
            _test_ultrasonic_sensor(robot)
        elif option == 9:
            _test_noise_sensor(robot)
        else:
            print("Invalid option")
        option = _options_menu()

if __name__ == '__main__':
    parameters = load_configuration()
    try:
        robot = FossBot(parameters=parameters)
        _select_test(robot)
    except Exception as e:
        print("Exception: {}".format(e))
    finally:
        robot.exit()
