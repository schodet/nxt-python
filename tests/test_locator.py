# test_locator -- Test nxt.locator module
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

import nxt.locator


def make_backend_mock():
    m = Mock(spec_set=("get_backend",))
    backend = Mock(spec_set=("find",))
    backend.find.return_value = []
    m.get_backend.return_value = backend
    return m


@pytest.fixture
def mbackend_usb():
    return make_backend_mock()


@pytest.fixture
def mbackend_bluetooth():
    return make_backend_mock()


@pytest.fixture
def mbackend_devfile():
    return make_backend_mock()


@pytest.fixture
def mbackend_socket():
    return make_backend_mock()


@pytest.fixture(autouse=True)
def mimportlib(mbackend_usb, mbackend_bluetooth, mbackend_devfile, mbackend_socket):
    def import_module(name):
        if name == "nxt.backend.usb":
            return mbackend_usb
        if name == "nxt.backend.bluetooth":
            return mbackend_bluetooth
        if name == "nxt.backend.devfile":
            return mbackend_devfile
        if name == "nxt.backend.socket":
            return mbackend_socket
        raise ImportError("no such module")

    with patch("nxt.locator.importlib") as m:
        m.import_module.side_effect = import_module
        yield m


@pytest.fixture(autouse=True)
def mconfigparser():
    parser = Mock(spec_set=("read", "__contains__", "__getitem__"))
    parser.read.return_value = ["some", "files"]
    parser.__contains__ = Mock(return_value=True)
    parser.__getitem__ = Mock(return_value=dict())
    with patch("nxt.locator.configparser") as m:
        m.ConfigParser.return_value = parser
        m.DEFAULTSECT = "DEFAULT"
        yield m


def test_find_no_found():
    with pytest.raises(nxt.locator.BrickNotFoundError):
        nxt.locator.find()


def test_find_first(mbackend_usb, mbackend_bluetooth, mbrick, mbrick2):
    mbackend_usb.get_backend().find.return_value = [mbrick]
    mbackend_bluetooth.get_backend().find.return_value = [mbrick2]
    assert nxt.locator.find() is mbrick


def test_find_first_second_backend(mbackend_usb, mbackend_bluetooth, mbrick):
    mbackend_usb.get_backend().find.return_value = []
    mbackend_bluetooth.get_backend().find.return_value = [mbrick]
    assert nxt.locator.find() is mbrick


def test_find_by_name(mbackend_usb, mbrick, mbrick2):
    mbackend_usb.get_backend().find.return_value = [mbrick, mbrick2]
    mbrick.get_device_info.return_value = "NXT", None, None, None
    mbrick2.get_device_info.return_value = "NXT2", None, None, None
    assert nxt.locator.find(name="NXT2") is mbrick2


def test_find_by_host(mbackend_usb, mbrick, mbrick2):
    mbackend_usb.get_backend().find.return_value = [mbrick, mbrick2]
    mbrick.get_device_info.return_value = "NXT", "00:16:53:00:00:01", None, None
    mbrick2.get_device_info.return_value = "NXT2", "00:16:53:00:00:02", None, None
    assert nxt.locator.find(host="00:16:53:00:00:02") is mbrick2


def test_find_by_custom(mbackend_usb, mbrick, mbrick2):
    mbackend_usb.get_backend().find.return_value = [mbrick, mbrick2]
    assert nxt.locator.find(custom_match=lambda b: b is mbrick2) is mbrick2


def test_find_all(mbackend_usb, mbackend_bluetooth, mbrick, mbrick2):
    mbackend_usb.get_backend().find.return_value = [mbrick]
    mbackend_bluetooth.get_backend().find.return_value = [mbrick2]
    bricks = list(nxt.locator.find(find_all=True))
    assert len(bricks) == 2
    assert bricks[0] == mbrick
    assert bricks[1] == mbrick2


def test_find_filename(mbackend_devfile, mbrick):
    mbackend_devfile.get_backend().find.return_value = [mbrick]
    assert nxt.locator.find(filename="/dev/rfcomm0") is mbrick


def test_find_socket(mbackend_socket, mbrick):
    mbackend_socket.get_backend().find.return_value = [mbrick]
    assert nxt.locator.find(server_host="localhost") is mbrick
    assert nxt.locator.find(server_port=2727) is mbrick


def test_find_bad_backend():
    with pytest.raises(ValueError):
        assert nxt.locator.find(backends=["bad!"])


def test_find_backend_not_found():
    with pytest.raises(ImportError):
        assert nxt.locator.find(backends=["unknown"])


def test_find_no_config(mbackend_usb, mconfigparser, mbrick):
    mbackend_usb.get_backend().find.return_value = [mbrick]
    assert nxt.locator.find(config=None) is mbrick
    assert not mconfigparser.ConfigParser.called


def test_find_no_config_section(mbackend_usb, mconfigparser, mbrick):
    mbackend_usb.get_backend().find.return_value = [mbrick]
    parser = mconfigparser.ConfigParser.return_value
    parser.__contains__.return_value = False
    assert nxt.locator.find() is mbrick
    assert parser.__contains__.mock_calls == [
        call("default"),
    ]
    assert parser.__getitem__.mock_calls == [
        call("DEFAULT"),
    ]


def test_find_config_backends(
    mbackend_usb,
    mbackend_bluetooth,
    mbackend_devfile,
    mbackend_socket,
    mconfigparser,
    mbrick,
):
    mbackend_socket.get_backend().find.return_value = [mbrick]
    parser = mconfigparser.ConfigParser.return_value
    parser.__getitem__.return_value = dict(backends="devfile socket")
    assert nxt.locator.find() is mbrick
    assert not mbackend_usb.get_backend().find.called
    assert not mbackend_bluetooth.get_backend().find.called
    assert mbackend_devfile.get_backend().find.called
    assert mbackend_socket.get_backend().find.called


def test_find_config_backends_override(
    mbackend_usb, mbackend_socket, mconfigparser, mbrick
):
    mbackend_usb.get_backend().find.return_value = [mbrick]
    parser = mconfigparser.ConfigParser.return_value
    parser.__getitem__.return_value = dict(backends="socket")
    assert nxt.locator.find(backends=["usb"]) is mbrick
    assert mbackend_usb.get_backend().find.called
    assert not mbackend_socket.get_backend().find.called


def test_find_config(mbackend_usb, mconfigparser, mbrick):
    mbackend_usb.get_backend().find.return_value = [mbrick]
    mbrick.get_device_info.return_value = "NXT", "00:16:53:00:00:01", None, None
    parser = mconfigparser.ConfigParser.return_value
    parser.__getitem__.return_value = dict(name="NXT", host="00:16:53:00:00:01")
    assert nxt.locator.find() is mbrick
    assert mbackend_usb.get_backend().find.mock_calls == [
        call(name="NXT", host="00:16:53:00:00:01"),
    ]


def test_find_config_override(mbackend_usb, mconfigparser, mbrick):
    mbackend_usb.get_backend().find.return_value = [mbrick]
    mbrick.get_device_info.return_value = "NXT2", "00:16:53:00:00:02", None, None
    parser = mconfigparser.ConfigParser.return_value
    parser.__getitem__.return_value = dict(name="NXT", host="00:16:53:00:00:01")
    assert nxt.locator.find(name="NXT2") is mbrick
    assert mbackend_usb.get_backend().find.mock_calls == [
        call(name="NXT2", host=None),
    ]


def test_find_config_filters(mbackend_usb, mconfigparser, mbrick):
    mbackend_usb.get_backend().find.return_value = [mbrick]
    parser = mconfigparser.ConfigParser.return_value
    parser.__getitem__.return_value = dict(test="testing")
    assert nxt.locator.find() is mbrick
    assert mbackend_usb.get_backend().find.mock_calls == [
        call(name=None, host=None, test="testing"),
    ]


def test_find_config_filenames(mbackend_usb, mconfigparser, mbrick):
    mbackend_usb.get_backend().find.return_value = [mbrick]
    parser = mconfigparser.ConfigParser.return_value
    assert nxt.locator.find(config_filenames=["some", "files"]) is mbrick
    assert parser.read.mock_calls == [
        call(["some", "files"]),
    ]
