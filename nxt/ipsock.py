# nxt.ipsock module -- Server socket communication with LEGO Minstorms NXT
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

import socket

from nxt.brick import Brick


class IpSock:
    """Socket socket connected to a NXT brick."""

    bsize = 60

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.debug = False

    def __str__(self):
        return f"Socket ({self.host}:{self.port})"

    def connect(self):
        """Connect to NXT brick, return a Brick instance."""
        if self.debug:
            print("Connecting via %s:%d" % (self.host, self.port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self.sock = sock
        self.send(bytes((0x98,)))
        self.type = "ip" + self.recv().decode("ascii")
        if self.debug:
            print("Connected.")
        return Brick(self)

    def close(self):
        """Close the connection."""
        if self.debug:
            print("Closing connection to %s:%d" % (self.host, self.port))
        self.sock.send(bytes((0x99,)))
        self.sock.close()
        self.sock = None
        self.type = None
        if self.debug:
            print("Server connection closed.")

    def send(self, data):
        """Send raw data."""
        if self.debug:
            print("Send:", data.hex(":"))
        self.sock.send(data)

    def recv(self):
        """Receive raw data."""
        data = self.sock.recv(1024)
        if self.debug:
            print("Recv:", data.hex(":"))
        return data


# TODO: add a find_bricks method and a corresponding broadcast system to nxt_server?
