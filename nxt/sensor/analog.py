# nxt.sensor.analog module -- submodule for use with analog sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2021  Nicolas Schodet
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

import time
from dataclasses import dataclass

import nxt.sensor


class InvalidReading(Exception):
    """Exception raised on timeout trying to get valid readings."""

    pass


@dataclass
class RawReading:
    """A object holding the raw sensor values for a sensor."""

    #: Input port identifier.
    port: nxt.sensor.Port
    #: ``True`` if the value is valid, else ``False``.
    valid: bool
    #: Always ``False``, there is no calibration in NXT firmware.
    calibrated: bool
    #: Sensor type.
    sensor_type: nxt.sensor.Type
    #: Sensor mode.
    sensor_mode: nxt.sensor.Mode
    #: Raw analog to digital converter value.
    raw_value: int
    #: Normalized value.
    normalized_value: int
    #: Scaled value.
    scaled_value: int
    #: Always normalized value, there is no calibration in NXT firmware.
    calibrated_value: int


class BaseAnalogSensor(nxt.sensor.Sensor):
    """Object for analog sensors."""

    def get_input_values(self):
        """Get raw sensor readings.

        :return: An object with the read values.
        :rtype: RawReading
        """
        return RawReading(*self._brick.get_input_values(self._port))

    def get_valid_input_values(self):
        """Wait until input is valid, then get raw sensor readings.

        :return: An object with the read values.
        :rtype: RawReading
        :raises InvalidReading: On timeout trying to get valid readings.
        """
        tries = 10
        tries_delay_s = 0.1
        readings = self.get_input_values()
        while not readings.valid:
            tries -= 1
            if tries == 0:
                raise InvalidReading()
            time.sleep(tries_delay_s)
            readings = self.get_input_values()
        return readings

    def reset_input_scaled_value(self):
        """Reset sensor scaled value.

        This can be used to reset accumulated value for some sensor modes.
        """
        self._brick.reset_input_scaled_value(self._port)
