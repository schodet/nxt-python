#!/usr/bin/env python3
"""NXT-Python example to use sensors."""
import time

import nxt.locator
import nxt.sensor
import nxt.sensor.generic

with nxt.locator.find() as b:
    touch = b.get_sensor(nxt.sensor.Port.S1, nxt.sensor.generic.Touch)
    sound = b.get_sensor(nxt.sensor.Port.S2, nxt.sensor.generic.Sound)
    light = b.get_sensor(nxt.sensor.Port.S3, nxt.sensor.generic.Light, False)
    us = b.get_sensor(nxt.sensor.Port.S4)
    sensors = [touch, sound, light, us]

    while True:
        samples = [s.get_sample() for s in sensors]
        print(samples)
        time.sleep(0.5)
