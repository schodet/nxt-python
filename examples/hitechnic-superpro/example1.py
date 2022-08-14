import nxt.locator
from nxt.sensor.hitechnic import SuperPro

"""
Experiment 1, adapted from the SuperPro demo

For this demo, attach an LED between B0 and GND, a button between 3V and A0, and a 10kOhm resistor between GND and A0.

When you press the button, it will turn on the LED.
"""

# Find NXT, configure sensor
with nxt.locator.find() as brick:
    pro = SuperPro(brick, nxt.sensor.Port.S1)

    # Configure B0 as output
    pro.set_digital_modes_byte(0x01)

    while True:
        try:
            # The original demo doesn't convert to volts, but I think displaying volts to the user is better than bits.
            analog_value = pro.get_analog_volts()["a0"]
            print("Analog 0: {}V".format(analog_value))
            if analog_value > 3.3/2.0:
                pro.set_digital_byte(0x01)
            else:
                pro.set_digital_byte(0x00)
        except KeyboardInterrupt:
            break

    # When program stopped, turn off outputs
    pro.set_digital_byte(0x00)
