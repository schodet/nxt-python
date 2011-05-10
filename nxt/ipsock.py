# nxt.ipsock module -- Server socket communication with LEGO Minstorms NXT
# Copyright (C) 2011  zonedaobne, Marcus Wanner
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

class IpSock(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.debug = False

    def __str__(self):
        return 'Server (%s)' % self.host

    def connect(self):
        if self.debug:
            print 'Connecting via Server...'
        sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        #TODO: sasl authentication here?
        self.sock = sock
        if self.debug:
            print 'Connected.'
        self.send('\x98')
        self.type = 'ip'+self.recv()
        return Brick(self)

    def close(self):
        if self.debug:
            print 'Closing Server connection...'
        self.sock.send('\x99')
        self.sock.close()
        if self.debug:
            print 'Server connection closed.'

    def send(self, data):
        if self.debug:
            print 'Send:',
            print ':'.join('%02x' % ord(c) for c in data)
        self.sock.send(data)

    def recv(self):
        data = self.sock.recv(1024)
        if self.debug:
            print 'Recv:',
            print ':'.join('%02x' % ord(c) for c in data)
        return data

#TODO: add a find_bricks method and a corresponding broadcast system to nxt_server?
