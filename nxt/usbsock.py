# nxt.usbsock module -- USB socket communication with LEGO Minstorms NXT
# Copyright (C) 2006, 2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
# Copyright (C) 2011  Paul Hollensen, Marcus Wanner
# Copyright (C) 2016  Alan Aguiar
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

IN_ENDPOINT  = 0x82
OUT_ENDPOINT = 0x01

NXT_CONFIGURATION = 1
NXT_INTERFACE     = 0

TIMEOUT = 250

class USBSock(object):
    'Object for USB connection to NXT'

    type = 'usb'

    def __init__(self, device):
        self.device = device
        self.debug = False

    def __str__(self):
        return 'USB (%s)' % (self.device.filename)

    def _debug(self, message, err=''):
        if self.debug:
            print(message, err)

    def connect(self):
        'Use to connect to NXT.'
        self._debug('Connecting via USB...')
        try:
            if os.name != 'nt' and self.device.is_kernel_driver_active(NXT_INTERFACE):
                self.device.detach_kernel_driver(NXT_INTERFACE)
            self.device.set_configuration(NXT_CONFIGURATION)
        except Exception as err:
            self._debug('ERROR:usbsock:connect', err)
            raise
        self._debug('Connected.')
        return Brick(self)

    def close(self):
        'Use to close the connection.'
        self._debug('Closing USB connection...')
        self.device = None
        self._debug('USB connection closed.')

    def send(self, data):
        'Use to send raw data over USB connection'
        self._debug('Send:', end=' ')
        self._debug(':'.join('%02x' % ord(c) for c in data))
        self.device.write(OUT_ENDPOINT, data, TIMEOUT)

    def recv(self):
        'Use to recieve raw data over USB connection'
        data = self.device.read(IN_ENDPOINT, 64, TIMEOUT)
        self._debug('Recv:', end=' ')
        self._debug(':'.join('%02x' % (c & 0xFF) for c in data))
        # NOTE: bulkRead returns a tuple of ints ... make it sane
        return bytearray(data)

def find_bricks(host=None, name=None):
    'Use to look for NXTs connected by USB only'
    for device in usb.core.find(find_all=True, idVendor=ID_VENDOR_LEGO, idProduct=ID_PRODUCT_NXT):
        yield USBSock(device)

