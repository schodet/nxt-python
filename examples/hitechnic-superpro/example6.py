import nxt.locator
from nxt.sensor.hitechnic import SuperPro

"""
Experiment 6, adapted from the SuperPro demo

For this demo, connect LEDs between B0-B1 and GND. Connect buttons between 3V and B4-B5. Connect 10kOhm resistors
between B4-B5 and GND.

Since the delay in signals being sent to/from the NXT is pretty long (10+ms in testing), I just turned this into a demo
that uses the input and output on the digital bus for testing with the example circuit provided.

If you press the B4 button, B0 turns on, and if you press B5, B1 turns on.
"""

# Find NXT, configure sensor
with nxt.locator.find() as brick:
    pro = SuperPro(brick, nxt.sensor.Port.S1)

    # Configure B0,B1 as output
    pro.set_digital_modes_byte(0b0000011)
    pro.set_digital_byte(0x00)
    while True:
        try:
            digital_input = pro.get_digital()
            left_button = digital_input["b4"]
            right_button = digital_input["b5"]
            left_button_status = ""
            if left_button:
                left_button_status = "Pressed"
            else:
                left_button_status = "Released"
            right_button_status = ""
            if right_button:
                right_button_status = "Pressed"
            else:
                right_button_status = "Released"
            print("Left Button: {}\nRight Button: {}\n".format(left_button_status, right_button_status))
            pro.set_digital_byte(left_button + right_button * 2)
        except KeyboardInterrupt:
            break

    # When program stopped, turn off outputs
    pro.set_digital_byte(0x00)

