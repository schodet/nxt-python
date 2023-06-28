# nxt.sensor module -- Classes to read LEGO Mindstorms NXT sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010,2011,2012  Marcus Wanner
# Copyright (C) 2023  Nicolas Schodet
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

import logging
import struct
import time

import nxt.sensor
from nxt.error import DirectProtocolError, I2CError, I2CPendingError

logger = logging.getLogger(__name__)


class SensorInfo:
    def __init__(self, version, product_id, sensor_type):
        self.version = version
        self.product_id = product_id
        self.sensor_type = sensor_type

    def clarifybinary(self, instr, label):
        outstr = ""
        outstr += label + ": `" + instr + "`\n"
        for char in instr:
            outstr += hex(ord(char)) + ", "
        outstr += "\n"
        return outstr

    def __str__(self):
        outstr = ""
        outstr += self.clarifybinary(str(self.version), "Version")
        outstr += self.clarifybinary(str(self.product_id), "Product ID")
        outstr += self.clarifybinary(str(self.sensor_type), "Type")
        return outstr


class BaseDigitalSensor(nxt.sensor.Sensor):
    """Object for digital sensors.

    :param bool check_compatible: Check sensor class match the connected sensor.

    If `check_compatible` is ``True``, queries the sensor for its name and print
    a warning if the wrong sensor class is used.

    `I2C_ADDRESS` is the dictionary storing name to I2C address mappings. It should be
    updated in every subclass. When subclassing this class, make sure to call
    :func:`add_compatible_sensor` to add compatible sensor data.
    """

    I2C_DEV = 0x02
    I2C_ADDRESS = {
        "version": (0x00, "8s"),
        "product_id": (0x08, "8s"),
        "sensor_type": (0x10, "8s"),
        # "factory_zero": (0x11, 1),  # is this really correct?
        "factory_scale_factor": (0x12, "B"),
        "factory_scale_divisor": (0x13, "B"),
    }

    def __init__(self, brick, port, check_compatible=True):
        super().__init__(brick, port)
        self.set_input_mode(nxt.sensor.Type.LOW_SPEED_9V, nxt.sensor.Mode.RAW)
        self.last_poll = time.time()
        self.poll_delay = 0.01
        time.sleep(0.1)  # Give I2C time to initialize
        # Don't do type checking if this class has no compatible sensors listed.
        try:
            self.compatible_sensors
        except AttributeError:
            check_compatible = False
        if check_compatible:
            sensor = self.get_sensor_info()
            if sensor not in self.compatible_sensors:
                logger.warning(
                    "wrong sensor class chosen for sensor %s on port %s",
                    sensor.product_id,
                    port,
                )
                logger.warning(
                    "   You may be using the wrong type of sensor or may have "
                    "connected the cable incorrectly. If you are sure you're using the "
                    "correct sensor class for the sensor, this message is likely in "
                    "error and you should disregard it and file a bug report, "
                    "including the output of get_sensor_info(). This message can be "
                    "suppressed by passing check_compatible=False when creating the "
                    "sensor object."
                )

    def _ls_get_status(self, size):
        for n in range(30):  # https://code.google.com/p/nxt-python/issues/detail?id=35
            try:
                b = self._brick.ls_get_status(self._port)
                if b >= size:
                    return b
            except I2CPendingError:
                pass
        raise I2CError("ls_get_status timeout")

    def _i2c_command(self, address, value, format):
        """Write one or several values to an I2C register.

        :param int address: I2C register address.
        :param tuple value: Tuple of values to write.
        :param str format: Format string using :mod:`struct` syntax.
        """
        value = struct.pack(format, *value)
        msg = bytes((self.I2C_DEV, address)) + value
        now = time.time()
        if self.last_poll + self.poll_delay > now:
            diff = now - self.last_poll
            time.sleep(self.poll_delay - diff)
        self.last_poll = time.time()
        self._brick.ls_write(self._port, msg, 0)

    def _i2c_query(self, address, format):
        """Read one or several values from an I2C register.

        :param int address: I2C register address.
        :param str format: Format string using :mod:`struct` syntax.
        :return: Read values in a tuple.
        :rtype: tuple
        """
        size = struct.calcsize(format)
        msg = bytes((self.I2C_DEV, address))
        now = time.time()
        if self.last_poll + self.poll_delay > now:
            diff = now - self.last_poll
            time.sleep(self.poll_delay - diff)
        self.last_poll = time.time()
        self._brick.ls_write(self._port, msg, size)
        try:
            self._ls_get_status(size)
        finally:
            # we should clear the buffer no matter what happens
            data = self._brick.ls_read(self._port)
        if len(data) < size:
            raise I2CError("Read failure: Not enough bytes")
        data = struct.unpack(format, data[-size:])
        return data

    def read_value(self, name):
        """Read one or several values from the sensor.

        :param str name: Name of the values to read.
        :return: Read values in a tuple.
        :rtype: tuple

        The `name` parameter is an index inside `I2C_ADDRESS` dictionary, which gives
        the corresponding I2C register address and format string.
        """
        address, fmt = self.I2C_ADDRESS[name]
        for n in range(3):
            try:
                return self._i2c_query(address, fmt)
            except DirectProtocolError:
                pass
        raise I2CError("read_value timeout")

    def write_value(self, name, value):
        """Write one or several values to the sensor.

        :param str name: Name of the values to write.
        :param tuple value: Tuple of values to write.

        The `name` parameter is an index inside `I2C_ADDRESS` dictionary, which gives
        the corresponding I2C register address and format string.
        """
        address, fmt = self.I2C_ADDRESS[name]
        self._i2c_command(address, value, fmt)

    def get_sensor_info(self):
        version = self.read_value("version")[0].decode("windows-1252").split("\0")[0]
        product_id = (
            self.read_value("product_id")[0].decode("windows-1252").split("\0")[0]
        )
        sensor_type = (
            self.read_value("sensor_type")[0].decode("windows-1252").split("\0")[0]
        )
        return SensorInfo(version, product_id, sensor_type)

    @classmethod
    def add_compatible_sensor(cls, version, product_id, sensor_type):
        """Adds an entry in the compatibility table for the sensor.

        :param version: Sensor version, or ``None`` for default class.
        :type version: str or None
        :param product_id: Product identifier, or ``None`` for default class.
        :type product_id: str or None
        :param str sensor_type: Sensor type
        """
        try:
            cls.compatible_sensors
        except AttributeError:
            cls.compatible_sensors = []
        finally:
            cls.compatible_sensors.append(
                _SCompatibility(version, product_id, sensor_type)
            )
            _add_mapping(cls, version, product_id, sensor_type)


class _SCompatibility(SensorInfo):
    """An object that helps manage the sensor mappings."""

    def __eq__(self, other):
        if self.product_id is None:
            return self.product_id == other.product_id
        elif self.version is None:
            return (
                self.product_id == other.product_id
                and self.sensor_type == other.sensor_type
            )
        else:
            return (
                self.version == other.version
                and self.product_id == other.product_id
                and self.sensor_type == other.sensor_type
            )


sensor_mappings = {}


def _add_mapping(cls, version, product_id, sensor_type):
    if product_id not in sensor_mappings:
        sensor_mappings[product_id] = {}
    models = sensor_mappings[product_id]

    if sensor_type is None:
        if sensor_type in models:
            raise ValueError("Already registered!")
        models[sensor_type] = cls
        return

    if sensor_type not in models:
        models[sensor_type] = {}
    versions = models[sensor_type]

    if version in versions:
        raise ValueError("Already registered!")
    else:
        versions[version] = cls


class SearchError(Exception):
    pass


def find_class(info):
    """Returns an appropriate class.

    :param SensorInfo info: Information read from the sensor.
    :return: Class corresponding to sensor.
    :rtype: BaseDigitalSensor
    :raises SearchError: When no class found.
    """
    dic = sensor_mappings
    for val, msg in zip(
        (info.product_id, info.sensor_type, info.version),
        ("Vendor", "Model", "Version"),
    ):
        if val in dic:
            dic = dic[val]
        elif None in dic:
            dic = dic[None]
        else:
            raise SearchError(msg + " not found")
        return dic[info.sensor_type][None]
