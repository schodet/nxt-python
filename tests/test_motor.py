# test_motor -- Test nxt.motor module
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
from nxt.motor import Mode, Port, RegulationMode, RunState


@pytest.fixture
def mmotor_factory(mbrick):
    def factory(port):
        mbrick.get_output_state.return_value = (
            port,
            0,
            Mode.IDLE,
            RegulationMode.IDLE,
            0,
            RunState.IDLE,
            0,
            0,
            0,
            0,
        )
        m = mbrick.get_motor(port)
        assert mbrick.mock_calls == [call.get_output_state(port)]
        mbrick.reset_mock()
        return m

    return factory


@pytest.fixture
def mmotor(mmotor_factory):
    return mmotor_factory(Port.A)


@pytest.fixture
def mmotorb(mmotor_factory):
    return mmotor_factory(Port.B)


@pytest.fixture
def msyncmotor(mmotor, mmotorb):
    m = nxt.motor.SynchronizedMotors(mmotor, mmotorb, 50)
    return m


def test_reset_position(mbrick, mmotor):
    mmotor.reset_position(True)
    mmotor.reset_position(False)
    assert mbrick.mock_calls == [
        call.reset_motor_position(Port.A, True),
        call.reset_motor_position(Port.A, False),
    ]


def test_run(mbrick, mmotor):
    mmotor.run()
    assert mbrick.mock_calls == [
        # TODO: should be RegulationMode.IDLE.
        call.set_output_state(
            Port.A, 100, Mode.ON, RegulationMode.SPEED, 0, RunState.RUNNING, 0
        ),
    ]


def test_run_regulated(mbrick, mmotor):
    mmotor.run(50, regulated=True)
    assert mbrick.mock_calls == [
        call.set_output_state(
            Port.A,
            50,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SPEED,
            0,
            RunState.RUNNING,
            0,
        ),
    ]


def test_brake(mbrick, mmotor):
    mmotor.brake()
    assert mbrick.mock_calls == [
        call.set_output_state(
            Port.A,
            0,
            Mode.ON | Mode.BRAKE | Mode.REGULATED,
            RegulationMode.SPEED,
            0,
            RunState.RUNNING,
            0,
        ),
    ]


def test_idle(mbrick, mmotor):
    mmotor.idle()
    assert mbrick.mock_calls == [
        call.set_output_state(
            Port.A, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0
        ),
    ]


def test_weak_turn(mbrick, mmotor):
    mmotor.weak_turn(50, 360)
    assert mbrick.mock_calls == [
        call.set_output_state(
            Port.A, 50, Mode.ON, RegulationMode.IDLE, 0, RunState.RUNNING, 360
        ),
    ]


def test_turn(mbrick, mmotor, mtime):
    mbrick.get_output_state.side_effect = [
        (Port.A, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0, 0, 0, 0),
        # Test overshoot.
        (
            Port.A,
            50,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SPEED,
            0,
            RunState.RUNNING,
            0,
            720,
            720,
            720,
        ),
    ]
    mmotor.turn(50, 360)
    assert mbrick.mock_calls == [
        call.get_output_state(Port.A),
        call.set_output_state(
            Port.A,
            50,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SPEED,
            0,
            RunState.RUNNING,
            0,
        ),
        call.get_output_state(Port.A),
        call.set_output_state(
            Port.A,
            0,
            Mode.ON | Mode.REGULATED | Mode.BRAKE,
            RegulationMode.SPEED,
            0,
            RunState.RUNNING,
            0,
        ),
    ]


def test_turn_blocked(mbrick, mmotor, mtime):
    mtime.time.side_effect = [0, 1]
    with pytest.raises(nxt.motor.BlockedException):
        mmotor.turn(50, 360, brake=False, timeout=0.1, emulate=False)
    assert mbrick.mock_calls == [
        call.get_output_state(Port.A),
        call.set_output_state(
            Port.A,
            50,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SPEED,
            0,
            RunState.RUNNING,
            360,
        ),
        call.get_output_state(Port.A),
        call.set_output_state(
            Port.A, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0
        ),
    ]


def test_sync_run(mbrick, msyncmotor):
    msyncmotor.run(50)
    assert mbrick.mock_calls == [
        call.reset_motor_position(Port.A, True),
        call.reset_motor_position(Port.B, True),
        call.set_output_state(
            Port.A,
            50,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SYNC,
            # TODO: why reversed? This does not seems right.
            -50,
            RunState.RUNNING,
            0,
        ),
        call.set_output_state(
            Port.B,
            50,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SYNC,
            -50,
            RunState.RUNNING,
            0,
        ),
    ]


def test_sync_brake(mbrick, msyncmotor):
    msyncmotor.brake()
    assert mbrick.mock_calls == [
        # TODO: this should be possible to make it simpler.
        call.set_output_state(
            Port.A, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0
        ),
        call.set_output_state(
            Port.B, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0
        ),
        call.reset_motor_position(Port.A, True),
        call.reset_motor_position(Port.B, True),
        call.set_output_state(
            Port.A,
            0,
            Mode.ON | Mode.BRAKE | Mode.REGULATED,
            RegulationMode.SYNC,
            -50,
            RunState.RUNNING,
            0,
        ),
        call.set_output_state(
            Port.B,
            0,
            Mode.ON | Mode.BRAKE | Mode.REGULATED,
            RegulationMode.SYNC,
            -50,
            RunState.RUNNING,
            0,
        ),
        call.set_output_state(
            Port.A, 0, Mode.IDLE, RegulationMode.IDLE, -50, RunState.IDLE, 0
        ),
        call.set_output_state(
            Port.B, 0, Mode.IDLE, RegulationMode.IDLE, -50, RunState.IDLE, 0
        ),
        call.set_output_state(
            Port.A,
            0,
            Mode.ON | Mode.BRAKE | Mode.REGULATED,
            RegulationMode.SPEED,
            -50,
            RunState.RUNNING,
            0,
        ),
        call.set_output_state(
            Port.B,
            0,
            Mode.ON | Mode.BRAKE | Mode.REGULATED,
            RegulationMode.SPEED,
            -50,
            RunState.RUNNING,
            0,
        ),
    ]


def test_sync_idle(mbrick, msyncmotor):
    msyncmotor.idle()
    assert mbrick.mock_calls == [
        call.set_output_state(
            Port.A, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0
        ),
        call.set_output_state(
            Port.B, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0
        ),
    ]


def test_sync_turn(mbrick, msyncmotor):
    mbrick.get_output_state.side_effect = [
        (Port.A, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0, 0, 0, 0),
        (Port.B, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0, 0, 0, 0),
        # Test overshoot.
        (
            Port.A,
            50,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SYNC,
            0,
            RunState.RUNNING,
            0,
            720,
            720,
            720,
        ),
        (
            Port.B,
            0,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SYNC,
            0,
            RunState.RUNNING,
            0,
            0,
            0,
            0,
        ),
    ]
    msyncmotor.turn(50, 360, brake=False)
    assert mbrick.mock_calls == [
        call.reset_motor_position(Port.A, True),
        call.reset_motor_position(Port.B, True),
        call.get_output_state(Port.A),
        call.get_output_state(Port.B),
        call.set_output_state(
            Port.A,
            50,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SYNC,
            -50,
            RunState.RUNNING,
            0,
        ),
        call.set_output_state(
            Port.B,
            50,
            Mode.ON | Mode.REGULATED,
            RegulationMode.SYNC,
            -50,
            RunState.RUNNING,
            0,
        ),
        call.get_output_state(Port.A),
        call.get_output_state(Port.B),
        call.set_output_state(
            Port.A, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0
        ),
        call.set_output_state(
            Port.B, 0, Mode.IDLE, RegulationMode.IDLE, 0, RunState.IDLE, 0
        ),
    ]
