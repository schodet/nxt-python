# test_backend_usb -- Test nxt.backend.usb module
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
from unittest.mock import Mock, call, patch

import pytest

import nxt.backend.usb


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
    with patch("nxt.backend.usb.usb.core") as usb_core:
        usb_core.find.return_value = [mdev]
        yield usb_core


def test_usb(musb, mdev):
    # Instantiate backend.
    backend = nxt.backend.usb.get_backend()
    # Find brick.
    epout = Mock(spec_set=("write",))
    epin = Mock(spec_set=("read",))
    mdev.get_active_configuration.return_value = {(0, 0): (epout, epin)}
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 1
    brick = bricks[0]
    assert mdev.reset.called
    assert mdev.set_configuration.called
    assert mdev.get_active_configuration.called
    sock = brick._sock
    # str.
    assert str(sock).startswith("USB (Bus")
    # Send.
    some_bytes = bytes.fromhex("01020304")
    sock.send(some_bytes)
    assert epout.write.call_args == call(some_bytes)
    # Recv.
    epin.read.return_value = array.array("B", (1, 2, 3, 4))
    r = sock.recv()
    assert r == some_bytes
    assert epin.read.called
    # Close.
    brick.close()
    # Duplicated close.
    sock.close()


@pytest.mark.nxt("usb")
def test_usb_real():
    # Instantiate backend.
    backend = nxt.backend.usb.get_backend()
    # Find brick.
    bricks = list(backend.find())
    assert len(bricks) > 0, "no NXT found"
    brick = bricks[0]
    sock = brick._sock
    # str.
    assert str(sock).startswith("USB (Bus")
    # Send.
    sock.send(bytes.fromhex("019b"))
    # Recv.
    r = sock.recv()
    assert r.startswith(bytes.fromhex("029b00"))
    # Close.
    brick.close()
