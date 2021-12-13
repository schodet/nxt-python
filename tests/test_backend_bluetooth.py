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
    class BluetoothError(Exception):
        pass

    bluetooth = Mock()
    bluetooth.BluetoothSocket.return_value = msock
    bluetooth.BluetoothError = BluetoothError
    return bluetooth


@pytest.fixture
def mbluetooth_import(mbluetooth):
    orig_import = __import__

    def mocked_import(name, *args):
        if name == "bluetooth":
            return mbluetooth
        return orig_import(name, *args)

    with patch("builtins.__import__", new=mocked_import):
        yield mocked_import


@pytest.fixture
def mbluetooth_import_error():
    orig_import = __import__

    def mocked_import(name, *args):
        if name == "bluetooth":
            raise ImportError("mocked")
        return orig_import(name, *args)

    with patch("builtins.__import__", new=mocked_import):
        yield mocked_import


@pytest.fixture
def mbluetooth_import_not_supported():
    orig_import = __import__

    def mocked_import(name, *args):
        if name == "bluetooth":
            raise Exception("mocked")
        return orig_import(name, *args)

    with patch("builtins.__import__", new=mocked_import):
        yield mocked_import


def test_bluetooth(mbluetooth, mbluetooth_import, msock):
    # Instantiate backend.
    backend = nxt.backend.bluetooth.get_backend()
    # Find brick.
    mbluetooth.discover_devices.return_value = [
        "00:01:02:03:04:05",
    ]
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 1
    brick = bricks[0]
    assert mbluetooth.BluetoothSocket.called
    assert msock.connect.called
    sock = brick._sock
    # str.
    assert str(sock) == "Bluetooth (00:01:02:03:04:05)"
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
    brick.close()
    assert msock.close.called
    # Duplicated close.
    sock.close()


def test_bluetooth_by_name(mbluetooth, mbluetooth_import, msock):
    # Instantiate backend.
    backend = nxt.backend.bluetooth.get_backend()
    # Find brick.
    mbluetooth.discover_devices.return_value = [
        ("00:01:02:03:04:05", "NXT"),
        ("00:01:02:03:04:06", "NXT"),
        ("00:01:02:03:04:07", "NXT2"),
    ]
    bricks = list(backend.find(name="NXT2", blah="blah"))
    assert len(bricks) == 1
    brick = bricks[0]
    assert mbluetooth.BluetoothSocket.called
    assert msock.connect.called
    sock = brick._sock
    # str.
    assert str(sock) == "Bluetooth (00:01:02:03:04:07)"
    # Close.
    brick.close()


def test_bluetooth_by_host(mbluetooth, mbluetooth_import, msock):
    # Instantiate backend.
    backend = nxt.backend.bluetooth.get_backend()
    # Find brick.
    bricks = list(backend.find(host="00:01:02:03:04:05", blah="blah"))
    assert len(bricks) == 1
    brick = bricks[0]
    assert not mbluetooth.discover_devices.called
    assert mbluetooth.BluetoothSocket.called
    assert msock.connect.called
    sock = brick._sock
    # str.
    assert str(sock) == "Bluetooth (00:01:02:03:04:05)"
    # Close.
    brick.close()


def test_bluetooth_by_host_and_name(mbluetooth, mbluetooth_import, msock):
    # Instantiate backend.
    backend = nxt.backend.bluetooth.get_backend()
    # Find brick.
    bricks = list(backend.find(host="00:01:02:03:04:05", name="NXT"))
    assert len(bricks) == 1
    brick = bricks[0]
    assert not mbluetooth.discover_devices.called
    assert mbluetooth.BluetoothSocket.called
    assert msock.connect.called
    sock = brick._sock
    # str.
    assert str(sock) == "Bluetooth (00:01:02:03:04:05)"
    # Close.
    brick.close()


def test_bluetooth_not_present(mbluetooth_import_error):
    assert nxt.backend.bluetooth.get_backend() is None


def test_bluetooth_not_supported(mbluetooth_import_not_supported):
    assert nxt.backend.bluetooth.get_backend() is None


def test_bluetooth_cant_connect(mbluetooth, mbluetooth_import, msock):
    backend = nxt.backend.bluetooth.get_backend()
    mbluetooth.discover_devices.return_value = [
        "00:01:02:03:04:05",
    ]
    msock.connect.side_effect = [mbluetooth.BluetoothError]
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 0


def test_bluetooth_cant_discover(mbluetooth, mbluetooth_import, msock):
    backend = nxt.backend.bluetooth.get_backend()
    mbluetooth.discover_devices.side_effect = [OSError]
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 0
    mbluetooth.discover_devices.side_effect = [mbluetooth.BluetoothError]
    bricks = list(backend.find(blah="blah"))
    assert len(bricks) == 0


@pytest.mark.nxt("bluetooth")
def test_bluetooth_real():
    # Instantiate backend.
    backend = nxt.backend.bluetooth.get_backend()
    # Find brick.
    bricks = list(backend.find())
    assert len(bricks) > 0, "no NXT found"
    brick = bricks[0]
    sock = brick._sock
    # str.
    assert str(sock).startswith("Bluetooth (")
    # Send.
    sock.send(bytes.fromhex("019b"))
    # Recv.
    r = sock.recv()
    assert r.startswith(bytes.fromhex("029b00"))
    # Close.
    brick.close()
