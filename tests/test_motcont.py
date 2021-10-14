# test_motcont -- Test nxt.motcont module
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
from unittest.mock import call

import pytest

import nxt.motor


def msg(x):
    """Remove spaces and encode to bytes."""
    return x.replace(" ", "").encode("ascii")


def test_cmd(mbrick):
    mbrick.mc.cmd(nxt.motor.PORT_B, -100, 1000, speedreg=1, smoothstart=0, brake=0)
    mbrick.mc.cmd(nxt.motor.PORT_B, 10, 0, speedreg=0, smoothstart=1, brake=1)
    assert mbrick.mock_calls == [
        call.message_write(1, msg("1 1 200 001000 2")),
        call.message_write(1, msg("1 1 010 000000 5")),
    ]


def test_move_to(mbrick):
    mbrick.get_output_state.return_value = (
        nxt.motor.PORT_B,
        0,
        0,
        0,
        0,
        0,
        1000,
        2000,
        3000,
        4000,
    )
    mbrick.mc.move_to(nxt.motor.PORT_B, 100, 10000)
    assert mbrick.mock_calls == [
        call.get_output_state(nxt.motor.PORT_B),
        call.get_output_state(nxt.motor.PORT_B),
        call.message_write(1, msg("1 1 100 007000 2")),
    ]


def test_reset_tacho(mbrick):
    mbrick.mc.reset_tacho(nxt.motor.PORT_B)
    assert mbrick.mock_calls == [call.message_write(1, msg("2 1"))]


def test_is_ready(mbrick, mtime):
    mbrick.message_read.side_effect = [(1, msg("1 1")), (1, msg("2 0"))]
    ready = mbrick.mc.is_ready(nxt.motor.PORT_B)
    not_ready = mbrick.mc.is_ready(nxt.motor.PORT_C)
    assert mtime.sleep.called
    assert mbrick.mock_calls == [
        call.message_write(1, msg("3 1")),
        call.message_read(0, 1, 1),
        call.message_write(1, msg("3 2")),
        call.message_read(0, 1, 1),
    ]
    assert ready is True
    assert not_ready is False


def test_is_ready_error(mbrick):
    mbrick.message_read.return_value = (1, msg("0 1"))
    with pytest.raises(nxt.motcont.MotorConError):
        mbrick.mc.is_ready(nxt.motor.PORT_B)


def test_set_output_state(mbrick):
    mbrick.mc.set_output_state(nxt.motor.PORT_C, -100, 1000, speedreg=1)
    mbrick.mc.set_output_state(nxt.motor.PORT_C, 10, 0, speedreg=0)
    assert mbrick.mock_calls == [
        call.message_write(1, msg("4 2 200 001000 1")),
        call.message_write(1, msg("4 2 010 000000 0")),
    ]


def test_start(mbrick):
    mbrick.mc.start()
    assert mbrick.mock_calls == [
        call.stop_program(),
        call.start_program("MotorControl22.rxe"),
    ]


def test_start_not_running(mbrick):
    mbrick.stop_program.side_effect = [nxt.error.DirProtError("")]
    mbrick.mc.start()
    assert mbrick.mock_calls == [
        call.stop_program(),
        call.start_program("MotorControl22.rxe"),
    ]


def test_stop(mbrick):
    mbrick.mc.stop()
    assert mbrick.mock_calls == [
        call.stop_program(),
    ]
