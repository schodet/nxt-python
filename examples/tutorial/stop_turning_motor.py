#!/usr/bin/python3
import nxt.locator
import nxt.motor

import time
import threading

with nxt.locator.find() as b:
    # Get the motor connected to the port A.
    mymotor: nxt.motor.BaseMotor = b.get_motor(nxt.motor.Port.A)

    stop_motor = False  # controls wether the motor should stop turning

    # create thread that turns the motor
    t = threading.Thread(target=mymotor.turn, kwargs={
                         'power': 50, 'tacho_units': 360*4, 'brake': True, 'stop_turn': lambda: stop_motor})
    t.start()

    # stop motor after 1sec (motor would turn approximately 3sec)
    time.sleep(1)
    stop_motor = True

    t.join()

    # release motor after 1sec since brake=True
    time.sleep(1)
    mymotor.idle()
