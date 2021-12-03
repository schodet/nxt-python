# conftest -- Common test fixtures for doctest
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
import argparse
from unittest.mock import Mock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_backends():
    brick = Mock()
    brick.get_device_info.return_value = ("NXT", None, None, None)
    brick.play_tone.return_value = None
    backend = Mock()
    backend.find.return_value = [brick]
    with patch("nxt.locator._get_default_backends") as m:
        m.return_value = [backend]
        yield m


@pytest.fixture(autouse=True)
def mock_config():
    with patch("nxt.locator._get_config") as m:
        m.return_value = None
        yield m


@pytest.fixture(autouse=True)
def mock_argparse(monkeypatch):
    ap = Mock()
    parser = Mock()
    ns = Mock()
    ns.backends = None
    ns.name = None
    ns.host = None
    ap.return_value = parser
    parser.add_argument.return_value = None
    parser.parse_args.return_value = ns
    monkeypatch.setattr(argparse, "ArgumentParser", ap)
