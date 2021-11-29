# nxt.backend.devfile module -- Device file backend
# Copyright (C) 2013  Dave Churchill, Marcus Wanner
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

import glob
import logging
import struct

import nxt.brick

logger = logging.getLogger(__name__)


class DevFileSock:
    """Device file socket connected to a NXT brick."""

    #: Block size.
    bsize = 118

    #: Connection type, used to evaluate latency.
    type = "bluetooth"

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"DevFile ({self._filename})"

    def connect(self):
        """Connect to NXT brick.

        :return: Connected brick.
        :rtype: Brick
        """
        logger.info("connecting via %s", self._filename)
        self._device = open(self._filename, "r+b", buffering=0)
        return nxt.brick.Brick(self)

    def close(self):
        """Close the connection."""
        if self._device is not None:
            logger.info("closing %s connection", self._filename)
            self._device.close()
            self._device = None

    def send(self, data):
        """Send raw data.

        :param bytes data: Data to send.
        """
        data = struct.pack("<H", len(data)) + data
        logger.debug("send: %s", data.hex(":"))
        self._device.write(data)

    def recv(self):
        """Receive raw data.

        :return: Received data.
        :rtype: bytes
        """
        data = self._device.read(2)
        logger.debug("recv: %s", data.hex(":"))
        (plen,) = struct.unpack("<H", data)
        data = self._device.read(plen)
        logger.debug("recv: %s", data.hex(":"))
        return data


class Backend:
    """Device file backend.

    This uses a device file present on mac OS /dev file system.
    """

    def find(self, name=None, filename=None, **kwargs):
        """Find bricks connected using Bluetooth using device file.

        :param name: Brick name (example: ``"NXT"``).
        :type name: str or None
        :param filename: Device file name.
        :type filename: str or None
        :param kwargs: Other parameters are ignored.
        :return: Iterator over all found bricks.
        :rtype: Iterator[DevFileSock]
        """
        matches = []
        if name:
            matches.extend(glob.glob("/dev/*%s*" % name))
        if filename:
            matches.append(filename)
        if not matches:
            # Based on observed behavior of OSX 10.8, see issue 49.
            matches = glob.glob("/dev/*-DevB")
        for match in matches:
            yield DevFileSock(match)


def get_backend():
    """Get an instance of the device file backend.

    :return: Device file backend.
    :rtype: Backend
    """
    return Backend()
