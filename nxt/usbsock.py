# nxt.usbsock module -- USB socket communication with LEGO Minstorms NXT
# Copyright (C) 2006, 2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
# Copyright (C) 2011  Paul Hollensen, Marcus Wanner
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

import usb.core

from nxt.brick import Brick

ID_VENDOR_LEGO = 0x0694
ID_PRODUCT_NXT = 0x0002


class USBSock:
    """USB socket connected to a NXT brick."""

    bsize = 60

    type = "usb"

    def __init__(self, dev):
        self.dev = dev
        self.epout = None
        self.epin = None
        self.debug = False

    def __str__(self):
        return "USB (Bus %03d Device %03d)" % (self.dev.bus, self.dev.address)

    def connect(self):
        """Connect to NXT brick, return a Brick instance."""
        if self.debug:
            print("Connecting via USB...")
        self.dev.reset()
        self.dev.set_configuration()
        intf = self.dev.get_active_configuration()[(0, 0)]
        self.epout, self.epin = intf
        if self.debug:
            print("Connected.")
        return Brick(self)

    def close(self):
        """Close the connection."""
        if self.debug:
            print("Closing USB connection...")
        self.epout = None
        self.epin = None
        self.dev = None
        if self.debug:
            print("USB connection closed.")

    def send(self, data):
        """Send raw data."""
        if self.debug:
            print("Send:", data.hex(":"))
        self.epout.write(data)

    def recv(self):
        """Receive raw data."""
        data = self.epin.read(64).tobytes()
        if self.debug:
            print("Recv:", data.hex(":"))
        return data


def find_bricks():
    """Find all bricks connected using USB."""
    for dev in usb.core.find(
        find_all=True, idVendor=ID_VENDOR_LEGO, idProduct=ID_PRODUCT_NXT
    ):
        yield USBSock(dev)
