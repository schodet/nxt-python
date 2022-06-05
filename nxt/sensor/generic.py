# nxt.sensor.generic module -- Support for LEGO Mindstorms NXT sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010  melducky, Marcus Wanner
# Copyright (C) 2022  Nicolas Schodet
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
"""The :mod:`nxt.sensor.generic` module supports the sensors manufactured by LEGO."""
import enum

from nxt.sensor import Mode, Type
from nxt.sensor.analog import BaseAnalogSensor
from nxt.sensor.digital import BaseDigitalSensor


class Touch(BaseAnalogSensor):
    """LEGO Mindstorms NXT touch sensor, part number 53793."""

    def __init__(self, brick, port):
        super().__init__(brick, port)
        self.set_input_mode(Type.SWITCH, Mode.BOOL)

    def is_pressed(self):
        """Get sensor pressed state.

        :return: ``True`` if the sensor is pressed, else ``False``.
        :rtype: bool
        """
        return bool(self.get_input_values().scaled_value)

    get_sample = is_pressed


class Light(BaseAnalogSensor):
    """LEGO Mindstorms NXT light sensor, part number 55969.

    This sensor is included in the first version of the Mindstorms NXT set and in the
    Education NXT set. Not to be confused with the color sensor included in the NXT 2.0
    set.

    :param bool illuminated: Initial illuminated state.
    """

    def __init__(self, brick, port, illuminated=True):
        super().__init__(brick, port)
        self.set_illuminated(illuminated)

    def set_illuminated(self, active):
        """Set illuminated state.

        :param bool active: ``True`` to activate light.
        """
        if active:
            type_ = Type.LIGHT_ACTIVE
        else:
            type_ = Type.LIGHT_INACTIVE
        self.set_input_mode(type_, Mode.RAW)

    def get_lightness(self):
        """Get detected light level.

        :return: Detected light level between 0 and 1023.
        :rtype: int
        """
        return self.get_input_values().scaled_value

    get_sample = get_lightness


class Sound(BaseAnalogSensor):
    """LEGO Mindstorms NXT sound sensor, part number 55963.

    :param bool adjusted: Initial adjusted state.
    """

    def __init__(self, brick, port, adjusted=True):
        super().__init__(brick, port)
        self.set_adjusted(adjusted)

    def set_adjusted(self, active):
        """Set adjusted state. When activated, the sensitivity of the sensor is adjusted
        to human perception.

        :param bool active: ``True`` to activate adjustment.
        """
        if active:
            type_ = Type.SOUND_DBA
        else:
            type_ = Type.SOUND_DB
        self.set_input_mode(type_, Mode.RAW)

    def get_loudness(self):
        """Get detected sound level.

        :return: Detected sound level between 0 and 1023.
        :rtype: int
        """
        return self.get_input_values().scaled_value

    get_sample = get_loudness


class Ultrasonic(BaseDigitalSensor):
    """LEGO Mindstorms NXT ultrasonic distance sensor, part number 53792."""

    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update(
        {
            "measurement_units": (0x14, "7s"),
            "continuous_measurement_interval": (0x40, "B"),
            "command": (0x41, "B"),
            "measurement_byte_0": (0x42, "B"),
            "measurement_byte_1": (0x43, "B"),
            "measurement_byte_2": (0x44, "B"),
            "measurement_byte_3": (0x45, "B"),
            "measurement_byte_4": (0x46, "B"),
            "measurement_byte_5": (0x47, "B"),
            "measurement_byte_6": (0x48, "B"),
            "measurement_byte_7": (0x49, "B"),
            "measurements": (0x42, "8B"),
            "actual_scale_factor": (0x51, "B"),
            "actual_scale_divisor": (0x52, "B"),
        }
    )

    class Command(enum.Enum):
        """Sensor command."""

        OFF = 0x00
        """Turn sensor OFF."""

        SINGLE_SHOT = 0x01
        """Enable single shot mode."""

        CONTINUOUS_MEASUREMENT = 0x02
        """Enable continuous measurement mode (default)."""

        EVENT_CAPTURE = 0x03
        """Enable event capture mode, to measure whether any other sensor is in the
        neighbourhood."""

        REQUEST_WARM_RESET = 0x04
        """Reset sensor."""

    def __init__(self, brick, port, check_compatible=True):
        super().__init__(brick, port, check_compatible)

    def get_distance(self):
        """Get distance to detected object.

        :return: Distance in cm.
        :rtype: int
        """
        return self.read_value("measurement_byte_0")[0]

    get_sample = get_distance

    def get_measurement_units(self):
        """Get measurement units.

        :return: String representing the measurement units, should be "10E-2m".
        :rtype: str
        """
        return (
            self.read_value("measurement_units")[0]
            .decode("windows-1252")
            .split("\0")[0]
        )

    def get_all_measurements(self):
        """Get all the measurements.

        :return: Eight distances in cm.
        :rtype: (int, int, int, int, int, int, int, int)
        """
        return self.read_value("measurements")

    def get_measurement_no(self, number):
        """Get one of the measurements.

        :param int number: Measurement number.
        :return: Distance in cm.
        :rtype: int
        """
        return self.read_value(f"measurement_byte_{number}")[0]

    def command(self, command):
        """Send a command to the sensor.

        :param Command command: Command to send.
        """
        self.write_value("command", (command.value,))

    def get_interval(self):
        """Get measurement interval, unknown unit.

        :return: Content of interval measurement register.
        :rtype: int
        """
        return self.read_value("continuous_measurement_interval")[0]

    def set_interval(self, interval):
        """Set measurement interval, unknown unit.

        :param int interval: New content of interval measurement register.
        """
        self.write_value("continuous_measurement_interval", (interval,))


Ultrasonic.add_compatible_sensor(None, "LEGO", "Sonar")  # Tested with version 'V1.0'


class Color(BaseAnalogSensor):
    """LEGO Mindstorms NXT color sensor, part number 64892.

    This sensor is included in the Mindstorms NXT 2.0 set. Not to be confused with the
    light sensor included in the first version or in the Education set.
    """

    class DetectedColor(enum.IntEnum):
        """Color detected by the sensor.

        This is an :class:`enum.IntEnum` for backward compatibility.
        """

        BLACK = 1
        """Black or low intensity."""

        BLUE = 2
        """Blue."""

        GREEN = 3
        """Green."""

        YELLOW = 4
        """Yellow."""

        RED = 5
        """Red."""

        WHITE = 6
        """White."""

    def __init__(self, brick, port):
        super().__init__(brick, port)
        self.set_light_color(Type.COLOR_FULL)

    def set_light_color(self, color):
        """Set the light color.

        :param Type color: Light color, or off, must be one of the Type.COLOR_* values.
        """
        self.set_input_mode(color, Mode.RAW)

    def get_light_color(self):
        """Get the light color previously set.

        :return: Light color, one of the Type.COLOR_* values.
        :rtype: Type
        """
        return self.get_input_values().sensor_type

    def get_reflected_light(self, color):
        """Get detected light level.

        :param Type color: Light color, or off, must be one of the Type.COLOR_* values.
        :return: Detected light level between 0 and 1023.
        :rtype: int
        """
        self.set_light_color(color)
        return self.get_input_values().scaled_value

    def get_color(self):
        """Get detected color.

        :return: Detected color.
        :rtype: DetectedColor

        This also sets the sensor mode to color detection (light is cycling quickly to
        determine color).
        """
        self.get_reflected_light(Type.COLOR_FULL)
        return self.DetectedColor(self.get_input_values().scaled_value)

    get_sample = get_color


class Temperature(BaseDigitalSensor):
    """LEGO Mindstorms NXT temperature sensor, part number 62840."""

    # This is actually a TI TMP275 chip: http://www.ti.com/product/tmp275
    I2C_DEV = 0x98
    I2C_ADDRESS = {"raw_value": (0x00, ">h")}

    def __init__(self, brick, port):
        # This sensor does not follow the convention of having version/vendor/product at
        # I2C registers 0x00/0x08/0x10, so check_compatible is always False.
        super().__init__(brick, port, False)

    def _get_raw_value(self):
        """Get raw unscaled value.

        :return: Unscaled value.
        :rtype: int
        """
        # This is a 12-bit value.
        return self.read_value("raw_value")[0] >> 4

    def get_deg_c(self):
        """Get the temperature in degrees Celsius.

        :return: Temperature in degrees Celsius.
        :rtype: float
        """
        v = self._get_raw_value()
        return round(v / 16, 1)

    def get_deg_f(self):
        """Get the temperature in degrees Fahrenheit.

        :return: Temperature in degrees Fahrenheit.
        :rtype: float
        """
        v = self._get_raw_value()
        return round(9 / 5 * v / 16 + 32, 1)

    get_sample = get_deg_c
