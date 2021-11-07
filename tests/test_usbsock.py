# test_socks -- Test nxt.usbsock module
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
import array
from unittest.mock import Mock, patch

import pytest

import nxt.usbsock


@pytest.fixture
def mdev():
    dev = Mock(
        spec_set=(
            "reset",
            "set_configuration",
            "get_active_configuration",
            "bus",
            "address",
        )
    )
    dev.bus = 1
    dev.address = 2
    return dev


@pytest.fixture
def musb(mdev):
    with patch("nxt.usbsock.usb.core") as usb_core:
        usb_core.find.return_value = [mdev]
        yield usb_core


def test_usbsock(musb, mdev):
    # Find brick.
    socks = list(nxt.usbsock.find_bricks())
    assert len(socks) == 1
    sock = socks[0]
    sock.debug = True
    # str.
    assert str(sock).startswith("USB (Bus")
    # Connect.
    epout = Mock(spec_set=("write",))
    epin = Mock(spec_set=("read",))
    mdev.get_active_configuration.return_value = {(0, 0): (epout, epin)}
    brick = sock.connect()
    assert mdev.reset.called
    assert mdev.set_configuration.called
    assert mdev.get_active_configuration.called
    # Send.
    some_bytes = bytes.fromhex("01020304")
    sock.send(some_bytes)
    assert epout.write.call_args == ((some_bytes,),)
    # Recv.
    epin.read.return_value = array.array("B", (1, 2, 3, 4))
    r = sock.recv()
    assert r == some_bytes
    assert epin.read.called
    # Close.
    # TODO: brick.__del__ should close the socket, but nobody knows when
    # python calls the destructor.
    sock.close()
    del brick


@pytest.mark.nxt("usb")
def test_usbsock_real():
    # Find brick.
    socks = list(nxt.usbsock.find_bricks())
    assert len(socks) > 0, "no NXT found"
    sock = socks[0]
    sock.debug = True
    # str.
    assert str(sock).startswith("USB (Bus")
    # Connect.
    brick = sock.connect()
    # Send.
    sock.send(bytes.fromhex("019b"))
    # Recv.
    r = sock.recv()
    assert r.startswith(bytes.fromhex("029b00"))
    # Close.
    sock.close()
    del brick
