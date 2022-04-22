# nxt.backend.usb module -- USB backend
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

import logging
import os

import usb.core

import nxt.brick

logger = logging.getLogger(__name__)

# LEGO USB vendor ID.
ID_VENDOR_LEGO = 0x0694

# NXT brick product ID.
ID_PRODUCT_NXT = 0x0002


class USBSock:
    """USB socket connected to a NXT brick."""

    #: Block size.
    bsize = 60

    #: Connection type, used to evaluate latency.
    type = "usb"

    def __init__(self, dev):
        self._dev = dev
        self._epout = None
        self._epin = None

    def __str__(self):
        return "USB (Bus %03d Device %03d)" % (self._dev.bus, self._dev.address)

    def connect(self):
        """Connect to NXT brick.

        :return: Connected brick.
        :rtype: Brick
        """
        logger.info("connecting via %s", self)
        if os.name != "nt":
            # Do not reset device on Windows, see
            # https://github.com/schodet/nxt-python/issues/182 and
            # https://github.com/schodet/nxt-python/issues/33
            self._dev.reset()
        self._dev.set_configuration()
        intf = self._dev.get_active_configuration()[(0, 0)]
        self._epout, self._epin = intf
        return nxt.brick.Brick(self)

    def close(self):
        """Close the connection."""
        if self._epout is not None:
            logger.info("closing %s connection", self)
            self._epout = None
            self._epin = None

    def send(self, data):
        """Send raw data.

        :param bytes data: Data to send.
        """
        logger.debug("send: %s", data.hex())
        self._epout.write(data)

    def recv(self):
        """Receive raw data.

        :return: Received data.
        :rtype: bytes
        """
        data = self._epin.read(64).tobytes()
        logger.debug("recv: %s", data.hex())
        return data


class Backend:
    """USB backend."""

    def find(self, **kwargs):
        """Find bricks connected using USB.

        :param kwargs: Parameters are ignored.
        :return: Iterator over all found bricks.
        :rtype: Iterator[Brick]
        """
        for dev in usb.core.find(
            find_all=True, idVendor=ID_VENDOR_LEGO, idProduct=ID_PRODUCT_NXT
        ):
            sock = USBSock(dev)
            brick = sock.connect()
            yield brick


def get_backend():
    """Get an instance of the Bluetooth backend.

    :return: Bluetooth backend.
    :rtype: Backend
    """
    return Backend()
