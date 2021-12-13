# nxt.motor module -- Class to control LEGO Mindstorms NXT motors
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, rhn
# Copyright (C) 2010  rhn
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

import enum
import logging
import time

logger = logging.getLogger(__name__)


class Port(enum.Enum):
    """Output port identifier."""

    A = 0
    """Output port A."""

    B = 1
    """Output port B."""

    C = 2
    """Output port C."""


class Mode(enum.Flag):
    """Motor mode.

    These are flags that can be combined together using the `|` operator.
    """

    IDLE = 0x00
    """Keep the motor unpowered."""

    ON = 0x01
    """Enable motor power."""

    BRAKE = 0x02
    """Enable brake, motor input voltage is not left floating, must also be
    :attr:`ON`."""

    REGULATED = 0x04
    """Enable regulation, must also be :attr:`ON`."""


class RegulationMode(enum.Enum):
    """Motor regulation mode."""

    IDLE = 0
    """No regulation."""

    SPEED = 1
    """Speed regulation, :attr:`Mode.REGULATED` must be enabled."""

    SYNC = 2
    """Synchronous regulation of two motors, :attr:`Mode.REGULATED` must be enabled."""


class RunState(enum.Enum):
    """Motor run state."""

    IDLE = 0x00
    """Not running."""

    RAMP_UP = 0x10
    """Ramping speed up."""

    RUNNING = 0x20
    """Running at constant speed."""

    RAMP_DOWN = 0x40
    """Ramping speed down."""


LIMIT_RUN_FOREVER = 0
"""No angle limit."""


class BlockedException(Exception):
    """Raised when a motor is not moving as expected."""

    pass


class OutputState:
    """An object holding the internal state of a motor, not including rotation
    counters."""

    def __init__(self, values):
        (
            self.power,
            self.mode,
            self.regulation_mode,
            self.turn_ratio,
            self.run_state,
            self.tacho_limit,
        ) = values

    def to_list(self):
        """Returns a list of properties that can be used with set_output_state."""
        return [
            self.power,
            self.mode,
            self.regulation_mode,
            self.turn_ratio,
            self.run_state,
            self.tacho_limit,
        ]

    def __str__(self):
        return ", ".join(
            [
                str(self.mode),
                str(self.regulation_mode),
                str(self.turn_ratio),
                str(self.run_state),
                str(self.tacho_limit),
            ]
        )


class TachoInfo:
    """An object containing the information about the rotation of a motor."""

    def __init__(self, values):
        self.tacho_count, self.block_tacho_count, self.rotation_count = values

    def get_target(self, tacho_limit, direction):
        """Returns a TachoInfo object which corresponds to tacho state after
        moving for tacho_limit ticks in the given direction.

        :param int tacho_limit: Move angle.
        :param int direction: 1 (add) or -1 (subtract).
        :return: Updated state.
        :rtype: TachoInfo
        """
        # TODO: adjust other fields
        if abs(direction) != 1:
            raise ValueError("invalid direction")
        new_tacho = self.tacho_count + direction * tacho_limit
        return TachoInfo([new_tacho, None, None])

    def is_greater(self, target, direction):
        return direction * (self.tacho_count - target.tacho_count) > 0

    def is_near(self, target, threshold):
        difference = abs(target.tacho_count - self.tacho_count)
        return difference < threshold

    def __str__(self):
        return str((self.tacho_count, self.block_tacho_count, self.rotation_count))


class SynchronizedTacho:
    def __init__(self, leader_tacho, follower_tacho):
        self.leader_tacho = leader_tacho
        self.follower_tacho = follower_tacho

    def get_target(self, tacho_limit, direction):
        """This method will leave follower's target as None"""
        leader_tacho = self.leader_tacho.get_target(tacho_limit, direction)
        return SynchronizedTacho(leader_tacho, None)

    def is_greater(self, other, direction):
        return self.leader_tacho.is_greater(other.leader_tacho, direction)

    def is_near(self, other, threshold):
        return self.leader_tacho.is_near(other.leader_tacho, threshold)

    def __str__(self):
        if self.follower_tacho is not None:
            t2 = str(self.follower_tacho.tacho_count)
        else:
            t2 = "None"
        t1 = str(self.leader_tacho.tacho_count)
        return f"tacho: {t1} {t2}"


def get_tacho_and_state(values):
    """A convenience function. values is the list of values from
    get_output_state. Returns both OutputState and TachoInfo.
    """
    return OutputState(values[1:7]), TachoInfo(values[7:])


class BaseMotor:
    """Base class for motors"""

    def turn(self, power, tacho_units, brake=True, timeout=1, emulate=True):
        """Use this to turn a motor.

        :param int power: Value between -127 and 128 (an absolute value greater than 64
           is recommended)
        :param int tacho_units: Number of degrees to turn the motor. Values smaller than
           50 are not recommended and may have strange results.
        :param bool brake: Whether or not to hold the motor after the function exits
           (either by reaching the distance or throwing an exception).
        :param int timeout: Number of seconds after which a BlockedException is raised
           if the motor doesn't turn.
        :param bool emulate: If set to ``False``, the motor is aware of the tacho limit.
           If ``True``, a run() function equivalent is used. Warning: motors remember
           their positions and not using emulate may lead to strange behavior,
           especially with synced motors

        The motor will not stop until it turns the desired distance. Accuracy is much
        better over a USB connection than with bluetooth...
        """

        tacho_limit = tacho_units

        if tacho_limit < 0:
            raise ValueError("tacho_units must be greater than 0!")
        # TODO Calibrate the new values for ip socket latency.
        if self.method == "bluetooth":
            threshold = 70
        elif self.method == "usb":
            threshold = 5
        elif self.method == "ipbluetooth":
            threshold = 80
        elif self.method == "ipusb":
            threshold = 15
        else:
            threshold = 30  # compromise

        tacho = self.get_tacho()
        state = self._get_new_state()

        # Update modifiers even if they aren't used, might have been changed
        state.power = power
        if not emulate:
            state.tacho_limit = tacho_limit

        logger.debug("updating motor information")
        self._set_state(state)

        direction = 1 if power > 0 else -1
        logger.debug("tachocount: %s", tacho)
        current_time = time.time()
        tacho_target = tacho.get_target(tacho_limit, direction)

        blocked = False
        try:
            while True:
                time.sleep(self._eta(tacho, tacho_target, power) / 2)

                if not blocked:  # if still blocked, don't reset the counter
                    last_tacho = tacho
                    last_time = current_time

                tacho = self.get_tacho()
                current_time = time.time()
                blocked = self._is_blocked(tacho, last_tacho, direction)
                if blocked:
                    logger.debug("not advancing: %s %s", last_tacho, tacho)
                    # The motor can be up to 80+ degrees in either direction from target
                    # when using Bluetooth.
                    if current_time - last_time > timeout:
                        if tacho.is_near(tacho_target, threshold):
                            break
                        else:
                            raise BlockedException("Blocked!")
                else:
                    logger.debug("advancing: %s %s", last_tacho, tacho)
                if tacho.is_near(tacho_target, threshold) or tacho.is_greater(
                    tacho_target, direction
                ):
                    break
        finally:
            if brake:
                self.brake()
            else:
                self.idle()


class Motor(BaseMotor):
    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self._read_state()
        self.sync = 0
        self.turn_ratio = 0
        self.method = brick._sock.type

    def _set_state(self, state):
        logger.debug("setting brick output state: %s", state)
        list_state = [self.port] + state.to_list()
        self.brick.set_output_state(*list_state)
        self._state = state

    def _read_state(self):
        logger.debug("getting brick output state")
        values = self.brick.get_output_state(self.port)
        self._state, tacho = get_tacho_and_state(values)
        return self._state, tacho

    # def get_tacho_and_state here would allow tacho manipulation

    def _get_state(self):
        """Returns a copy of the current motor state for manipulation."""
        return OutputState(self._state.to_list())

    def _get_new_state(self):
        state = self._get_state()
        if self.sync:
            state.mode = Mode.ON | Mode.REGULATED
            state.regulation_mode = RegulationMode.SYNC
            state.turn_ratio = self.turn_ratio
        else:
            state.mode = Mode.ON | Mode.REGULATED
            state.regulation_mode = RegulationMode.SPEED
        state.run_state = RunState.RUNNING
        state.tacho_limit = LIMIT_RUN_FOREVER
        return state

    def get_tacho(self):
        return self._read_state()[1]

    def reset_position(self, relative):
        """Resets the counters. Relative can be True or False"""
        self.brick.reset_motor_position(self.port, relative)

    def run(self, power=100, regulated=False):
        """Tells the motor to run continuously.

        :param int power: Motor power or speed if `regulated`.
        :param bool regulated: If ``True``, use speed regulation.
        """
        state = self._get_new_state()
        state.power = power
        if not regulated:
            state.mode = Mode.ON
        self._set_state(state)

    def brake(self):
        """Holds the motor in place"""
        state = self._get_new_state()
        state.power = 0
        state.mode = Mode.ON | Mode.BRAKE | Mode.REGULATED
        self._set_state(state)

    def idle(self):
        """Tells the motor to stop whatever it's doing. It also desyncs it."""
        state = self._get_new_state()
        state.power = 0
        state.mode = Mode.IDLE
        state.regulation_mode = RegulationMode.IDLE
        state.run_state = RunState.IDLE
        self._set_state(state)

    def weak_turn(self, power, tacho_units):
        """Tries to turn a motor for the specified distance. This function
        returns immediately, and it's not guaranteed that the motor turns that
        distance. This is an interface to use tacho_limit without
        RegulationMode.SPEED
        """
        tacho_limit = tacho_units
        state = self._get_new_state()

        # Update modifiers even if they aren't used, might have been changed
        state.mode = Mode.ON
        state.regulation_mode = RegulationMode.IDLE
        state.power = power
        state.tacho_limit = tacho_limit

        logger.debug("updating motor information")
        self._set_state(state)

    def _eta(self, current, target, power):
        """Returns time in seconds. Do not trust it too much"""
        tacho = abs(current.tacho_count - target.tacho_count)
        return (float(tacho) / abs(power)) / 5

    def _is_blocked(self, tacho, last_tacho, direction):
        """Returns if any of the engines is blocked"""
        return direction * (last_tacho.tacho_count - tacho.tacho_count) >= 0


class SynchronizedMotors(BaseMotor):
    """The object used to make two motors run in sync. Many objects may be
    present at the same time but they can't be used at the same time.
    Warning! Movement methods reset tacho counter.
    THIS CODE IS EXPERIMENTAL!!!
    """

    def __init__(self, leader, follower, turn_ratio):
        """Turn ratio can be >= 0 only! If you want to have it reversed,
        change motor order.
        """
        if follower.brick != leader.brick:
            raise ValueError("motors belong to different bricks")
        self.leader = leader
        self.follower = follower
        # Being from the same brick, they both have the same com method.
        self.method = self.leader.method

        if turn_ratio < 0:
            raise ValueError("turn ratio < 0, change motor order instead")

        if self.leader.port == self.follower.port:
            raise ValueError("The same motor passed twice")
        elif self.leader.port.value > self.follower.port.value:
            self.turn_ratio = turn_ratio
        else:
            logger.debug("reversed")
            self.turn_ratio = -turn_ratio

    def _get_new_state(self):
        return self.leader._get_new_state()

    def _set_state(self, state):
        self.leader._set_state(state)
        self.follower._set_state(state)

    def get_tacho(self):
        leadertacho = self.leader.get_tacho()
        followertacho = self.follower.get_tacho()
        return SynchronizedTacho(leadertacho, followertacho)

    def reset_position(self, relative):
        """Resets the counters. Relative can be True or False"""
        self.leader.reset_position(relative)
        self.follower.reset_position(relative)

    def _enable(self):  # This works as expected. I'm not sure why.
        # self._disable()
        self.reset_position(True)
        self.leader.sync = True
        self.follower.sync = True
        self.leader.turn_ratio = self.turn_ratio
        self.follower.turn_ratio = self.turn_ratio

    def _disable(self):  # This works as expected. (tacho is reset ok)
        self.leader.sync = False
        self.follower.sync = False
        # self.reset_position(True)
        self.leader.idle()
        self.follower.idle()
        # self.reset_position(True)

    def run(self, power=100):
        """Warning! After calling this method, make sure to call idle. The
        motors are reported to behave wildly otherwise.
        """
        self._enable()
        self.leader.run(power, True)
        self.follower.run(power, True)

    def brake(self):
        self._disable()  # reset the counters
        self._enable()
        self.leader.brake()  # brake both motors at the same time
        self.follower.brake()
        self._disable()  # now brake as usual
        self.leader.brake()
        self.follower.brake()

    def idle(self):
        self._disable()

    def turn(self, power, tacho_units, brake=True, timeout=1):
        self._enable()
        # non-emulation is a nightmare, tacho is being counted differently
        try:
            if power < 0:
                self.leader, self.follower = self.follower, self.leader
            BaseMotor.turn(self, power, tacho_units, brake, timeout, emulate=True)
        finally:
            if power < 0:
                self.leader, self.follower = self.follower, self.leader

    def _eta(self, tacho, target, power):
        return self.leader._eta(tacho.leader_tacho, target.leader_tacho, power)

    def _is_blocked(self, tacho, last_tacho, direction):
        # no need to check both, they're synced
        return self.leader._is_blocked(
            tacho.leader_tacho, last_tacho.leader_tacho, direction
        )
