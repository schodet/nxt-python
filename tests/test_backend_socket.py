# test_backend_socket -- Test nxt.backend.socket module
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

import nxt.backend.socket


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
    with patch("nxt.backend.socket.socket") as socket:
        socket.socket.return_value = mdev
        yield socket


def test_socket(msocket, mdev):
    # Instantiate backend.
    backend = nxt.backend.socket.get_backend()
    # Find brick.
    mdev.recv.return_value = b"usb"
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 1
    brick = bricks[0]
    assert brick._sock.type == "ipusb"
    assert msocket.socket.called
    assert mdev.connect.called
    assert mdev.send.call_args == call(b"\x98")
    sock = brick._sock
    # str.
    assert str(sock) == "Socket (localhost:2727)"
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
    brick.close()
    assert mdev.send.call_args == call(b"\x99")
    assert mdev.close.called
    # Duplicated close.
    sock.close()


def test_socket_cant_connect(msocket, mdev):
    backend = nxt.backend.socket.get_backend()
    mdev.connect.side_effect = [ConnectionRefusedError]
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 0


@pytest.mark.nxt("socket")
def test_socket_real():
    # Instantiate backend.
    backend = nxt.backend.socket.get_backend()
    # Find brick.
    bricks = list(backend.find())
    assert len(bricks) > 0, "no NXT found"
    brick = bricks[0]
    sock = brick._sock
    # str.
    assert str(sock) == "Socket (localhost:2727)"
    # Send.
    sock.send(bytes.fromhex("019b"))
    # Recv.
    r = sock.recv()
    assert r.startswith(bytes.fromhex("029b00"))
    # Close.
    brick.close()
