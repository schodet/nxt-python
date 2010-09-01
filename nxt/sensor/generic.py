# nxt.sensor.generic module -- Classes to read LEGO Mindstorms NXT sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010  melducky, Marcus Wanner
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


class Touch(BaseAnalogSensor):
    """The LEGO touch sensor"""

    def __init__(self, brick, port):
        super(Touch, self).__init__(brick, port)
        self.set_input_mode(Type.SWITCH, Mode.BOOLEAN)
    
    def is_pressed(self):
        return bool(self.get_input_values().scaled_value)
    
    get_sample = is_pressed


class Light(BaseAnalogSensor):
    """Object for light sensors. It automatically turns off light when it's not
    used.
    """
    # TODO: A program may be running in the background. Leave the turning off to the user?
    def __init__(self, brick, port, illuminated=True):
        super(Light, self).__init__(brick, port)
        self.set_illuminated(illuminated)

    def set_illuminated(self, active):
        if active:
            type_ = Type.LIGHT_ACTIVE
        else:
            type_ = Type.LIGHT_INACTIVE
        self.set_input_mode(type_, Mode.RAW)

    def get_lightness(self):
        return self.get_input_values().scaled_value	
    
    get_sample = get_lightness
    
    def __del__(self):
        self.set_illuminated(False)


class Sound(BaseAnalogSensor):
    'Object for sound sensors'

    def __init__(self, brick, port, adjusted=True):
        super(Sound, self).__init__(brick, port)
        self.set_adjusted(adjusted)

    def set_adjusted(self, active):
        if active:
            type_ = Type.SOUND_DBA
        else:
            type_ = Type.SOUND_DB
        self.set_input_mode(type_, Mode.RAW)
    
    def get_loudness(self):
        return self.get_input_values().scaled_value
    
    get_sample = get_loudness
	

class Ultrasonic(BaseDigitalSensor):
    """Object for ultrasonic sensors"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'measurement_units': (0x14, '7s'),
        'continuous_measurement_interval': (0x40, 'B'),
        'command_state': (0x41, 'B'),
        'measurement_byte_0': (0x42, 'B'),
        'measurements': (0x42, 'B' * 8),
        'actual_scale_factor': (0x51, 'B'),
        'actual_scale_divisor': (0x52, 'B'),
    })

    def __init__(self, brick, port, check_compatible=True):
        super(Ultrasonic, self).__init__(brick, port, check_compatible)
        self.set_input_mode(Type.LOW_SPEED_9V, Mode.RAW)

    def get_distance(self):
        'Function to get data from the ultrasonic sensor'
        return self.read_value('measurement_byte_0')[0]
    
    get_sample = get_distance
            
    def get_measurement_units(self):
        return self.read_value('measurement_units')[0].split('\0')[0]

    def get_all_measurements(self):
        "Returns all the past readings in measurement_byte_0 through 7"
        return self.read_value('measurements')
    
    def get_measurement_no(self, number):
        "Returns measurement_byte_number"
        if not 0 <= number < 8:
            raise ValueError('Measurements are numbered 0 to 7, not ' + str(number))
        base_address, format = self.I2C_ADDRESS['measurement_byte_0']
        return self._i2c_query(base_address + number, format)[0]

Ultrasonic.add_compatible_sensor(None, 'LEGO', 'Sonar') #Tested with version 'V1.0'


class Color20(BaseAnalogSensor):
    def __init__(self, brick, port):
        super(Color20, self).__init__(brick, port)
        self.set_light_color(Type.COLORFULL)

    def set_light_color(self, color):
        """color should be one of the COLOR* Type namespace values, e.g. Type.COLORBLUE"""
        self.set_input_mode(color, Mode.RAW)

    def get_light_color(self):
        """Returns one of the COLOR* Type namespace values, e.g. Type.COLORRED"""
        return self.get_input_values().sensor_type

    def get_reflected_light(self, color):
        self.set_light_color(color)
        return self.get_input_values().scaled_value
    
    def get_color(self):
        self.get_reflected_light(Type.COLORFULL)
        return self.get_input_values().scaled_value
    
    get_sample = get_color
