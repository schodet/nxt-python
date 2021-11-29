# nxt.backend.bluetooth module -- Bluetooth backend
# Copyright (C) 2006, 2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
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

import logging
import struct

import bluetooth

import nxt.brick

logger = logging.getLogger(__name__)

# NXT brick RFCOMM port.
PORT = 1


class BluetoothSock:
    """Bluetooth socket connected to a NXT brick."""

    #: Block size.
    bsize = 118

    #: Connection type, used to evaluate latency.
    type = "bluetooth"

    def __init__(self, host):
        self._host = host
        self._sock = None

    def __str__(self):
        return f"Bluetooth ({self._host})"

    def connect(self):
        """Connect to NXT brick.

        :return: Connected brick.
        :rtype: Brick
        """
        logger.info("connecting via %s", self)
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((self._host, PORT))
        self._sock = sock
        return nxt.brick.Brick(self)

    def close(self):
        """Close the connection."""
        logger.info("closing %s connection", self)
        self._sock.close()
        self._sock = None

    def send(self, data):
        """Send raw data.

        :param bytes data: Data to send.
        """
        data = struct.pack("<H", len(data)) + data
        logger.debug("send: %s", data.hex(":"))
        self._sock.send(data)

    def recv(self):
        """Receive raw data.

        :return: Received data.
        :rtype: bytes
        """
        data = self._sock.recv(2)
        logger.debug("recv: %s", data.hex(":"))
        (plen,) = struct.unpack("<H", data)
        data = self._sock.recv(plen)
        logger.debug("recv: %s", data.hex(":"))
        return data


class Backend:
    """Bluetooth backend."""

    def find(self, host=None, name=None, **kwargs):
        """Find bricks connected using Bluetooth.

        :param host: Bluetooth address (example: ``"00:16:53:01:02:03"``).
        :type host: str or None
        :param name: Brick name (example: ``"NXT"``).
        :type name: str or None
        :param kwargs: Other parameters are ignored.
        :return: Iterator over all found bricks.
        :rtype: Iterator[BluetoothSock]
        """
        for h, n in bluetooth.discover_devices(lookup_names=True):
            if (host is None or h == host) and (name is None or n == name):
                yield BluetoothSock(h)


def get_backend():
    """Get an instance of the Bluetooth backend.

    :return: Bluetooth backend.
    :rtype: Backend
    """
    return Backend()
