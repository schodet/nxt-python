# bluetooth.py module -- Glue code from NXT_Python to Lightblue, allowing
# NXT_Python to run on Mac without modification.  Supports subset of
# PyBluez/bluetooth.py used by NXT_Python.
#
# Copyright (C) 2007  Simon D. Levy
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import lightblue

RFCOMM=11

def discover_devices(lookup_names=False):  # parameter is ignored
    pairs = []
    d = lightblue.finddevices()
    for p in d:
        h = p[0]
        n = p[1]
        pairs.append((h, n))
    return pairs

class BluetoothSocket:

    def __init__(self, proto = RFCOMM, _sock=None):
        if _sock is None:
            _sock = lightblue.socket(proto)
        self._sock = _sock
        self._proto = proto

    def connect(self, addrport):
        addr, port = addrport
        self._sock.connect( (addr, port ))
    
    def send(self, data):
        return self._sock.send( data )

    def recv(self, numbytes):
        return self._sock.recv( numbytes )
    
    def close(self):
        return self._sock.close()
    
class BluetoothError(IOError):
    pass    

