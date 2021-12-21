# nxt.backend.socket module -- Socket backend
# Copyright (C) 2011  zonedaobne, Marcus Wanner
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
import socket

import nxt.brick

logger = logging.getLogger(__name__)


class SocketSock:
    """Socket socket connected to a NXT brick."""

    #: Block size, conservative.
    bsize = 60

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = None
        #: Connection type, used to evaluate latency, known on connection.
        self.type = None

    def __str__(self):
        return f"Socket ({self._host}:{self._port})"

    def connect(self):
        """Connect to NXT brick.

        :return: Connected brick.
        :rtype: Brick
        """
        logger.info("connecting via %s:%d", self._host, self._port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._host, self._port))
        self._sock = sock
        self.send(bytes((0x98,)))
        self.type = "ip" + self.recv().decode("ascii")
        return nxt.brick.Brick(self)

    def close(self):
        """Close the connection."""
        if self._sock is not None:
            logger.info("closing connection to %s:%d", self._host, self._port)
            self._sock.send(bytes((0x99,)))
            self._sock.close()
            self._sock = None
            self.type = None

    def send(self, data):
        """Send raw data.

        :param bytes data: Data to send.
        """
        logger.debug("send: %s", data.hex())
        self._sock.send(data)

    def recv(self):
        """Receive raw data.

        :return: Received data.
        :rtype: bytes
        """
        data = self._sock.recv(1024)
        logger.debug("recv: %s", data.hex())
        return data


class Backend:
    """Socket backend.

    To be used with ``nxt_server`` script to access a NXT brick over the network.
    """

    def find(self, server_host="localhost", server_port=2727, **kwargs):
        """Find bricks connected using a socket.

        :param str server_host: Server address or name, default to `localhost`.
        :param server_port: Server port, default to 2727.
        :type server_port: str or int
        :param kwargs: Other parameters are ignored.
        :return: Iterator over all found bricks.
        :rtype: Iterator[Brick]
        """
        sock = SocketSock(server_host, int(server_port))
        try:
            brick = sock.connect()
        except ConnectionRefusedError:
            logger.exception("failed to connect to device %s", sock)
        else:
            yield brick


def get_backend():
    """Get an instance of the Socket backend.

    :return: Socket backend.
    :rtype: Backend
    """
    return Backend()
