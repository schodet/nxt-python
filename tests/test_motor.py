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
from nxt.motor import (
    MODE_BRAKE,
    MODE_IDLE,
    MODE_MOTOR_ON,
    MODE_REGULATED,
    PORT_A,
    PORT_B,
    REGULATION_IDLE,
    REGULATION_MOTOR_SPEED,
    REGULATION_MOTOR_SYNC,
    RUN_STATE_IDLE,
    RUN_STATE_RUNNING,
)


@pytest.fixture
def mmotor_factory(mbrick):
    def factory(port):
        mbrick.get_output_state.return_value = (port, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        m = nxt.motor.Motor(mbrick, port)
        assert mbrick.mock_calls == [call.get_output_state(port)]
        mbrick.reset_mock()
        return m

    return factory


@pytest.fixture
def mmotor(mmotor_factory):
    return mmotor_factory(PORT_A)


@pytest.fixture
def mmotorb(mmotor_factory):
    return mmotor_factory(PORT_B)


@pytest.fixture
def msyncmotor(mmotor, mmotorb):
    m = nxt.motor.SynchronizedMotors(mmotor, mmotorb, 50)
    return m


def test_reset_position(mbrick, mmotor):
    mmotor.reset_position(True)
    mmotor.reset_position(False)
    assert mbrick.mock_calls == [
        call.reset_motor_position(PORT_A, True),
        call.reset_motor_position(PORT_A, False),
    ]


def test_run(mbrick, mmotor):
    mmotor.run()
    assert mbrick.mock_calls == [
        # TODO: should be REGULATION_IDLE.
        call.set_output_state(
            PORT_A, 100, MODE_MOTOR_ON, REGULATION_MOTOR_SPEED, 0, RUN_STATE_RUNNING, 0
        ),
    ]


def test_run_regulated(mbrick, mmotor):
    mmotor.run(50, regulated=True)
    assert mbrick.mock_calls == [
        call.set_output_state(
            PORT_A,
            50,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SPEED,
            0,
            RUN_STATE_RUNNING,
            0,
        ),
    ]


def test_brake(mbrick, mmotor):
    mmotor.brake()
    assert mbrick.mock_calls == [
        call.set_output_state(
            PORT_A,
            0,
            MODE_MOTOR_ON | MODE_BRAKE | MODE_REGULATED,
            REGULATION_MOTOR_SPEED,
            0,
            RUN_STATE_RUNNING,
            0,
        ),
    ]


def test_idle(mbrick, mmotor):
    mmotor.idle()
    assert mbrick.mock_calls == [
        call.set_output_state(
            PORT_A, 0, MODE_IDLE, REGULATION_IDLE, 0, RUN_STATE_IDLE, 0
        ),
    ]


def test_weak_turn(mbrick, mmotor):
    mmotor.weak_turn(50, 360)
    assert mbrick.mock_calls == [
        # TODO: why get_output_state?
        call.get_output_state(PORT_A),
        call.set_output_state(
            PORT_A, 50, MODE_MOTOR_ON, REGULATION_IDLE, 0, RUN_STATE_RUNNING, 360
        ),
    ]


def test_turn(mbrick, mmotor, mtime):
    mbrick.get_output_state.side_effect = [
        (PORT_A, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        # Test overshoot.
        (
            PORT_A,
            50,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SPEED,
            0,
            RUN_STATE_RUNNING,
            0,
            720,
            720,
            720,
        ),
    ]
    mmotor.turn(50, 360)
    assert mbrick.mock_calls == [
        call.get_output_state(PORT_A),
        call.set_output_state(
            PORT_A,
            50,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SPEED,
            0,
            RUN_STATE_RUNNING,
            0,
        ),
        call.get_output_state(PORT_A),
        call.set_output_state(
            PORT_A,
            0,
            MODE_MOTOR_ON | MODE_REGULATED | MODE_BRAKE,
            REGULATION_MOTOR_SPEED,
            0,
            RUN_STATE_RUNNING,
            0,
        ),
    ]


def test_turn_blocked(mbrick, mmotor, mtime):
    mtime.time.side_effect = [0, 1]
    with pytest.raises(nxt.motor.BlockedException):
        mmotor.turn(50, 360, brake=False, timeout=0.1, emulate=False)
    assert mbrick.mock_calls == [
        call.get_output_state(PORT_A),
        call.set_output_state(
            PORT_A,
            50,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SPEED,
            0,
            RUN_STATE_RUNNING,
            360,
        ),
        call.get_output_state(PORT_A),
        call.set_output_state(
            PORT_A, 0, MODE_IDLE, REGULATION_IDLE, 0, RUN_STATE_IDLE, 0
        ),
    ]


def test_sync_run(mbrick, msyncmotor):
    msyncmotor.run(50)
    assert mbrick.mock_calls == [
        call.reset_motor_position(PORT_A, True),
        call.reset_motor_position(PORT_B, True),
        call.set_output_state(
            PORT_A,
            50,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SYNC,
            # TODO: why reversed? This does not seems right.
            -50,
            RUN_STATE_RUNNING,
            0,
        ),
        call.set_output_state(
            PORT_B,
            50,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SYNC,
            -50,
            RUN_STATE_RUNNING,
            0,
        ),
    ]


def test_sync_brake(mbrick, msyncmotor):
    msyncmotor.brake()
    assert mbrick.mock_calls == [
        # TODO: this should be possible to make it simpler.
        call.set_output_state(
            PORT_A, 0, MODE_IDLE, REGULATION_IDLE, 0, RUN_STATE_IDLE, 0
        ),
        call.set_output_state(
            PORT_B, 0, MODE_IDLE, REGULATION_IDLE, 0, RUN_STATE_IDLE, 0
        ),
        call.reset_motor_position(PORT_A, True),
        call.reset_motor_position(PORT_B, True),
        call.set_output_state(
            PORT_A,
            0,
            MODE_MOTOR_ON | MODE_BRAKE | MODE_REGULATED,
            REGULATION_MOTOR_SYNC,
            -50,
            RUN_STATE_RUNNING,
            0,
        ),
        call.set_output_state(
            PORT_B,
            0,
            MODE_MOTOR_ON | MODE_BRAKE | MODE_REGULATED,
            REGULATION_MOTOR_SYNC,
            -50,
            RUN_STATE_RUNNING,
            0,
        ),
        call.set_output_state(
            PORT_A, 0, MODE_IDLE, REGULATION_IDLE, -50, RUN_STATE_IDLE, 0
        ),
        call.set_output_state(
            PORT_B, 0, MODE_IDLE, REGULATION_IDLE, -50, RUN_STATE_IDLE, 0
        ),
        call.set_output_state(
            PORT_A,
            0,
            MODE_MOTOR_ON | MODE_BRAKE | MODE_REGULATED,
            REGULATION_MOTOR_SPEED,
            -50,
            RUN_STATE_RUNNING,
            0,
        ),
        call.set_output_state(
            PORT_B,
            0,
            MODE_MOTOR_ON | MODE_BRAKE | MODE_REGULATED,
            REGULATION_MOTOR_SPEED,
            -50,
            RUN_STATE_RUNNING,
            0,
        ),
    ]


def test_sync_idle(mbrick, msyncmotor):
    msyncmotor.idle()
    assert mbrick.mock_calls == [
        call.set_output_state(
            PORT_A, 0, MODE_IDLE, REGULATION_IDLE, 0, RUN_STATE_IDLE, 0
        ),
        call.set_output_state(
            PORT_B, 0, MODE_IDLE, REGULATION_IDLE, 0, RUN_STATE_IDLE, 0
        ),
    ]


def test_sync_turn(mbrick, msyncmotor):
    mbrick.get_output_state.side_effect = [
        (PORT_A, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (PORT_B, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        # Test overshoot.
        (
            PORT_A,
            50,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SYNC,
            0,
            RUN_STATE_RUNNING,
            0,
            720,
            720,
            720,
        ),
        (
            PORT_B,
            0,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SYNC,
            0,
            RUN_STATE_RUNNING,
            0,
            0,
            0,
            0,
        ),
    ]
    msyncmotor.turn(50, 360, brake=False)
    assert mbrick.mock_calls == [
        call.reset_motor_position(PORT_A, True),
        call.reset_motor_position(PORT_B, True),
        call.get_output_state(PORT_A),
        call.get_output_state(PORT_B),
        call.set_output_state(
            PORT_A,
            50,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SYNC,
            -50,
            RUN_STATE_RUNNING,
            0,
        ),
        call.set_output_state(
            PORT_B,
            50,
            MODE_MOTOR_ON | MODE_REGULATED,
            REGULATION_MOTOR_SYNC,
            -50,
            RUN_STATE_RUNNING,
            0,
        ),
        call.get_output_state(PORT_A),
        call.get_output_state(PORT_B),
        call.set_output_state(
            PORT_A, 0, MODE_IDLE, REGULATION_IDLE, 0, RUN_STATE_IDLE, 0
        ),
        call.set_output_state(
            PORT_B, 0, MODE_IDLE, REGULATION_IDLE, 0, RUN_STATE_IDLE, 0
        ),
    ]
