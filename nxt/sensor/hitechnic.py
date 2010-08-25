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
         
Compass.add_compatible_sensor(None, 'HiTechnc', 'Compass ') #Tested with version '\xfdV1.23  '
Compass.add_compatible_sensor(None, 'HITECHNC', 'Compass ') #Tested with version '\xfdV2.1   '


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

Accelerometer.add_compatible_sensor(None, 'HiTechnc', 'Accel.  ')
Accelerometer.add_compatible_sensor(None, 'HITECHNC', 'Accel.  ') #Tested with version '\xfdV1.1   '


class CompassMode:
    ACTIVE = 0x00 #get measurements using get_active_color
    PASSIVE = 0x01 #get measurements using get_passive_color
    RAW = 0x03 #get measurements using get_passive_color
    BLACK_CALIBRATION = 0x42 #hold away from objects, results saved in EEPROM
    WHITE_CALIBRATION = 0x43 #hold in front of white surface, results saved in EEPROM
    LED_POWER_LOW = 0x4C #saved in EEPROM, must calibrate after using
    LED_POWER_HIGH = 0x48 #saved in EEPROM, must calibrate after using
    RANGE_NEAR = 0x4E #saved in EEPROM, only affects active mode
    RANGE_FAR = 0x46 #saved in EEPROM, only affects active mode, more susceptable to noise
    FREQ_50 = 0x35 #saved in EEPROM, use when local wall power is 50Hz
    FREQ_60 = 0x36 #saved in EEPROM, use when local wall power is 60Hz

class ActiveColor:
    def __init__(self, number, red, green, blue, white, index, normred, normgreen, normblue):
        self.number, self.red, self.green, self.blue, self.white, self.index, self.normred, self.normgreen, self.normblue = number, red, green, blue, white, index, normred, normgreen, normblue

class PassiveColor:
    #also holds raw mode data
    def __init__(self, red, green, blue, white):
        self.red, self.green, self.blue, self.white = red, green, blue, white

class Colorv2(BaseDigitalSensor):
    """Object for HiTechnic Color v2 Sensors. Coded to HiTechnic's specs for the sensor
but not tested. Please report whether this worked for you or not!"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'mode': (0x41, 'B'),
        'number': (0x42, 'B'),
        'red': (0x43, 'B'),
        'green': (0x44, 'B'),
        'blue': (0x45, 'B'),
        'white': (0x46, 'B')
        'index': (0x47, 'B'),
        'normred': (0x48, 'B'),
        'normgreen': (0x49, 'B'),
        'normblue': (0x4A, 'B'),
        'all_data': (0x42, '9B'),
        'rawred': (0x42, '<H'),
        'rawgreen': (0x44, '<H'),
        'rawblue': (0x46, '<H'),
        'rawwhite': (0x48, '<H'),
        'all_raw_data': (0x42, '<4H')
    })
    
    def __init__(self, brick, port, check_compatible=False):
        super(Colorv2, self).__init__(brick, port, check_compatible)

    def get_active_color(self):
        """"Returns color values when in active mode.
        """
        number, red, green, blue, white, index, normred, normgreen, normblue = self.read_value('all_data')
        return ActiveColor(number, red, green, blue, white, index, normred, normgreen, normblue)
    
    get_sample = get_active_color
    
    def get_passive_color(self):
        """"Returns color values when in passive or raw mode.
        """
        red, green, blue, white = self.read_value('all_raw_data')
        return PassiveColor(red, green, blue, white)
    
    def get_mode(self):
        return self.read_value('mode')
    
    def set_mode(self, mode)
        self.write_value('mode', (mode, ))

Colorv2.add_compatible_sensor(None, 'HiTechnc', 'ColorPD')
Colorv2.add_compatible_sensor(None, 'HITECHNC', 'ColorPD')
Colorv2.add_compatible_sensor(None, 'HiTechnc', 'ColorPD ')
Colorv2.add_compatible_sensor(None, 'HITECHNC', 'ColorPD ')


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
