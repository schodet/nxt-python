# nxt.backend.btsocket module -- Bluetooth backend using socket
# Copyright (C) 2024  Nicolas Schodet
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
import socket
import struct

import nxt.brick

logger = logging.getLogger(__name__)

# NXT brick RFCOMM port.
PORT = 1


class BtSocketSock:
    """Bluetooth socket connected to a NXT brick."""

    #: Block size.
    bsize = 118

    #: Connection type, used to evaluate latency.
    type = "bluetooth"

    def __init__(self, host):
        self._host = host
        self._sock = None

    def __str__(self):
        return f"BtSocket ({self._host})"

    def connect(self):
        """Connect to NXT brick.

        :return: Connected brick.
        :rtype: Brick
        """
        logger.info("connecting via %s", self)
        sock = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        try:
            sock.connect((self._host, PORT))
        except OSError:
            sock.close()
            raise
        self._sock = sock
        return nxt.brick.Brick(self)

    def close(self):
        """Close the connection."""
        if self._sock is not None:
            logger.info("closing %s connection", self)
            self._sock.close()
            self._sock = None

    def send(self, data):
        """Send raw data.

        :param bytes data: Data to send.
        """
        data = struct.pack("<H", len(data)) + data
        logger.debug("send: %s", data.hex())
        self._sock.send(data)

    def recv(self):
        """Receive raw data.

        :return: Received data.
        :rtype: bytes
        """
        data = self._sock.recv(2)
        logger.debug("recv: %s", data.hex())
        (plen,) = struct.unpack("<H", data)
        data = self._sock.recv(plen)
        logger.debug("recv: %s", data.hex())
        return data


class Backend:
    """Bluetooth socket backend.

    This uses a system socket to connect to the NXT brick without needing a Bluetooth
    python package.

    This backend does not support brick discovery, you need to know the brick address.

    You only need to use this backend if the :mod:`~nxt.backend.bluetooth` backend is
    not working for you.
    """

    def find(self, host=None, **kwargs):
        """Find bricks connected using Bluetooth using socket.

        :param host: Bluetooth address (example: ``"00:16:53:01:02:03"``).
        :type host: str or None
        :param kwargs: Other parameters are ignored.
        :return: Iterator over all found bricks.
        :rtype: Iterator[Brick]
        """
        if host is not None:
            sock = BtSocketSock(host)
            try:
                brick = sock.connect()
            except OSError:
                logger.warning("failed to connect to device %s", sock)
                logger.debug("error from connect", exc_info=True)
            else:
                yield brick


def get_backend():
    """Get an instance of the Bluetooth socket backend if available.

    :return: Bluetooth socket backend.
    :rtype: Backend or None
    """
    return Backend()
