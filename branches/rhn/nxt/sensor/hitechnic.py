# nxt.sensor.hitechnic module -- Classes to read HiTechnic sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira
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

from .common import *
from .digital import BaseDigitalSensor


class CompassMode:
    MEASUREMENT = 0x00
    CALIBRATION = 0x43
    CALIBRATION_FAILED = 0x02


class Compass(BaseDigitalSensor):
    """Hitechnic compass sensor."""
    #tested on '\xfdV1.23  ', 'HiTechnc', 'Compass '

    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'heading': (0x44, '<H'),
                        'mode': (0x41, 'B'),
    })

    def get_heading(self):
        """Returns heading from North in degrees."""
        return self.read_value('heading')[0]
    
    get_sample = get_heading

    def get_mode(self):
        return self.read_value('mode')[0]
    
    def set_mode(self, mode):
         if mode != CompassMode.MEASUREMENT and \
                 mode != CompassMode.CALIBRATION:
             raise ValueError('Invalid mode specified: ' + str(mode))
         self.write_value('mode', (mode, ))
 

class Acceleration:
    def __init__(self, x, y, z):
        self.x, self.y, self.z =x, y, z
        

class Accelerometer(BaseDigitalSensor):
    'Object for Accelerometer sensors. Thanks to Paulo Vieira. Broken by rhn.'
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'x_axis_high': (0x42, 'b'),
        'y_axis_high': (0x43, 'b'),
        'z_axis_high': (0x44, 'b'),
        'xyz_short': (0x42, '3b'),
        'all_data': (0x42, '3b3B')
    })

    def get_acceleration(self):
        """"Returns the acceleration along x, y, z axes. Units are unknown to
        me.
        """
        xh, yh, zh, xl, yl, zl = self.read_values('all_data')
        x = xh << 2 + xl
        y = yh << 2 + yl
        z = zh << 2 + yl
        return Acceleration(x, y, z)
    
    get_sample = get_acceleration
