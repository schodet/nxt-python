#!/usr/bin/python3
"""NXT-Python tutorial: use touch sensor."""
import time

import nxt.locator
import nxt.sensor
import nxt.sensor.generic

with nxt.locator.find() as b:
    # Get the sensor connected to port 1, not a digital sensor, must give the sensor
    # class.
    mysensor = b.get_sensor(nxt.sensor.Port.S1, nxt.sensor.generic.Touch)
    # Read the sensor in a loop (until interrupted).
    print("Use Ctrl-C to interrupt")
    while True:
        value = mysensor.get_sample()
        print(value)
        time.sleep(0.5)
