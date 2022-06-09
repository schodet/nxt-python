#!/usr/bin/env python3
"""NXT-Python example to use Linus Atorf's MotorControl.

You need to have MotorControl22 program installed on the brick, you can find it here:

https://github.com/schodet/MotorControl

Build it and install it with nxc, or upload the precompiled version (MotorControl22.rxe
file).
"""
import time

import nxt.locator
import nxt.motcont
import nxt.motor

with nxt.locator.find() as b:
    mc = nxt.motcont.MotCont(b)

    def wait():
        while not mc.is_ready(nxt.motor.Port.A) or not mc.is_ready(nxt.motor.Port.B):
            time.sleep(0.5)

    mc.start()

    mc.cmd((nxt.motor.Port.A, nxt.motor.Port.B), 50, 360)
    wait()

    mc.cmd((nxt.motor.Port.A, nxt.motor.Port.B), -50, 360)
    wait()

    mc.stop()
