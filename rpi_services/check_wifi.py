import time
import os
import sys
import RPi.GPIO as GPIO
from fossbot_lib.real_robot.control import LedRGB, start_lib, clean

def check_internet():
    """
    Check if the Raspberry Pi has internet access.
    Returns True if connected to the internet, False otherwise.
    """
    return os.system("ping -c 1 8.8.8.8 > /dev/null 2>&1") == 0

def check_wifi():
    """
    Check if the Raspberry Pi is connected to a Wi-Fi network.
    Returns True if connected to Wi-Fi, False otherwise.
    """
    return os.system("iwgetid -r > /dev/null 2>&1") == 0

def main():
    start_lib()
    # Initialize the LED control object
    led_control = LedRGB(anode=False)

    # Check if the Raspberry Pi is connected to Wi-Fi
    if not check_wifi():
        # No Wi-Fi connection: Blink red once
        led_control.set_on('red')
        time.sleep(1)
        led_control.set_on('closed')
        time.sleep(1)
        # Exit with an error status code
        clean()
        sys.exit(1)
    else:
        # Wi-Fi is connected, show green
        led_control.set_on('green')
        time.sleep(1)
        if check_internet():
            # If internet is available, show blue for success
            led_control.set_on('blue')
            time.sleep(1)
            # Exit successfully
            
            sys.exit(0)
        else:
            # Wi-Fi connected but no internet, show yellow
            led_control.set_on('yellow')
            time.sleep(1)
            
            sys.exit(2)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
