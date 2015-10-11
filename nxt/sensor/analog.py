# nxt.sensor.analog module -- submodule for use with analog sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
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


class RawReading: # can be converted to the old version
    """A pseudo-structure holding the raw sensor values as returned by the NXT
    brick.
    """
    def __init__(self, values):
        (self.port, self.valid, self.calibrated, self.sensor_type, self.mode,
            self.raw_ad_value, self.normalized_ad_value, self.scaled_value,
            self.calibrated_value) = values
    
    def __repr__(self):
        return str((self.port, self.valid, self.calibrated, self.sensor_type, self.mode,
            self.raw_ad_value, self.normalized_ad_value, self.scaled_value,
            self.calibrated_value))
            

class BaseAnalogSensor(Sensor):
    """Object for analog sensors."""
    def get_input_values(self):
        """Returns the raw sensor values as returned by the NXT brick."""
        return RawReading(self.brick.get_input_values(self.port))

    def reset_input_scaled_value(self):
        self.brick.reset_input_scaled_value()

