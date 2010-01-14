# nxt.locator module -- Locate LEGO Minstorms NXT bricks via USB or Bluetooth
# Copyright (C) 2006-2007  Douglas P Lau
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
        print >>sys.stderr, "USB unavailable, not searching there"
    
    try:
        import bluesock
        try:
            socks = bluesock.find_bricks(host, name)
            for s in socks:
                yield s
        except:
            #"except:" is dangerous and the code in the above try: block should
            #be treated with extreme caution. Any errors in it will be dropped
            #silently.
            #This is necessary to provide a higher level of abstraction above
            #the "bluetooth" module on linux/windows and the "lightblue" module
            #on mac, since catching bluetooth errors would involve a non-cross-
            #platform "import bluetooth", which also happens to break compata-
            #bility with lightblueglue even when used externally.
            #When testing modifications to the try: block, it may be helpful to
            #add "import sys; print sys.exc_info()" right below this message, to
            #print out any errors.
            pass
    except ImportError:
        import sys
        print >>sys.stderr, "Bluetooth unavailable, not searching there"
        if not usb_available:
            raise NoBackendError("Neither USB nor Bluetooth could be used!")
    

def find_one_brick(host=None, name=None):
    """Use to find one brick. After it returns a usbsock object or a bluesock
    object, use .connect() to connect to the brick, which returns a brick
    object."""
    for s in find_bricks(host, name):
        return s
    raise BrickNotFoundError
