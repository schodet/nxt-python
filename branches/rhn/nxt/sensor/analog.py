# nxt.sensor.analog module -- submodule for use with analog sensors
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

from common import *

class BaseAnalogSensor(Sensor):
	'Object for analog sensors'

	def __init__(self, brick, port):
		super(BaseAnalogSensor, self).__init__(brick, port)
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

