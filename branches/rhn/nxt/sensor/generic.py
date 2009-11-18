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


class _MetaUS(nxt.sensor._Meta):
	'Metaclass which adds accessor methods for US I2C addresses'

	def __init__(cls, name, bases, dict):
		super(_MetaUS, cls).__init__(name, bases, dict)
		for address in I2C_ADDRESS_US:
			name, n_bytes, set_method = I2C_ADDRESS_US[address]
			q = nxt.sensor._make_query(address, n_bytes)
			setattr(cls, 'get_' + name, q)
			if set_method:
				c = nxt.sensor._make_command(address)
				setattr(cls, 'set_' + name, c)


class UltrasonicSensor(nxt.sensor.DigitalSensor):
	'Object for ultrasonic sensors'

	__metaclass__ = _MetaUS

	def __init__(self, brick, port):
		super(UltrasonicSensor, self).__init__(brick, port)
		self.sensor_type = nxt.sensor.Type.LOW_SPEED_9V
		self.mode = nxt.sensor.Mode.RAW
		self.set_input_mode()
		sleep(0.1)  # Give I2C time to initialize

	def get_sample(self):
		'Function to get data from ultrasonic sensors, synonmous to self.get_sample()'
		self.set_command_state(nxt.sensor.CommandState.SINGLE_SHOT)
		return self.get_measurement_byte_0()
		


