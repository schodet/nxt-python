# test_ipsock -- Test nxt.ipsock module
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
from unittest.mock import Mock, call, patch

import pytest

import nxt.ipsock


@pytest.fixture
def mdev():
    dev = Mock(
        spec_set=(
            "connect",
            "send",
            "recv",
            "close",
        )
    )
    return dev


@pytest.fixture
def msocket(mdev):
    with patch("nxt.ipsock.socket") as socket:
        socket.socket.return_value = mdev
        yield socket


def test_ipsock(msocket, mdev):
    # Find brick.
    sock = nxt.ipsock.IpSock("localhost", 2727)
    sock.debug = True
    # str.
    assert str(sock) == "Socket (localhost:2727)"
    # Connect.
    mdev.recv.return_value = b"usb"
    brick = sock.connect()
    assert sock.type == "ipusb"
    assert msocket.socket.called
    assert mdev.connect.called
    assert mdev.send.call_args == call(b"\x98")
    # Send.
    some_bytes = bytes.fromhex("01020304")
    sock.send(some_bytes)
    assert mdev.send.call_args == call(some_bytes)
    # Recv.
    mdev.recv.return_value = some_bytes
    r = sock.recv()
    assert r == some_bytes
    assert mdev.recv.called
    # Close.
    # TODO: brick.__del__ should close the socket, but nobody knows when
    # python calls the destructor.
    sock.close()
    assert mdev.send.call_args == call(b"\x99")
    assert mdev.close.called
    del brick


@pytest.mark.nxt("socket")
def test_ipsock_real():
    # Find brick.
    sock = nxt.ipsock.IpSock("localhost", 2727)
    sock.debug = True
    # str.
    assert str(sock) == "Socket (localhost:2727)"
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
