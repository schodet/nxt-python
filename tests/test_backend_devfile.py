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
        yield glob


@pytest.fixture
def mtty():
    with patch("nxt.backend.devfile.tty") as tty:
        yield tty


@pytest.fixture
def mplatform():
    with patch("nxt.backend.devfile.platform") as platform:
        yield platform


def test_devfile(mopen, mtty, mdev):
    # Instantiate backend.
    backend = nxt.backend.devfile.get_backend()
    # Find brick.
    bricks = list(backend.find(filename="/dev/nxt", blah="blah"))
    assert len(bricks) == 1
    brick = bricks[0]
    assert mopen.called
    assert mtty.setraw.called
    sock = brick._sock
    # str.
    assert str(sock).startswith("DevFile (/dev")
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
    brick.close()
    assert mdev.close.called
    # Duplicated close.
    sock.close()


def test_devfile_linux(mopen, mtty, mglob, mplatform):
    mplatform.system.return_value = "Linux"
    mglob.glob.return_value = ["/dev/rfcomm0"]
    backend = nxt.backend.devfile.get_backend()
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 1
    assert mglob.mock_calls == [call.glob("/dev/rfcomm*")]


def test_devfile_darwin(mopen, mtty, mglob, mplatform):
    mplatform.system.return_value = "Darwin"
    mglob.glob.return_value = ["/dev/tty.NXT-DevB-1"]
    backend = nxt.backend.devfile.get_backend()
    bricks = list(backend.find(name="NXT", blah="blah"))
    assert len(bricks) == 1
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 1
    assert mglob.mock_calls == [
        call.glob("/dev/*NXT*"),
        call.glob("/dev/*-DevB*"),
    ]


def test_devfile_other(mplatform):
    mplatform.system.return_value = "MSDos"
    backend = nxt.backend.devfile.get_backend()
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 0


def test_devfile_cant_connect(mopen, mtty, mdev):
    backend = nxt.backend.devfile.get_backend()
    mopen.side_effect = [OSError]
    bricks = list(backend.find(filename="/dev/nxt", blah="blah"))
    assert len(bricks) == 0


@pytest.mark.nxt("devfile")
def test_devfile_real():
    # Instantiate backend.
    backend = nxt.backend.devfile.get_backend()
    # Find brick.
    bricks = list(backend.find())
    assert len(bricks) > 0, "no NXT found"
    brick = bricks[0]
    sock = brick._sock
    # str.
    assert str(sock).startswith("DevFile (/dev")
    # Send.
    sock.send(bytes.fromhex("019b"))
    # Recv.
    r = sock.recv()
    assert r.startswith(bytes.fromhex("029b00"))
    # Close.
    brick.close()
