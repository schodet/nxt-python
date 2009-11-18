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

import nxt.sensor
from time import sleep
from .common import *
from .digital import _Meta, BaseDigitalSensor, _make_query, _make_command, CommandState
from .analog import BaseAnalogSensor
# so many to keep track of how many is left. ideally, only BaseDigitalSensor needs to be imported


class Touch(BaseAnalogSensor):
	"""The LEGO touch sensor"""

	def __init__(self, brick, port):
		super(Touch, self).__init__(brick, port)
		self.sensor_type = Type.SWITCH
		self.mode = Mode.BOOLEAN
		self.set_input_mode()

	def is_pressed(self):
		return bool(self.scaled_value)

	def get_sample(self):
		self.get_input_values()
		return self.is_pressed()


class Light(BaseAnalogSensor):
	'Object for light sensors'

	def __init__(self, brick, port):
		super(Sensor, self).__init__(brick, port)
		self.set_illuminated(True)

	def set_illuminated(self, active):
		if active:
			self.sensor_type = Type.LIGHT_ACTIVE
		else:
			self.sensor_type = Type.LIGHT_INACTIVE
		self.set_input_mode()


class Sound(AnalogSensor):
	'Object for sound sensors'

	def __init__(self, brick, port):
		super(Sound, self).__init__(brick, port)
		self.set_adjusted(True)

	def set_adjusted(self, active):
		if active:
			self.sensor_type = Type.SOUND_DBA
		else:
			self.sensor_type = Type.SOUND_DB
		self.set_input_mode()



# I2C addresses for an Ultrasonic sensor
I2C_ADDRESS_US = {
	0x40: ('continuous_measurement_interval', 1, True),
	0x41: ('command_state', 1, True),
	0x42: ('measurement_byte_0', 1, False),
	0x43: ('measurement_byte_1', 1, False),
	0x44: ('measurement_byte_2', 1, False),
	0x45: ('measurement_byte_3', 1, False),
	0x46: ('measurement_byte_4', 1, False),
	0x47: ('measurement_byte_5', 1, False),
	0x48: ('measurement_byte_6', 1, False),
	0x49: ('measurement_byte_7', 1, False),
	0x50: ('actual_zero', 1, True),
	0x51: ('actual_scale_factor', 1, True),
	0x52: ('actual_scale_divisor', 1, True),
}


class _MetaUS(_Meta):
	'Metaclass which adds accessor methods for US I2C addresses'

	def __init__(cls, name, bases, dict):
		super(_MetaUS, cls).__init__(name, bases, dict)
		for address in I2C_ADDRESS_US:
			name, n_bytes, set_method = I2C_ADDRESS_US[address]
			q = _make_query(address, n_bytes)
			setattr(cls, 'get_' + name, q)
			if set_method:
				c = _make_command(address)
				setattr(cls, 'set_' + name, c)


class Ultrasonic(BaseDigitalSensor):
	'Object for ultrasonic sensors'

	__metaclass__ = _MetaUS

	def __init__(self, brick, port):
		super(Ultrasonic, self).__init__(brick, port)
		self.sensor_type = Type.LOW_SPEED_9V
		self.mode = Mode.RAW
		self.set_input_mode()
		sleep(0.1)  # Give I2C time to initialize

	def get_sample(self):
		'Function to get data from ultrasonic sensors, synonmous to self.get_sample()'
		self.set_command_state(CommandState.SINGLE_SHOT)
		return self.get_measurement_byte_0()
		



I2C_ADDRESS_ACC = {
	0x40: ('continuous_measurement_interval', 1, True),
	0x41: ('command_state', 1, True),
	0x42: ('measurement_byte_0', 1, False),
	0x43: ('measurement_byte_1', 1, False),
	0x44: ('measurement_byte_2', 1, False),
	0x45: ('measurement_byte_3', 1, False),
	0x46: ('measurement_byte_4', 1, False),
	0x47: ('measurement_byte_5', 1, False),
	0x48: ('measurement_byte_6', 1, False),
	0x49: ('measurement_byte_7', 1, False),
	0x50: ('actual_zero', 1, True),
	0x51: ('actual_scale_factor', 1, True),
	0x52: ('actual_scale_divisor', 1, True),
}


class _MetaAcc(_Meta):
	'Metaclass which adds accessor methods for US I2C addresses'

	def __init__(cls, name, bases, dict):
		super(_MetaAcc, cls).__init__(name, bases, dict)
		for address in I2C_ADDRESS_ACC:
			name, n_bytes, set_method = I2C_ADDRESS_ACC[address]
			q = _make_query(address, n_bytes)
			setattr(cls, 'get_' + name, q)
			if set_method:
				c = _make_command(address)
				setattr(cls, 'set_' + name, c)


class Accelerometer(BaseDigitalSensor):
	'Object for Accelerometer sensors. Thanks to Paulo Vieira.'

	__metaclass__ = _MetaAcc

	def __init__(self, brick, port):
		super(Accelerometer, self).__init__(brick, port)
		self.sensor_type = Type.LOW_SPEED_9V
		self.mode = Mode.RAW
		self.set_input_mode()
		sleep(0.1)  # Give I2C time to initialize

	def get_sample(self):
		self.set_command_state(CommandState.SINGLE_SHOT)
		out_buffer = [0,0,0,0,0,0]
		# Upper X, Y, Z
		out_buffer[0] = self.get_measurement_byte_0()
		out_buffer[1] = self.get_measurement_byte_1()
		out_buffer[2] = self.get_measurement_byte_2()
		# Lower X, Y, Z
		out_buffer[3] = self.get_measurement_byte_3()
		out_buffer[4] = self.get_measurement_byte_4()
		out_buffer[5] = self.get_measurement_byte_5()
		self.xval = out_buffer[0]
		if self.xval > 127:
			self.xval -= 256
		self.xval = self.xval * 4 + out_buffer[3]

		self.yval = out_buffer[1]
		if self.yval > 127:
			self.yval -= 256
		self.yval = self.yval * 4 + out_buffer[4]

		self.zval = out_buffer[2]
		if self.zval > 127:
			self.zval -= 256
		self.zval = self.zval * 4 + out_buffer[5]

		self.xval = float(self.xval)/200
		self.yval = float(self.yval)/200
		self.zval = float(self.zval)/200

		return self.xval, self.yval, self.zval

