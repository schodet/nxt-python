# nxt.devsock module -- Bluetooth communication using a device file
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
import struct

from nxt.brick import Brick


class DeviceSocket:
    """Device file socket connected to a NXT brick."""

    bsize = 118

    type = "bluetooth"

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"DevFile ({self._filename})"

    def connect(self):
        """Connect to NXT brick, return a Brick instance."""
        self._device = open(self._filename, "r+b", buffering=0)
        return Brick(self)

    def close(self):
        """Close the connection."""
        self._device.close()

    def send(self, data):
        """Send raw data."""
        data = struct.pack("<H", len(data)) + data
        self._device.write(data)

    def recv(self):
        """Receive raw data."""
        data = self._device.read(2)
        (plen,) = struct.unpack("<H", data)
        return self._device.read(plen)


def find_bricks(host=None, name=None, filename=None):
    """Find all bricks connected using Bluetooth matching given host and name."""
    if name:
        matches = glob.glob("/dev/*%s*" % name)
    elif filename:
        matches = glob.glob(filename)
    else:
        # Based on observed behavior of OSX 10.8, see issue 49.
        matches = glob.glob("/dev/*-DevB")
    for match in matches:
        yield DeviceSocket(match)
