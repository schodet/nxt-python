# nxt.sensor.hitechnic module -- Classes to read HiTechnic sensors
# Copyright (C) 2009 rhn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import nxt.sensor
import struct
from time import sleep

class CompassMode:
    MEASUREMENT = 0
    CALIBRATION = 0x43
    CALIBRATION_FAILED = 0x02


class Compass(nxt.sensor.DigitalSensor):
    I2C_ADDR = {'heading': (0x44, '<H'),
                        'mode': (0x41, 'b'),
    }
    
    def __init__(self, brick, port):
        super(Compass, self).__init__(brick, port)
        self.sensor_type = nxt.sensor.Type.LOW_SPEED_9V
        self.mode = nxt.sensor.Mode.RAW
        self.set_input_mode()
        sleep(0.1)	# Give I2C time to initialize
    
    def get_heading(self):
        return self._i2c_query('heading')[0]

    def get_mode(self):
        return self._i2c_query('mode')[0]
    
    def set_mode(self, mode):
         if mode != CompassMode.MEASUREMENT and \
                 mode != CompassMode.CALIBRATION:
             raise TypeError('Invalid mode specified: ' + str(mode))
         self._i2c_command('mode', (mode, ))
