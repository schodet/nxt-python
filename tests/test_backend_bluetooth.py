# test_backend_bluetooth -- Test nxt.backend.bluetooth module
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

import nxt.backend.bluetooth


@pytest.fixture
def msock():
    sock = Mock(
        spec_set=(
            "connect",
            "close",
            "send",
            "recv",
        )
    )
    return sock


@pytest.fixture
def mbluetooth(msock):
    with patch("nxt.backend.bluetooth.bluetooth") as bluetooth:
        bluetooth.discover_devices.return_value = [
            ("00:01:02:03:04:05", "NXT"),
            ("00:01:02:03:04:06", "NXT"),
            ("00:01:02:03:04:05", "NXT2"),
        ]
        bluetooth.BluetoothSocket.return_value = msock
        yield bluetooth


def test_bluetooth(mbluetooth, msock):
    # Instantiate backend.
    backend = nxt.backend.bluetooth.get_backend()
    # Find brick.
    socks = list(backend.find(host="00:01:02:03:04:05", name="NXT", blah="blah"))
    assert len(socks) == 1
    sock = socks[0]
    # str.
    assert str(sock) == "Bluetooth (00:01:02:03:04:05)"
    # Connect.
    brick = sock.connect()
    assert mbluetooth.BluetoothSocket.called
    assert msock.connect.called
    # Send.
    some_bytes = bytes.fromhex("01020304")
    some_len = bytes.fromhex("0400")
    some_bytes_with_len = some_len + some_bytes
    sock.send(some_bytes)
    assert msock.send.call_args == call(some_bytes_with_len)
    # Recv.
    msock.recv.side_effect = [some_len, some_bytes]
    r = sock.recv()
    assert r == some_bytes
    assert msock.recv.called
    # Close.
    # TODO: brick.__del__ should close the socket, but nobody knows when
    # python calls the destructor.
    sock.close()
    assert msock.close.called
    del brick


@pytest.mark.nxt("bluetooth")
def test_bluetooth_real():
    # Instantiate backend.
    backend = nxt.backend.bluetooth.get_backend()
    # Find brick.
    socks = list(backend.find())
    assert len(socks) > 0, "no NXT found"
    sock = socks[0]
    # str.
    assert str(sock).startswith("Bluetooth (")
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
