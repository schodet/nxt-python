# nxt.sensor.hitechnic module -- Classes to read HiTechnic sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010  rhn, Marcus Wanner, melducky, Samuel Leeman-Munk
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
from .analog import BaseAnalogSensor

class CompassMode:
    MEASUREMENT = 0x00
    CALIBRATION = 0x43
    CALIBRATION_FAILED = 0x02


class Compass(BaseDigitalSensor):
    """Hitechnic compass sensor."""

    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'heading': (0x44, '<H'),
                        'mode': (0x41, 'B'),
    })

    def get_heading(self):
        """Returns heading from North in degrees."""
        return self.read_value('heading')[0]
    
    get_sample = get_heading

    def get_relative_heading(self,target=0):
        """This function is untested but should work.
        If it does work, please post a message to the mailing list
        or email marcusw@cox.net. If it doesn't work, please file
        an issue in the bug tracker.
        """
        rheading = self.get_sample()-target
        if rheading > 180:
            rheading -= 360
        elif rheading < -180:
            rheading += 360
        return rheading	
    
    #this deserves a little explanation:
    #if max > min, it's straightforward, but
    #if min > max, it switches the values of max and min
    #and returns true if heading is NOT between the new max and min
    def is_in_range(self,min,max):
        """This function is untested but should work.
        If it does work, please post a message to the mailing list
        or email marcusw@cox.net. If it doesn't work, please file
        an issue in the bug tracker.
        """
        reversed = False
        if min > max:
            (max,min) = (min,max)
            reversed = True
        heading = self.get_sample()
        in_range = (heading > min) and (heading < max)
        #an xor handles the reversal
        #a faster, more compact way of saying
        #if !reversed return in_range
        #if reversed return !in_range
        return bool(reversed) ^ bool(in_range) 

    def get_mode(self):
        return self.read_value('mode')[0]
    
    def set_mode(self, mode):
         if mode != CompassMode.MEASUREMENT and \
                 mode != CompassMode.CALIBRATION:
             raise ValueError('Invalid mode specified: ' + str(mode))
         self.write_value('mode', (mode, ))
         
Compass.add_compatible_sensor('\xfdV1.23  ', 'HiTechnc', 'Compass ')
Compass.add_compatible_sensor('\xfdV2.1   ', 'HITECHNC', 'Compass ')


class Acceleration:
    def __init__(self, x, y, z):
        self.x, self.y, self.z =x, y, z

class Accelerometer(BaseDigitalSensor):
    'Object for Accelerometer sensors. Thanks to Paulo Vieira.'
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'x_axis_high': (0x42, 'b'),
        'y_axis_high': (0x43, 'b'),
        'z_axis_high': (0x44, 'b'),
        'xyz_short': (0x42, '3b'),
        'all_data': (0x42, '3b3B')
    })
    
    def __init__(self, brick, port, check_compatible=False):
        super(Accelerometer, self).__init__(brick, port, check_compatible)

    def get_acceleration(self):
        """"Returns the acceleration along x, y, z axes. Units are unknown to
        me.
        """
        xh, yh, zh, xl, yl, zl = self.read_value('all_data')
        x = xh << 2 + xl
        y = yh << 2 + yl
        z = zh << 2 + yl
        return Acceleration(x, y, z)
    
    get_sample = get_acceleration

Accelerometer.add_compatible_sensor('\xfdV1.1   ', 'HITECHNC', 'Accel.  ')


class Gyro(BaseAnalogSensor):
    'Object for gyro sensors'
#This class is for the hitechnic gryo sensor. When the gryo is not
#moving there will be a constant offset that will change with 
#temperature and other ambient factors. The calibrate() function
#takes the currect value and uses it to offset subsequesnt ones.

    def __init__(self, brick, port):
        super(Gyro, self).__init__(brick, port)
        self.set_input_mode(Type.ANGLE, Mode.RAW)
        self.offset = 0
    
    def get_rotation_speed(self):
        return self.get_input_values().scaled_value - self.offset
    
    def set_zero(self, value):
        self.offset = value
    
    def calibrate(self):
        self.set_zero(self.get_rotation_speed())
    
    get_sample = get_rotation_speed
