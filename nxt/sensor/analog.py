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

import nxt.sensor


class RawReading:
    """A object holding the raw sensor values for a sensor."""

    def __init__(self, values):
        (
            self.port,
            self.valid,
            self.calibrated,
            self.sensor_type,
            self.mode,
            self.raw_value,
            self.normalized_value,
            self.scaled_value,
            self.calibrated_value,
        ) = values

    def __repr__(self):
        return str(
            (
                self.port,
                self.valid,
                self.calibrated,
                self.sensor_type,
                self.mode,
                self.raw_value,
                self.normalized_value,
                self.scaled_value,
                self.calibrated_value,
            )
        )


class BaseAnalogSensor(nxt.sensor.Sensor):
    """Object for analog sensors."""

    def get_input_values(self):
        """Get raw sensor readings.

        :return: An object with the read values.
        :rtype: RawReading
        """
        return RawReading(self._brick.get_input_values(self._port))

    def reset_input_scaled_value(self):
        """Reset sensor scaled value.

        This can be used to reset accumulated value for some sensor modes.
        """
        self._brick.reset_input_scaled_value(self._port)
