# nxt.sensor.generic module -- Classes to read LEGO Mindstorms NXT sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira
# Copyright (C) 2009  rhn
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

from time import sleep
from .common import *
from .digital import BaseDigitalSensor
from .analog import BaseAnalogSensor


class TouchReading:
    def __init__(self, raw_reading):
        self.raw = raw_reading
        self.pressed = bool(raw_reading.scaled_value)


class Touch(BaseAnalogSensor):
    """The LEGO touch sensor"""
    ReadingClass = TouchReading
    def __init__(self, brick, port):
        super(Touch, self).__init__(brick, port)
        self.set_input_mode(Type.SWITCH, Mode.BOOLEAN)


class LightReading:
    def __init__(self, raw_reading):
        self.raw = raw_reading
        self.lightness = raw_reading.scaled_value
        #self.lightness_lumens = raw_reading.raw_value * magical_lumen_factor


class Light(BaseAnalogSensor):
    'Object for light sensors'
    ReadingClass = LightReading
    def __init__(self, brick, port):
        super(Sensor, self).__init__(brick, port)
        self.set_illuminated(True)

    def set_illuminated(self, active):
        if active:
            type_ = Type.LIGHT_ACTIVE
        else:
            type_ = Type.LIGHT_INACTIVE
        self.set_input_mode(type_, Mode.RAW)
	

class SoundReading:
    def __init__(self, raw_reading):
        self.raw = raw_reading
        self.loudness = raw_reading.scaled_value


class Sound(BaseAnalogSensor):
    'Object for sound sensors'
    ReadingClass = SoundReading
    def __init__(self, brick, port):
        super(Sound, self).__init__(brick, port)
        self.set_adjusted(True)

    def set_adjusted(self, active):
        if active:
            type_ = Type.SOUND_DBA
        else:
            type_ = Type.SOUND_DB
        self.set_input_mode(type_, Mode.RAW)
	    

class Ultrasonic(BaseDigitalSensor):
    'Object for ultrasonic sensors'

    # I2C addresses for an Ultrasonic sensor
    I2C_ADDR = {'continuous_measurement_interval': (0x40, 'B'),
    	'command_state': (0x41, 'B'),
    	'measurement_byte_0': (0x42, 'B'),
    	'measurements': (0x42, 'B' * 8),
    	'actual_scale_factor': (0x51, 'B'),
    	'actual_scale_divisor': (0x52, 'B'),
    }

    def __init__(self, brick, port):
        super(Ultrasonic, self).__init__(brick, port)
        self.set_input_mode(Type.LOW_SPEED_9V, Mode.RAW)
        sleep(0.1)  # Give I2C time to initialize

    def get_distance(self):
        'Function to get data from the ultrasonic sensor'
        return self.read_value('measurement_byte_0')[0]
		
    def get_all_measurements(self):
        "Returns all the past readings in measurement_byte_0 through 7"
        return self.read_value('measurements')
    
    def get_measurement_no(self, number):
        "Returns measurement_byte_number"
        if not 0 <= number < 8:
            raise ValueError('Measurements are numbered 0 to 7, not' + str(number))
        base_address, format = self.I2C_ADDR['measurement_byte_0']
        return self._i2c_query(base_address + number, format)
