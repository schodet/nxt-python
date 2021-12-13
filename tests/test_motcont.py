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

import nxt.error
import nxt.motcont
import nxt.motor


@pytest.fixture
def mc(mbrick):
    return nxt.motcont.MotCont(mbrick)


def msg(x):
    """Remove spaces and encode to bytes."""
    return x.replace(" ", "").encode("ascii")


def test_cmd(mbrick, mtime, mc):
    mc.cmd(nxt.motor.Port.B, -100, 1000, speedreg=1, smoothstart=0, brake=0)
    # Using the same port yield a delay.
    mc.cmd(nxt.motor.Port.B, 10, 0, speedreg=0, smoothstart=1, brake=1)
    assert mbrick.mock_calls == [
        call.message_write(1, msg("1 1 200 001000 2")),
        call.message_write(1, msg("1 1 010 000000 5")),
    ]
    assert mtime.sleep.mock_calls == [
        call(0.015),
    ]


def test_cmd_nosleep(mbrick, mtime, mc):
    mc.cmd(nxt.motor.Port.B, -100, 1000, speedreg=1, smoothstart=0, brake=0)
    # Using a different port yield no delay.
    mc.cmd(nxt.motor.Port.C, 10, 0, speedreg=0, smoothstart=1, brake=1)
    assert mbrick.mock_calls == [
        call.message_write(1, msg("1 1 200 001000 2")),
        call.message_write(1, msg("1 2 010 000000 5")),
    ]
    assert mtime.sleep.mock_calls == []


def test_cmd_twomotors(mbrick, mtime, mc):
    mc.cmd(nxt.motor.Port.B, -100, 1000, speedreg=1, smoothstart=0, brake=0)
    # When using two motors, there should be a delay as the same motor is used again.
    mc.cmd(
        (nxt.motor.Port.B, nxt.motor.Port.C), 10, 0, speedreg=0, smoothstart=1, brake=1
    )
    assert mbrick.mock_calls == [
        call.message_write(1, msg("1 1 200 001000 2")),
        call.message_write(1, msg("1 5 010 000000 5")),
    ]
    assert mtime.sleep.mock_calls == [
        call(0.015),
    ]


def test_cmd_threemotors(mbrick, mtime, mc):
    with pytest.raises(ValueError):
        mc.cmd(
            (nxt.motor.Port.A, nxt.motor.Port.B, nxt.motor.Port.C),
            -100,
            1000,
            speedreg=1,
            smoothstart=0,
            brake=0,
        )


def test_reset_tacho(mbrick, mc):
    mc.reset_tacho(nxt.motor.Port.B)
    assert mbrick.mock_calls == [call.message_write(1, msg("2 1"))]


def test_is_ready(mbrick, mtime, mc):
    mbrick.message_read.side_effect = [(1, msg("1 1")), (1, msg("2 0"))]
    ready = mc.is_ready(nxt.motor.Port.B)
    not_ready = mc.is_ready(nxt.motor.Port.C)
    assert mtime.sleep.called
    assert mbrick.mock_calls == [
        call.message_write(1, msg("3 1")),
        call.message_read(0, 1, 1),
        call.message_write(1, msg("3 2")),
        call.message_read(0, 1, 1),
    ]
    assert ready is True
    assert not_ready is False


def test_is_ready_error(mbrick, mc):
    mbrick.message_read.return_value = (1, msg("0 1"))
    with pytest.raises(nxt.error.ProtocolError):
        mc.is_ready(nxt.motor.Port.B)


def test_set_output_state(mbrick, mc):
    mc.set_output_state(nxt.motor.Port.C, -100, 1000, speedreg=1)
    mc.set_output_state(nxt.motor.Port.C, 10, 0, speedreg=0)
    assert mbrick.mock_calls == [
        call.message_write(1, msg("4 2 200 001000 1")),
        call.message_write(1, msg("4 2 010 000000 0")),
    ]


def test_start(mbrick, mc):
    mc.start()
    assert mbrick.mock_calls == [
        call.stop_program(),
        call.start_program("MotorControl22.rxe"),
    ]


def test_start_not_running(mbrick, mc):
    mbrick.stop_program.side_effect = [nxt.error.DirectProtocolError("")]
    mc.start()
    assert mbrick.mock_calls == [
        call.stop_program(),
        call.start_program("MotorControl22.rxe"),
    ]


def test_stop(mbrick):
    mc = nxt.motcont.MotCont(mbrick)
    mc.stop()
    assert mbrick.mock_calls == [
        call.stop_program(),
    ]
