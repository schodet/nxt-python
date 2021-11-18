# conftest -- Common test fixtures
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
from unittest.mock import Mock, patch

import pytest

import nxt.brick
import nxt.motcont


def pytest_addoption(parser):
    parser.addoption(
        "--run-nxt",
        action="append",
        choices=("usb", "bluetooth"),
        default=[],
        help="run tests needing a real NXT connected over given interface",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "nxt: mark test as needing a real NXT")


def pytest_collection_modifyitems(config, items):
    run_nxt = config.getoption("--run-nxt")
    for item in items:
        for marker in item.iter_markers("nxt"):
            if marker.args[0] not in run_nxt:
                item.add_marker(
                    pytest.mark.skip(
                        reason="need --run-nxt=%s option to run" % marker.args[0]
                    )
                )


@pytest.fixture
def mtime():
    current_time = 0
    with patch("nxt.motcont.time") as time:

        def timef():
            nonlocal current_time
            return current_time

        def sleepf(delay):
            nonlocal current_time
            current_time += delay

        time.time.side_effect = timef
        time.sleep.side_effect = sleepf
        yield time


@pytest.fixture
def mbrick(mtime):
    """A brick with mocked low level functions."""
    b = Mock()

    def find_files(pattern):
        return nxt.brick.Brick.find_files(b, pattern)

    def find_modules(pattern):
        return nxt.brick.Brick.find_modules(b, pattern)

    def open_file(*args, **kwargs):
        return nxt.brick.Brick.open_file(b, *args, **kwargs)

    b.sock.bsize = 60
    b.find_files = find_files
    b.find_modules = find_modules
    b.open_file = open_file
    return b
