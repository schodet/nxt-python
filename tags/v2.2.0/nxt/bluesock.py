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

try:
    import bluetooth
except ImportError:
    import lightblueglue as bluetooth
from nxt.brick import Brick

class BlueSock(object):

    bsize = 118  # Bluetooth socket block size
    PORT = 1     # Standard NXT rfcomm port

    type = 'bluetooth'

    def __init__(self, host):
        self.host = host
        self.sock = None
        self.debug = False

    def __str__(self):
        return 'Bluetooth (%s)' % self.host

    def connect(self):
        if self.debug:
            print 'Connecting via Bluetooth...'
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((self.host, BlueSock.PORT))
        self.sock = sock
        if self.debug:
            print 'Connected.'
        return Brick(self)

    def close(self):
        if self.debug:
            print 'Closing Bluetooth connection...'
        self.sock.close()
        if self.debug:
            print 'Bluetooth connection closed.'

    def send(self, data):
        if self.debug:
            print 'Send:',
            print ':'.join('%02x' % ord(c) for c in data)
        l0 = len(data) & 0xFF
        l1 = (len(data) >> 8) & 0xFF
        d = chr(l0) + chr(l1) + data
        self.sock.send(d)

    def recv(self):
        data = self.sock.recv(2)
        l0 = ord(data[0])
        l1 = ord(data[1])
        plen = l0 + (l1 << 8)
        data = self.sock.recv(plen)
        if self.debug:
            print 'Recv:',
            print ':'.join('%02x' % ord(c) for c in data)
        return data

def _check_brick(arg, value):
    return arg is None or arg == value

def find_bricks(host=None, name=None):
    for h, n in bluetooth.discover_devices(lookup_names=True):
        if _check_brick(host, h) and _check_brick(name, n):
            yield BlueSock(h)
