# nxt.locator module -- Locate LEGO Minstorms NXT bricks via USB or Bluetooth
# Copyright (C) 2013  Dave Churchill, Marcus Wanner
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

from nxt.brick import Brick
from glob import glob

class DeviceSocket:
    def __init__(self, filename=None):
        self._filename = filename

    def connect(self):
        self._device = open(self._filename, 'r+b', buffering=0)
        return Brick(self)
    
    def close(self):
        self._device.close()

    def send(self, data):
        l0 = len(data) & 0xFF
        l1 = (len(data) >> 8) & 0xFF
        d = chr(l0) + chr(l1) + data
        self._device.write(d)

    def recv(self):
        data = self._device.read(2)
        l0 = ord(data[0])
        l1 = ord(data[1])
        plen = l0 + (l1 << 8)
        return self._device.read(plen)

def find_bricks(host=None, name=None, filename=None):
    """Supply either name=brickname (path will be guessed),
filename=absolute path to brick file, or neither. host is ignored."""
    if name:
        matches = glob('/dev/*%s*' % name)
    elif filename:
        matches = glob(filename)
    else:
        #based on observed behavior of OSX 10.8, see issue 49
        matches = glob('/dev/*-DevB')
    for match in matches:
        yield DeviceSocket(match)
