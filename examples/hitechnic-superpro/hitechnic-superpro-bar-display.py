from time import sleep
import nxt.locator
from nxt.sensor.hitechnic import SuperPro

"""
For this demo, attach LED's to the HiTechnic SuperPro from pins B0-B7 to GND.
No resistors necessary, as these pins already have 220 ohm resistors.
After electrical connections are completed, connect the SuperPro to Port S1 on the NXT.

Note: The original kit only comes with 6 green/red LED's, so if you're short on LED's just connect B0-B5.
WARNING: If you are light sensitive, avoid this demo. It flashes the B0 LED at ~5Hz.
"""

# Find NXT, configure sensor
with nxt.locator.find() as brick:
    pro = SuperPro(brick, nxt.sensor.Port.S1)

    # Configure digital pins as outputs.
    # Outputs have 220 ohm resistors in series, so directly connect LED's from pins to GND
    pro.set_digital_modes_byte(0xFF)

    # For x in 0 to 255 (inclusive) - byte representation, Python range() is range(inclusive, exclusive)
    for x in range(0, 256):
        pro.set_digital_byte(x)
        print("Outputting {0:3} ({0:<08b})".format(x))
        sleep(0.1)

    # Output 0 to turn off all pins
    pro.set_digital_byte(0x00)
    # Put all pins back as inputs (default state)
    pro.set_digital_modes_byte(0x00)
