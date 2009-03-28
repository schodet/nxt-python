# nxt.sensor module -- Classes to read LEGO Mindstorms NXT sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from time import sleep
from nxt.error import I2CError, I2CPendingError

PORT_1 = 0x00
PORT_2 = 0x01
PORT_3 = 0x02
PORT_4 = 0x03

class Type(object):
	'Namespace for enumeration of the type of sensor'
	# NOTE: just a namespace (enumeration)
	NO_SENSOR = 0x00
	SWITCH = 0x01       # Touch sensor
	TEMPERATURE = 0x02
	REFLECTION = 0x03
	ANGLE = 0x04
	LIGHT_ACTIVE = 0x05 # Light sensor (illuminated)
	LIGHT_INACTIVE = 0x06   # Light sensor (ambient)
	SOUND_DB = 0x07     # Sound sensor (unadjusted)
	SOUND_DBA = 0x08    # Sound sensor (adjusted)
	CUSTOM = 0x09
	LOW_SPEED = 0x0A
	LOW_SPEED_9V = 0x0B # Low-speed I2C (Ultrasonic sensor)

class Mode(object):
	'Namespace for enumeration of the mode of sensor'
	# NOTE: just a namespace (enumeration)
	RAW = 0x00
	BOOLEAN = 0x20
	TRANSITION_CNT = 0x40
	PERIOD_COUNTER = 0x60
	PCT_FULL_SCALE = 0x80
	CELSIUS = 0xA0
	FAHRENHEIT = 0xC0
	ANGLE_STEPS = 0xE0
	MASK = 0xE0
	MASK_SLOPE = 0x1F   # Why isn't this slope thing documented?

class Sensor(object):
	'Main sensor object'

	def __init__(self, brick, port):
		self.brick = brick
		self.port = port
		self.sensor_type = Type.NO_SENSOR
		self.mode = Mode.RAW

	def set_input_mode(self):
		self.brick.set_input_mode(self.port, self.sensor_type,
			self.mode)

class AnalogSensor(Sensor):
	'Object for analog sensors'

	def __init__(self, brick, port):
		super(AnalogSensor, self).__init__(brick, port)
		self.valid = False
		self.calibrated = False
		self.raw_ad_value = 0
		self.normalized_ad_value = 0
		self.scaled_value = 0
		self.calibrated_value = 0

	def get_input_values(self):
		values = self.brick.get_input_values(self.port)
		(self.port, self.valid, self.calibrated, self.sensor_type,
			self.mode, self.raw_ad_value, self.normalized_ad_value,
			self.scaled_value, self.calibrated_value) = values
		return values

	def reset_input_scaled_value(self):
		self.brick.reset_input_scaled_value()

	def get_sample(self):
		self.get_input_values()
		return self.scaled_value

class TouchSensor(AnalogSensor):
	'Object for touch sensors'

	def __init__(self, brick, port):
		super(TouchSensor, self).__init__(brick, port)
		self.sensor_type = Type.SWITCH
		self.mode = Mode.BOOLEAN
		self.set_input_mode()

	def is_pressed(self):
		return bool(self.scaled_value)

	def get_sample(self):
		self.get_input_values()
		return self.is_pressed()

class LightSensor(AnalogSensor):
	'Object for light sensors'

	def __init__(self, brick, port):
		super(LightSensor, self).__init__(brick, port)
		self.set_illuminated(True)

	def set_illuminated(self, active):
		if active:
			self.sensor_type = Type.LIGHT_ACTIVE
		else:
			self.sensor_type = Type.LIGHT_INACTIVE
		self.set_input_mode()

class SoundSensor(AnalogSensor):
	'Object for sound sensors'

	def __init__(self, brick, port):
		super(SoundSensor, self).__init__(brick, port)
		self.set_adjusted(True)

	def set_adjusted(self, active):
		if active:
			self.sensor_type = Type.SOUND_DBA
		else:
			self.sensor_type = Type.SOUND_DB
		self.set_input_mode()

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
		data = self.i2c_query(address, n_bytes)
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

class DigitalSensor(Sensor):
	'Object for digital sensors'

	__metaclass__ = _Meta

	I2C_DEV = 0x02

	def __init__(self, brick, port):
		super(DigitalSensor, self).__init__(brick, port)

	def _ls_get_status(self, n_bytes):
		for n in range(3):
			try:
				b = self.brick.ls_get_status(self.port)
				if b >= n_bytes:
					return b
			except I2CPendingError:
				sleep(0.01)
		raise I2CError, 'ls_get_status timeout'

	def i2c_command(self, address, value):
		msg = chr(DigitalSensor.I2C_DEV) + chr(address) + chr(value)
		self.brick.ls_write(self.port, msg, 0)

	def i2c_query(self, address, n_bytes):
		msg = chr(DigitalSensor.I2C_DEV) + chr(address)
		self.brick.ls_write(self.port, msg, n_bytes)
		self._ls_get_status(n_bytes)
		data = self.brick.ls_read(self.port)
		if len(data) < n_bytes:
			raise I2CError, 'Read failure'
		return data[-n_bytes:]

class CommandState(object):
	'Namespace for enumeration of the command state of sensors'
	# NOTE: just a namespace (enumeration)
	OFF = 0x00
	SINGLE_SHOT = 0x01
	CONTINUOUS_MEASUREMENT = 0x02
	EVENT_CAPTURE = 0x03 # Check for ultrasonic interference
	REQUEST_WARM_RESET = 0x04

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

def _make_command(address):
	def command(self, value):
		self.i2c_command(address, value)
	return command

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

class UltrasonicSensor(DigitalSensor):
	'Object for ultrasonic sensors'

	__metaclass__ = _MetaUS

	def __init__(self, brick, port):
		super(UltrasonicSensor, self).__init__(brick, port)
		self.sensor_type = Type.LOW_SPEED_9V
		self.mode = Mode.RAW
		self.set_input_mode()
		sleep(0.1)  # Give I2C time to initialize

	def get_single_shot_measurement(self):
		'Function to get data from ultrasonic sensors, synonmous to self.get_sample()'
		self.set_command_state(CommandState.SINGLE_SHOT)
		return self.get_measurement_byte_0()

UltrasonicSensor.get_sample = UltrasonicSensor.get_measurement_byte_0

class AccelerometerSensor(DigitalSensor):
	'Object for Accelerometer sensors. Thanks to Paulo Vieira.'

	__metaclass__ = _MetaUS

	def __init__(self, brick, port):
		super(AccelerometerSensor, self).__init__(brick, port)
		self.sensor_type = Type.LOW_SPEED_9V
		self.mode = Mode.RAW
		self.set_input_mode()
		sleep(0.1)  # Give I2C time to initialize

		def get_sample(self):
			self.set_command_state(CommandState.SINGLE_SHOT)
			outbuf = [0,0,0,0,0,0]
			# Upper X, Y, Z
			outbuf[0] = self.get_measurement_byte_0()
			outbuf[1] = self.get_measurement_byte_1()
			outbuf[2] = self.get_measurement_byte_2()
			# Lower X, Y, Z
			outbuf[3] = self.get_measurement_byte_3()
			outbuf[4] = self.get_measurement_byte_4()
			outbuf[5] = self.get_measurement_byte_5()
			self.xval = outbuf[0]
			if self.xval > 127:
				self.xval -= 256
			self.xval = self.xval * 4 + outbuf[3]

			self.yval = outbuf[1]
			if self.yval > 127:
				self.yval -= 256
			self.yval = self.yval * 4 + outbuf[4]

			self.zval = outbuf[2]
			if self.zval > 127:
				self.zval -= 256
			self.zval = self.zval * 4 + outbuf[5]

			self.xval = float(self.xval)/200
			self.yval = float(self.yval)/200
			self.zval = float(self.zval)/200

			return self.xval, self.yval, self.zval

