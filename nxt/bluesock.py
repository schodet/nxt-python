# nxt.bluesock module -- Bluetooth socket communication with LEGO Minstorms NXT
# Copyright (C) 2006, 2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
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

import struct

import bluetooth

from nxt.brick import Brick


class BlueSock:
    """Bluetooth socket connected to a NXT brick."""

    bsize = 118
    PORT = 1  # Standard NXT rfcomm port

    type = "bluetooth"

    def __init__(self, host):
        self.host = host
        self.sock = None
        self.debug = False

    def __str__(self):
        return "Bluetooth (%s)" % self.host

    def connect(self):
        """Connect to NXT brick, return a Brick instance."""
        if self.debug:
            print("Connecting via Bluetooth...")
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((self.host, BlueSock.PORT))
        self.sock = sock
        if self.debug:
            print("Connected.")
        return Brick(self)

    def close(self):
        """Close the connection."""
        if self.debug:
            print("Closing Bluetooth connection...")
        self.sock.close()
        if self.debug:
            print("Bluetooth connection closed.")

    def send(self, data):
        """Send raw data."""
        data = struct.pack("<H", len(data)) + data
        if self.debug:
            print("Send:", data.hex(":"))
        self.sock.send(data)

    def recv(self):
        """Receive raw data."""
        data = self.sock.recv(2)
        if self.debug:
            print("Recv:", data.hex(":"))
        (plen,) = struct.unpack("<H", data)
        data = self.sock.recv(plen)
        if self.debug:
            print("Recv:", data.hex(":"))
        return data


def find_bricks(host=None, name=None):
    """Find all bricks connected using Bluetooth matching given host and name."""
    for h, n in bluetooth.discover_devices(lookup_names=True):
        if (host is None or h == host) and (name is None or n == name):
            yield BlueSock(h)
