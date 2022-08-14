import nxt.locator
from nxt.sensor.hitechnic import SuperPro

"""
Experiment 2, adapted from the SuperPro demo

For this demo, attach LEDs between B0-B5 and GND, and a 10K between GND, 3V, and A0 (the wiper pin to A0).

When you turn the dial, the voltage changes and the LED's turn on roughly indicating the voltage at A0.
"""

# Find NXT, configure sensor
with nxt.locator.find() as brick:
    pro = SuperPro(brick, nxt.sensor.Port.S1)

    # Configure B0-5 as output
    pro.set_digital_modes_byte(0x3F)

    while True:
        try:
            # The original demo doesn't convert to volts, but I think displaying volts to the user is better than bits.
            analog_value = pro.get_analog_volts()["a0"]
            print("Analog 0: {}V".format(analog_value))
            # Convert voltage to 6 divisions
            segmented = int((analog_value / 3.3) * 6)
            # This prevents 3.3V "exactly" from being no LED's lit.
            if segmented == 6:
                segmented = 5
            # Set the corresponding bit
            pro.set_digital_byte(2 ** segmented)
        except KeyboardInterrupt:
            break

    # When program stopped, turn off outputs
    pro.set_digital_byte(0x00)
