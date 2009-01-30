# nxt.compass module -- Classes to read Mindsensors Compass sensors
# Copyright (C) 2007  Douglas P Lau
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

import sensor
from time import sleep

class Command(object):
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

class _MetaCMPS_Nx(sensor._Meta):
	'Metaclass which adds accessor methods for CMPS-Nx I2C addresses'

	def __init__(cls, name, bases, dict):
		super(_MetaCMPS_Nx, cls).__init__(name, bases, dict)
		for address in I2C_ADDRESS_CMPS_NX:
			name, n_bytes, set_method = I2C_ADDRESS_CMPS_NX[address]
			q = sensor._make_query(address, n_bytes)
			setattr(cls, 'get_' + name, q)
			if set_method:
				c = sensor._make_command(address)
				setattr(cls, 'set_' + name, c)

class CompassSensor(sensor.DigitalSensor):

	__metaclass__ = _MetaCMPS_Nx

	def __init__(self, brick, port):
		super(CompassSensor, self).__init__(brick, port)
		self.sensor_type = Type.LOW_SPEED_9V
		self.mode = Mode.RAW
		self.set_input_mode()
		sleep(0.1)	# Give I2C time to initialize

CompassSensor.get_sample = CompassSensor.get_heading_lsb
