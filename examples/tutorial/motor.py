#!/usr/bin/python3
"""NXT-Python tutorial: turn a motor."""
import nxt.locator
import nxt.motor

with nxt.locator.find() as b:
    # Get the motor connected to the port A.
    mymotor = b.get_motor(nxt.motor.Port.A)
    # Full circle in one direction.
    mymotor.turn(25, 360)
    # Full circle in the opposite direction.
    mymotor.turn(-25, 360)
