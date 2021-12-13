# nxt.sensor module -- Classes to read LEGO Mindstorms NXT sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010  Marcus Wanner
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

import enum

__all__ = ["Port", "Type", "Mode", "Sensor"]


class Port(enum.Enum):
    """Input port identifier.

    The prefix is needed because a Python identifier can not start with a digit.
    """

    S1 = 0
    """Sensor port 1."""

    S2 = 1
    """Sensor port 2."""

    S3 = 2
    """Sensor port 3."""

    S4 = 3
    """Sensor port 4."""


class Type(enum.Enum):
    """Sensor type."""

    NO_SENSOR = 0
    """No sensor is connected."""

    SWITCH = 1
    """Touch sensor."""

    TEMPERATURE = 2
    """RCX temperature sensor."""

    REFLECTION = 3
    """RCX light sensor."""

    ANGLE = 4
    """RCX rotation sensor."""

    LIGHT_ACTIVE = 5
    """Light sensor with light active."""

    LIGHT_INACTIVE = 6
    """Light sensor with light off."""

    SOUND_DB = 7
    """Sound sensor (unadjusted)."""

    SOUND_DBA = 8
    """Sound sensor (adjusted)."""

    CUSTOM = 9
    """Custom sensor (unused)."""

    LOW_SPEED = 10
    """Low speed digital sensor."""

    LOW_SPEED_9V = 11
    """Low speed digital sensor with 9V supply voltage."""

    HIGH_SPEED = 12
    """High speed sensor."""

    COLOR_FULL = 13
    """NXT color sensor in full color mode (color sensor mode)."""

    COLOR_RED = 14
    """NXT color sensor with red light on (light sensor mode)."""

    COLOR_GREEN = 15
    """NXT color sensor with green light on (light sensor mode)."""

    COLOR_BLUE = 16
    """NXT color sensor in with blue light on (light sensor mode)."""

    COLOR_NONE = 17
    """NXT color sensor in with light off (light sensor mode)."""

    COLOR_EXIT = 18
    """NXT color sensor internal state."""


class Mode(enum.Enum):
    """Sensor mode."""

    RAW = 0x00
    """Raw value, from 0 to 1023."""

    BOOL = 0x20
    """Boolean value, 0 or 1."""

    EDGE = 0x40
    """Count number of transitions."""

    PULSE = 0x60
    """Count number of pulse."""

    PERCENT = 0x80
    """Value from 0 to 100."""

    CELSIUS = 0xA0
    """Temperature in degree Celsius."""

    FAHRENHEIT = 0xC0
    """Temperature in degree Fahrenheit."""

    ROTATION = 0xE0
    """RCX rotation sensor mode."""


class Sensor:
    """Sensor base class."""

    def __init__(self, brick, port):
        self._brick = brick
        self._port = port

    def set_input_mode(self, sensor_type, sensor_mode):
        """Set sensor input mode.

        :param Type sensor_type: Sensor type.
        :param Mode sensor_mode: Sensor mode.
        """
        self._brick.set_input_mode(self._port, sensor_type, sensor_mode)
