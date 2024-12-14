from time import sleep

import nxt.locator
from nxt.sensor.hitechnic import SuperPro

"""
Experiment 4, adapted from the SuperPro demo

For this demo, attach a photo-resistor between A0 and 3V and a 4.7kOhm resistor between
GND and A0.

Note: In testing I used a 10kOhm since I don't have 4.7kOhm handy.

It measures brightness and prints to the console. The brighter it is, the higher the
voltage.

In my testing, a phone flashlight puts it to 3.2V and putting my hand over it results in
0.1V, with natural light levels in my workspace being around 1.9-2.0V
"""

# Find NXT, configure sensor
with nxt.locator.find() as brick:
    pro = SuperPro(brick, nxt.sensor.Port.S1)

    while True:
        try:
            # Get brightness (measured in volts)
            analog_value = pro.get_analog_volts()["a0"]
            print(f"Analog 0: {analog_value}V")
            # Sleep 0.1s to allow console to be read.
            sleep(0.1)
        except KeyboardInterrupt:
            break

    # When program stopped, turn off outputs
    pro.set_digital_byte(0x00)
