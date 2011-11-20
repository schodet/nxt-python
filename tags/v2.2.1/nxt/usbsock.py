# nxt.usbsock module -- USB socket communication with LEGO Minstorms NXT
# Copyright (C) 2006, 2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
# Copyright (C) 2011  Paul Hollensen, Marcus Wanner
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

import usb, os
from nxt.brick import Brick

ID_VENDOR_LEGO = 0x0694
ID_PRODUCT_NXT = 0x0002

class USBSock(object):
    'Object for USB connection to NXT'

    bsize = 60	# USB socket block size

    type = 'usb'

    def __init__(self, device):
        self.device = device
        self.handle = None
        self.debug = False

    def __str__(self):
        return 'USB (%s)' % (self.device.filename)

    def connect(self):
        'Use to connect to NXT.'
        if self.debug:
            print 'Connecting via USB...'
        config = self.device.configurations[0]
        iface = config.interfaces[0][0]
        self.blk_out, self.blk_in = iface.endpoints
        self.handle = self.device.open()
        self.handle.setConfiguration(1)
        self.handle.claimInterface(0)
        if os.name != 'nt': # http://code.google.com/p/nxt-python/issues/detail?id=33
            self.handle.reset()
        if self.debug:
            print 'Connected.'
        return Brick(self)

    def close(self):
        'Use to close the connection.'
        if self.debug:
            print 'Closing USB connection...'
        self.device = None
        self.handle = None
        self.blk_out = None
        self.blk_in = None
        if self.debug:
            print 'USB connection closed.'

    def send(self, data):
        'Use to send raw data over USB connection ***ADVANCED USERS ONLY***'
        if self.debug:
            print 'Send:',
            print ':'.join('%02x' % ord(c) for c in data)
        self.handle.bulkWrite(self.blk_out.address, data)

    def recv(self):
        'Use to recieve raw data over USB connection ***ADVANCED USERS ONLY***'
        data = self.handle.bulkRead(self.blk_in.address, 64)
        if self.debug:
            print 'Recv:',
            print ':'.join('%02x' % (c & 0xFF) for c in data)
        # NOTE: bulkRead returns a tuple of ints ... make it sane
        return ''.join(chr(d & 0xFF) for d in data)

def find_bricks(host=None, name=None):
    'Use to look for NXTs connected by USB only. ***ADVANCED USERS ONLY***'
    # FIXME: probably should check host (MAC)
    # if anyone knows how to do this, please file a bug report
    for bus in usb.busses():
        for device in bus.devices:
            if device.idVendor == ID_VENDOR_LEGO and device.idProduct == ID_PRODUCT_NXT:
                yield USBSock(device)
