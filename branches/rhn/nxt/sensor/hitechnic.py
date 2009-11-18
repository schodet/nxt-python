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

import struct
from time import sleep
from .common import *
from .digital import BaseDigitalSensor

class CompassMode:
    MEASUREMENT = 0
    CALIBRATION = 0x43
    CALIBRATION_FAILED = 0x02


class Compass(BaseDigitalSensor):
    I2C_ADDR = {'heading': (0x44, '<H'),
                        'mode': (0x41, 'B'),
    }
    
    def __init__(self, brick, port):
        super(Compass, self).__init__(brick, port)
		self.set_input_mode(Type.LOW_SPEED_9V, Mode.RAW)
        sleep(0.1)	# Give I2C time to initialize
    
    def get_heading(self):
        return self.read_value('heading')[0]

    def get_mode(self):
        return self.read_value('mode')[0]
    
    def set_mode(self, mode):
         if mode != CompassMode.MEASUREMENT and \
                 mode != CompassMode.CALIBRATION:
             raise TypeError('Invalid mode specified: ' + str(mode))
         self.write_value('mode', (mode, ))
 
         
class Accelerometer(BaseDigitalSensor):
	'Object for Accelerometer sensors. Thanks to Paulo Vieira. Broken by rhn.'
	I2C_ADDR = {'x_axis_high': (0x42, 'b'),
	    'y_axis_high': (0x43, 'b'),
	    'z_axis_high': (0x44, 'b'),
	    'xyz_short': (0x42, 'b' * 3),
	    'all_data': (0x42, 'b' * 3 + 'B' * 3)
	}
	def __init__(self, brick, port):
		super(Accelerometer, self).__init__(brick, port)
		self.set_input_mode(Type.LOW_SPEED_9V, Mode.RAW)
		sleep(0.1)  # Give I2C time to initialize

    def get_acceleration(self):
        """"Returns the acceleration along x, y, z axes. Units are unknown to
        me.
        """
        xh, yh, zh, xl, yl, zl = self.read_values('all_data')
        x = xh << 2 + xl
        y = yh << 2 + yl
        z = zh << 2 + yl
        return x, y, z
