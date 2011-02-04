# nxt.locator module -- Locate LEGO Minstorms NXT bricks via USB or Bluetooth
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

class BrickNotFoundError(Exception):
    pass

class NoBackendError(Exception):
    pass

def find_bricks(host=None, name=None):
    """Used by find_one_brick to look for bricks ***ADVANCED USERS ONLY***"""

    try:
        import usbsock
        usb_available = True
        socks = usbsock.find_bricks(host, name)
        for s in socks:
            yield s
    except ImportError:
        usb_available = False
        import sys
        print >>sys.stderr, "USB module unavailable, not searching there"
    
    try:
        import bluesock
        try:
            socks = bluesock.find_bricks(host, name)
            for s in socks:
                yield s
        except (bluesock.bluetooth.BluetoothError, IOError): #for cases such as no adapter, bluetooth throws IOError, not BluetoothError
            pass
    except ImportError:
        import sys
        print >>sys.stderr, "Bluetooth module unavailable, not searching there"
        if not usb_available:
            raise NoBackendError("Neither USB nor Bluetooth could be used! Did you install PyUSB or PyBluez?")
    

def find_one_brick(host=None, name=None):
    """Use to find one brick. After it returns a usbsock object or a bluesock
    object, it automatically connects to it."""
    for s in find_bricks(host, name):
        return s.connect()
    raise BrickNotFoundError
