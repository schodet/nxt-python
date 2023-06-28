from time import sleep

import nxt.locator
from nxt.sensor.hitechnic import SuperPro

"""
Experiment 9, adapted from the SuperPro demo

For this demo, connect a speaker between O0 and O1.
"""
A4_FREQ = 440
C4_FREQ = 261
DS4_FREQ = 311
E4_FREQ = 329
F4_FREQ = 349
G4_FREQ = 392

# Find NXT, configure sensor
with nxt.locator.find() as brick:
    pro = SuperPro(brick, nxt.sensor.Port.S1)

    pro.analog_out_voltage(0, SuperPro.AnalogOutputMode.SQUARE, C4_FREQ, 3.3)
    sleep(0.2)
    pro.analog_out_voltage(0, SuperPro.AnalogOutputMode.SQUARE, DS4_FREQ, 3.3)
    sleep(0.2)
    pro.analog_out_voltage(0, SuperPro.AnalogOutputMode.SQUARE, E4_FREQ, 3.3)
    sleep(0.2)
    pro.analog_out_voltage(0, SuperPro.AnalogOutputMode.SQUARE, 1, 0.0)

    sleep(0.2)

    pro.analog_out_voltage(0, SuperPro.AnalogOutputMode.SQUARE, F4_FREQ, 3.3)
    pro.analog_out_voltage(1, SuperPro.AnalogOutputMode.SQUARE, A4_FREQ, 3.3)
    sleep(0.2)
    pro.analog_out_voltage(0, SuperPro.AnalogOutputMode.SQUARE, E4_FREQ, 3.3)
    pro.analog_out_voltage(1, SuperPro.AnalogOutputMode.SQUARE, G4_FREQ, 3.3)
    sleep(0.2)
    pro.analog_out_voltage(0, SuperPro.AnalogOutputMode.SQUARE, C4_FREQ, 3.3)
    pro.analog_out_voltage(1, SuperPro.AnalogOutputMode.SQUARE, E4_FREQ, 3.3)
    sleep(0.2)
    pro.analog_out_voltage(0, SuperPro.AnalogOutputMode.SQUARE, 1, 0.0)
    pro.analog_out_voltage(1, SuperPro.AnalogOutputMode.SQUARE, 1, 0.0)
