# test_backend_devfile -- Test nxt.backend.devfile module
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

import nxt.backend.devfile


@pytest.fixture
def mdev():
    dev = Mock(
        spec_set=(
            "read",
            "write",
            "close",
        )
    )
    return dev


@pytest.fixture
def mopen(mdev):
    with patch("nxt.backend.devfile.open") as fopen:
        fopen.return_value = mdev
        yield fopen


@pytest.fixture
def mglob():
    with patch("nxt.backend.devfile.glob") as glob:
        glob.glob.return_value = ["/dev/nxt"]
        yield glob


def test_devfile(mglob, mopen, mdev):
    # Instantiate backend.
    backend = nxt.backend.devfile.get_backend()
    # Find brick.
    socks = list(backend.find(name="NXT", blah="blah"))
    assert len(socks) == 1
    socks = list(backend.find(filename="/dev/nxt", blah="blah"))
    assert len(socks) == 1
    socks = list(backend.find(blah="blah"))
    assert len(socks) == 1
    sock = socks[0]
    # str.
    assert str(sock).startswith("DevFile (/dev")
    # Connect.
    brick = sock.connect()
    assert mopen.called
    # Send.
    some_bytes = bytes.fromhex("01020304")
    some_len = bytes.fromhex("0400")
    some_bytes_with_len = some_len + some_bytes
    sock.send(some_bytes)
    assert mdev.write.call_args == call(some_bytes_with_len)
    # Recv.
    mdev.read.side_effect = [some_len, some_bytes]
    r = sock.recv()
    assert r == some_bytes
    assert mdev.read.called
    # Close.
    # TODO: brick.__del__ should close the socket, but nobody knows when
    # python calls the destructor.
    sock.close()
    assert mdev.close.called
    del brick


@pytest.mark.nxt("devfile")
def test_devfile_real():
    # Instantiate backend.
    backend = nxt.backend.devfile.get_backend()
    # Find brick.
    socks = list(backend.find())
    assert len(socks) > 0, "no NXT found"
    sock = socks[0]
    # str.
    assert str(sock).startswith("DevFile (/dev")
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
