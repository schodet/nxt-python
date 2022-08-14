import nxt.locator
from nxt.sensor.hitechnic import SuperPro

"""
Experiment 7, adapted from the SuperPro demo

For this demo, connect a LED between B4 and GND. Connect the magnetic hall-effect sensor (A3212EUA-T) as follows:

* Pin 1: 3V
* Pin 2: GND
* Pin 3: B0

Connect B0 to 3V with a 10kOhm resistor

Note: My magnetic hall effect sensor appears to be broken, so I couldn't really test this. RIP
"""

# Find NXT, configure sensor
with nxt.locator.find() as brick:
    pro = SuperPro(brick, nxt.sensor.Port.S1)

    # Configure B4 as output
    pro.set_digital_modes_byte(0b00010000)
    pro.set_digital_byte(0x00)

    while True:
        try:
            # Read B0 (magnet signal is inverted, low = magnet, then write back B4 with the value.
            hall_effect_sensor = pro.get_digital()["b0"]
            print("Magnet: {}".format(not hall_effect_sensor))
            pro.set_digital_byte((not hall_effect_sensor) << 4)
        except KeyboardInterrupt:
            break

    # When program stopped, turn off outputs
    pro.set_digital_byte(0x00)
