# fantomsock.py module -- NXT_Python socket wrapper for pyfantom (Mac)
#
# Copyright (C) 2011  Tat-Chee Wan, Marcus Wanner
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

import pyfantom
from nxt.brick import Brick

USB_BUFSIZE = 64
BT_BUFSIZE = 1024 #"arbitrary"
FANTOMSOCK_DEBUG = False


class BluetoothSocket:
    bsize = BT_BUFSIZE - 4        # Bluetooth socket block size

    '''recv() method is currently reported broken'''
    def __init__(self, _sock=None):
        # We instantiate a NXT object only when we connect if none supplied
        self._sock = _sock
        self.debug = FANTOMSOCK_DEBUG

    def __str__(self):
        return 'FantomSock BT (%s)' % self.device_name()

    def device_name(self):
        devinfo = self._sock.get_device_info()
        return devinfo.name

    def connect(self, addrport=None):
        if self._sock is None:
            if self.debug:
                print "No NXT object assigned"
            assert addrport is not None
            # Port is ignored
            addr, port = addrport
            paired_addr = pyfantom.pair_bluetooth(addr)
            if self.debug:
                print "BT Paired Addr: ", paired_addr
            self._sock = pyfantom.NXT(paired_addr)
        else:
            if self.debug:
                print "Using existing NXT object"
        return Brick(self)
    
    def send(self, data):
        return self._sock.write(data)

    def recv(self, numbytes=BT_BUFSIZE):
        '''currently reported broken'''
        return self._sock.read(numbytes)
    
    def close(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None


class USBSocket:
    bsize = USB_BUFSIZE - 4        # USB socket block size

    def __init__(self, device=None):
        self._sock = device
        self.debug = FANTOMSOCK_DEBUG

    def __str__(self):
        return 'FantomSock USB (%s)' % self.device_name()

    def device_name(self):
        devinfo = self._sock.get_device_info()
        return devinfo.name

    def connect(self, addrport=None):
        if self._sock is None:
            if self.debug:
                print "No NXT object assigned"
            assert addrport is not None
            # Port is ignored
            addr, port = addrport
            self._sock = pyfantom.NXT(addr)
        else:
            if self.debug:
                print "Using existing NXT object"
        return Brick(self)
    
    def send(self, data):
        return self._sock.write(data)

    def recv(self, numbytes=USB_BUFSIZE):
        return self._sock.read(numbytes)

    def close(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None


def find_bricks(host=None, name=None, useBT=False):
    for d in pyfantom.NXTIterator(useBT):
        nxt = d.get_nxt()
        if host or name:
            info = nxt.get_device_info()
        if ((host and not info.bluetooth_address == host) or
            (name and not info.name == name)): #name or host doesn't match
            continue
        if useBT:
            yield BluetoothSocket(nxt)
        else:
            yield USBSocket(nxt)
