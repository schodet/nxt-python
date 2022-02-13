#!/usr/bin/python3
"""NXT-Python tutorial: use ultra-sonic sensor."""
import time

import nxt.locator
import nxt.sensor

# Need to import generic sensors for auto-detection to work.
import nxt.sensor.generic

with nxt.locator.find() as b:
    # Find the sensor connected to port 4.
    mysensor = b.get_sensor(nxt.sensor.Port.S4)
    # Read the sensor in a loop (until interrupted).
    print("Use Ctrl-C to interrupt")
    while True:
        distance_cm = mysensor.get_sample()
        print(distance_cm)
        time.sleep(0.5)
