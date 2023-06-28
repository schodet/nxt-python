import nxt.locator
from nxt.sensor.generic import Ultrasonic
from nxt.sensor.hitechnic import SuperPro

"""
Experiment 3, adapted from the SuperPro demo

For this demo, attach LEDs between B0-B5 and GND, and connect an Ultrasonic to Sensor
Port 4.

When you change the distance, the LED's will roughly indicate the distance in 10cm
increments.
"""

# Find NXT, configure sensor
with nxt.locator.find() as brick:
    pro = SuperPro(brick, nxt.sensor.Port.S1)
    ultrasonic = Ultrasonic(brick, nxt.sensor.Port.S4)

    # Configure B0-5 as output
    pro.set_digital_modes_byte(0x3F)

    while True:
        try:
            # Get distance (cm)
            distance_cm = ultrasonic.get_distance()
            print("Distance: {}cm".format(distance_cm))
            # Convert distance to 6 divisions
            segmented = int(distance_cm / 10.0)
            # This prevents longer distances from turning off the LED
            if segmented > 6:
                segmented = 5
            # Set the corresponding bit
            pro.set_digital_byte(2**segmented)
        except KeyboardInterrupt:
            break

    # When program stopped, turn off outputs
    pro.set_digital_byte(0x00)
