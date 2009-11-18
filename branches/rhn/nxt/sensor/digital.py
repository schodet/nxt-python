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

I2C_ADDRESS = {
	0x00: ('version', 8),
	0x08: ('product_id', 8),
	0x10: ('sensor_type', 8),
	0x11: ('factory_zero', 1),      # is this really correct?
	0x12: ('factory_scale_factor', 1),
	0x13: ('factory_scale_divisor', 1),
	0x14: ('measurement_units', 1),
}
def _make_query(address, n_bytes):
	def query(self):
		data = self._i2c_query(address, n_bytes)
		if n_bytes == 1:
			return ord(data)
		else:
			return data
	return query

class _Meta(type):
	'Metaclass which adds accessor methods for I2C addresses'

	def __init__(cls, name, bases, dict):
		super(_Meta, cls).__init__(name, bases, dict)
		for address in I2C_ADDRESS:
			name, n_bytes = I2C_ADDRESS[address]
			q = _make_query(address, n_bytes)
			setattr(cls, 'get_' + name, q)

class BaseDigitalSensor(Sensor):
	'Object for digital sensors'

	__metaclass__ = _Meta

	I2C_DEV = 0x02

	def __init__(self, brick, port):
		super(BaseDigitalSensor, self).__init__(brick, port)

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
		msg = chr(DigitalSensor.I2C_DEV) + chr(address) + chr(value)
		self.brick.ls_write(self.port, msg, 0)

	def _i2c_query(self, address, format):
		"""Reads an i2c value from given address, and returns a value unpacked
		according to the given format. Format is the same as in the struct
		module.
		"""
		n_bytes = struct.calcsize(format)
		msg = chr(DigitalSensor.I2C_DEV) + chr(address)
		self.brick.ls_write(self.port, msg, n_bytes)
		self._ls_get_status(n_bytes)
		data = self.brick.ls_read(self.port)
		if len(data) < n_bytes:
			raise I2CError, 'Read failure'
		return struct.unpack(format, data[-n_bytes:]) # TODO: why could there be more than n_bytes? 
		
	def read_value(self, name):
	    """Reads an value from the sensor. Name must be a string found in
	    self.I2C_ADDR dictionary. Entries in self.I2C_ADDR are in the
	    name: (address, format) form, with format as in the struct module.
	    """
	    address, fmt = self.I2C_ADDR[name]
	    return self._i2c_query(address, fmt)

	def write_value(self, name, value):
	    """Writes value to the sensor. Name must be a string found in
		self.I2C_ADDR dictionary. Entries in self.I2C_ADDR are in the
		name: (address, format) form, with format as in the struct module.
		value is a tuple of values corresponding to the format from
		self.I2C_ADDR dictionary.
		"""
		address, fmt = self.I2C_ADDR[address]
		self._i2c_command(address, value, fmt)
		

class CommandState(object):
	'Namespace for enumeration of the command state of sensors'
	# NOTE: just a namespace (enumeration)
	OFF = 0x00
	SINGLE_SHOT = 0x01
	CONTINUOUS_MEASUREMENT = 0x02
	EVENT_CAPTURE = 0x03 # Check for ultrasonic interference
	REQUEST_WARM_RESET = 0x04


def _make_command(address):
	def command(self, value):
		self._i2c_command(address, value)
	return command
