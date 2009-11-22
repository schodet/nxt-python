# nxt.sensor.mindsensors module -- Classes implementing Mindsensors sensors
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


from .common import *
from .digital import BaseDigitalSensor, SensorInfo
from .analog import BaseAnalogSensor


class SumoEyesReading:
    """Contains the reading of SumoEyes sensor. left and right can be True or
    False. If True, then there is something there, if False, then it's empty
    there.
    """
    def __init__(self, raw_reading):
        self.raw = raw_reading
        val = raw_reading.normalized_ad_value # FIXME: make it rely on raw_ad_value
        right = 600 < val < 700
        both = 700 <= val < 900
        left = 300 < val < 400
        self.left = left or both
        self.right = right or both
    
    def __str__(self):
        return '(left: ' + str(self.left) + ', right: ' + str(self.right) + ')'

class SumoEyes(BaseAnalogSensor):
    """The class to control Mindsensors Sumo sensor. Warning: long range not
    working for my sensor.
    """
    #range: 5-10cm
    def __init__(self, brick, port, long_range=False):
        super(SumoEyes, self).__init__(brick, port)
        self.set_long_range(long_range)
        
    def set_long_range(self, val):
        """Sets if the sensor should operate in long range mode (12 inches) or
        the short range mode (6 in). val should be True or False.
        """
        if val:
            type_ = Type.LIGHT_INACTIVE
        else:
            type_ = Type.LIGHT_ACTIVE
        self.set_input_mode(type_, Mode.RAW)
    
    def get_sample(self):
        """Returns the processed meaningful values of the sensor"""
        return SumoEyesReading(self.get_input_values())
    

        
class CompassCommand(object):
    'Namespace for enumeration compass sensor commands'
    # NOTE: just a namespace (enumeration)
    AUTO_TRIG_ON = (0x41, 0x02)
    AUTO_TRIG_OFF = (0x53, 0x01)
    MAP_HEADING_BYTE = 0x42        # map heading to 0-255 range
    MAP_HEADING_INTEGER = 0x49    # map heading to 0-36000 range
    SAMPLING_50_HZ = 0x45        # set sampling frequency to 50 Hz
    SAMPLING_60_HZ = 0x55        # set sampling frequency to 60 Hz
    SET_ADPA_MODE_ON = 0x4E        # set ADPA mode on
    SET_ADPA_MODE_OFF = 0x4F    # set ADPA mode off
    BEGIN_CALIBRATION = 0x43    # begin calibration
    DONE_CALIBRATION = 0x44        # done with calibration
    LOAD_USER_CALIBRATION = 0x4C    # load user calibration value


class Compass(BaseDigitalSensor):
    """Warning! Likely to be broken because of no access to the hardware.
    If it doesn't work, contact me at nxpygoac.rhn@porcupinefactory.org
    """
    # TODO: ADPA, calibration
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command': (0x41, 'B'),
        'heading': (0x42, '<H'),
        'x_offset': (0x44, '<H'),
        'y_offset': (0x46, '<H'),
        'x_range': (0x48, '<H'),
        'y_range': (0x4A, '<H'),
        'x_raw': (0x4C, '<H'),
        'y_raw': (0x4E, '<H'),
    })

    def __init__(self, brick, port, check_compatible=False):
        super(Compass, self).__init__(brick, port, check_compatible)
        self.write_value('command', (CompassCommand.MAP_HEADING_INTEGER, )) # is this necessary?
    
    def get_heading(self):
        return self.read_value('heading')[0]
        
    get_sample = get_heading
    
    def set_sampling_frequency(self, frequency):
        if frequency == 60:
            command = CompassCommand.SAMPLING_60_HZ
        elif frequency == 50:
            command = CompassCommand.SAMPLING_50_HZ
        else:
            raise ValueError('Only 50 or 60 [Hz] supported')
        self.write_value('command', (command, ))


class IRLong(BaseDigitalSensor):
    """Class for the Long Distance Infrared Sensor"""
    # TODO: data point upload, ADPA
    
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'command': (0x41, 'B'),
                        'distance': (0x42, '<H'),
                        'voltage': (0x44, '<H'),
                        'type': (0x50, 'B'),
                        'no_of_data_points': (0x51, 'B'),
                        'min_distance': (0x52, '<H'),
                        'max_distance': (0x54, '<H'),
    })
    
    def get_distance(self):
        return self.read_value('distance')[0]

    get_sample = get_distance

    def get_type(self):
        return self.read_value('type')[0]
        
    def get_voltage(self):
        return self.read_value('voltage')[0]
    
    def get_min_distance(self):
        return self.read_value('min_distance')[0]
        
    def get_max_distance(self):
        return self.read_value('max_distance')[0]

IRLong.add_compatible_sensor('V1.20', 'mndsnsrs', 'DIST')
