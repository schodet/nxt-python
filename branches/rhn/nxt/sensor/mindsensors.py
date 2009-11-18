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

import nxt.sensor
from time import sleep
from .common import *
from .digital import _Meta, BaseDigitalSensor, _make_query, _make_command
# so many to keep track of how many is left. ideally, only BaseDigitalSensor needs to be imported

class SumoEyesReading:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class SumoEyes(nxt.sensor.LightSensor):
    """The class to control Mindsensors Sumo sensor. Warning: long range not
    tested yet.
    """
    def set_long_range(self, val):
        """Sets if the sensor should operate in long range mode (12 inches) or
        the short range mode (6 in). val should be True or False.
        """
        self.set_illuminated(val)
    
    def get_input_values(self):
        """Returns a SumoReading"""
        rd = nxt.sensor.LightSensor.get_input_values(self)
        val = rd[6]
        raw = val
        right = 600 < val < 700
        both = 700 <= val < 900
        left = 300 < val < 400
        left = left or both
        right = right or both
        return SumoReading(left, right)
        
        
class Command(object):
        'Namespace for enumeration compass sensor commands'
	# NOTE: just a namespace (enumeration)
	AUTO_TRIG_ON = (0x41, 0x02)
	AUTO_TRIG_OFF = (0x53, 0x01)
	MAP_HEADING_BYTE = 0x42		# map heading to 0-255 range
	MAP_HEADING_INTEGER = 0x49	# map heading to 0-36000 range
	SAMPLING_50_HZ = 0x45		# set sampling frequency to 50 Hz
	SAMPLING_60_HZ = 0x55		# set sampling frequency to 60 Hz
	SET_ADPA_MODE_ON = 0x4E		# set ADPA mode on
	SET_ADPA_MODE_OFF = 0x4F	# set ADPA mode off
	BEGIN_CALIBRATION = 0x43	# begin calibration
	DONE_CALIBRATION = 0x44		# done with calibration
	LOAD_USER_CALIBRATION = 0x4C	# load user calibration value

# I2C addresses for a Mindsensors CMPS-Nx compass sensor
I2C_ADDRESS_CMPS_NX = {
	0x41: ('command', 1, True),
	0x42: ('heading_lsb', 1, False),
	0x43: ('heading_msb', 1, False),
	0x44: ('x_offset_lsb', 1, True),
	0x45: ('x_offset_msb', 1, True),
	0x46: ('y_offset_lsb', 1, True),
	0x47: ('y_offset_msb', 1, True),
	0x48: ('x_range_lsb', 1, True),
	0x49: ('x_range_msb', 1, True),
	0x4A: ('y_range_lsb', 1, True),
	0x4B: ('y_range_msb', 1, True),
	0x4C: ('x_raw_lsb', 1, True),
	0x4D: ('x_raw_msb', 1, True),
	0x4E: ('y_raw_lsb', 1, True),
	0x4F: ('y_raw_msb', 1, True),
}

class _MetaCMPS_Nx(_Meta):
	'Metaclass which adds accessor methods for CMPS-Nx I2C addresses'

	def __init__(cls, name, bases, dict):
		super(_MetaCMPS_Nx, cls).__init__(name, bases, dict)
		for address in I2C_ADDRESS_CMPS_NX:
			name, n_bytes, set_method = I2C_ADDRESS_CMPS_NX[address]
			q = _make_query(address, n_bytes)
			setattr(cls, 'get_' + name, q)
			if set_method:
				c = _make_command(address)
				setattr(cls, 'set_' + name, c)


class Compass(BaseDigitalSensor):
    """Warning! Likely to be broken because of no access to the hardware.
    If it doesn't work, contact me at nxpygoac.rhn@porcupinefactory.org
    """
	__metaclass__ = _MetaCMPS_Nx

	def __init__(self, brick, port):
		super(Compass, self).__init__(brick, port)
		self.sensor_type = Type.LOW_SPEED_9V
		self.mode = Mode.RAW
		self.set_input_mode()
		sleep(0.1)	# Give I2C time to initialize

Compass.get_sample = Compass.get_heading_lsb


class IRLong(BaseDigitalSensor):
    I2C_ADDR = {'command': (0x41, 'b'),
                        'distance': (0x42, '<H'),
                        'voltage': (0x44, '<H'),
                        'type': (0x50, 'b'),
                        'no_of_data_points': (0x51, 'b'),
                        'min_distance': (0x52, '<H'),
                        'max_distance': (0x54, '<H'),
    }
    
    def __init__(self, brick, port):
        super(IRLong, self).__init__(brick, port)
        self.sensor_type = Type.LOW_SPEED_9V
        self.mode = Mode.RAW
        self.set_input_mode()
        sleep(0.1)	# Give I2C time to initialize
    
    def get_distance(self):
        return self._i2c_query('distance')[0]

    def get_type(self):
        return self._i2c_query('type')[0]
        
    def get_voltage(self):
        return self._i2c_query('voltage')[0]
    
    def get_min_distance(self):
        return self._i2c_query('min_distance')[0]
        
    def get_max_distance(self):
        return self._i2c_query('max_distance')[0]

