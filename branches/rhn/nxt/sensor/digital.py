# nxt.sensor module -- Classes to read LEGO Mindstorms NXT sensors
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

from nxt.error import I2CError, I2CPendingError

from common import *
from time import sleep
import struct


class BaseDigitalSensor(Sensor):
	"""Object for digital sensors. I2C_ADDRESS is the dictionary storing name
	to	i2c address mappings. It should be updated in every subclass.
	"""
	I2C_DEV = 0x02
    I2C_ADDRESS = {'version': (0x00, '8s'),
        'product_id': (0x08, '8s'),
        'sensor_type': (0x10, '8s'),
#        0x11: ('factory_zero', 1),      # is this really correct?
        'factory_scale_factor': (0x12, 'B'),
        'factory_scale_divisor': (0x13, 'B'),
        'measurement_units': (0x14, '7s'),
    }
    
	def __init__(self, brick, port):
		super(BaseDigitalSensor, self).__init__(brick, port)
		self.set_input_mode(Type.LOW_SPEED_9V, Mode.RAW)
		sleep(0.1)  # Give I2C time to initialize

	def _ls_get_status(self, n_bytes):
		for n in range(3):
			try:
				b = self.brick.ls_get_status(self.port)
				if b >= n_bytes:
					return b
			except I2CPendingError:
				sleep(0.01)
		raise I2CError, 'ls_get_status timeout'

	def _i2c_command(self, address, value, format):
		"""Writes an i2c value to the given address. value must be a string. value is
		a tuple of values corresponding to the given format.
		"""
		value = struct.pack(fmt, value)
		msg = chr(self.I2C_DEV) + chr(address) + chr(value)
		self.brick.ls_write(self.port, msg, 0)

	def _i2c_query(self, address, format):
		"""Reads an i2c value from given address, and returns a value unpacked
		according to the given format. Format is the same as in the struct
		module.
		"""
		n_bytes = struct.calcsize(format)
		msg = chr(self.I2C_DEV) + chr(address)
		self.brick.ls_write(self.port, msg, n_bytes)
		self._ls_get_status(n_bytes)
		data = self.brick.ls_read(self.port)
		if len(data) < n_bytes:
			raise I2CError, 'Read failure'
		return struct.unpack(format, data[-n_bytes:]) # TODO: why could there be more than n_bytes? 
		
	def read_value(self, name):
	    """Reads an value from the sensor. Name must be a string found in
	    self.I2C_ADDRESS dictionary. Entries in self.I2C_ADDRESS are in the
	    name: (address, format) form, with format as in the struct module.
	    """
	    address, fmt = self.I2C_ADDRESS[name]
	    return self._i2c_query(address, fmt)

	def write_value(self, name, value):
	    """Writes value to the sensor. Name must be a string found in
		self.I2C_ADDRESS dictionary. Entries in self.I2C_ADDRESS are in the
		name: (address, format) form, with format as in the struct module.
		value is a tuple of values corresponding to the format from
		self.I2C_ADDRESS dictionary.
		"""
		address, fmt = self.I2C_ADDRESS[address]
		self._i2c_command(address, value, fmt)
		
	def get_version(self):
	    return self.read_value('version')
	
	def get_vendor(self):
	    return self.read_value('product_id')
	    
	def get_sensor_type(self):
	    return self.read_value('sensor_type')
	    
	def get_measurement_units(self):
	    return self.read_value('measurement_units')
	    

class CommandState(object):
	'Namespace for enumeration of the command state of sensors'
	# NOTE: just a namespace (enumeration)
	OFF = 0x00
	SINGLE_SHOT = 0x01
	CONTINUOUS_MEASUREMENT = 0x02
	EVENT_CAPTURE = 0x03 # Check for ultrasonic interference
	REQUEST_WARM_RESET = 0x04

