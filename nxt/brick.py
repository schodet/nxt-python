# nxt.brick module -- Classes to represent LEGO Mindstorms NXT bricks
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, rhn
# Copyright (C) 2010  rhn, Marcus Wanner, zonedabone
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

import io
import sys
import threading
import time
from collections.abc import Iterator
from types import TracebackType
from typing import IO, Any, Optional, cast

import nxt.error
import nxt.motor
import nxt.sensor
import nxt.sensor.digital
from nxt.telegram import Opcode, Telegram

__all__ = ["Brick"]


# No Buffer before 3.12.
if sys.version_info >= (3, 12):
    from collections.abc import Buffer
else:
    from typing import Any as Buffer


class RawFileReader(io.RawIOBase):
    """Implement RawIOBase for reading a file on the NXT brick."""

    def __init__(self, brick: "Brick", name: str) -> None:
        self._brick = brick
        self._handle, self._remaining = brick.file_open_read(name)

    def close(self) -> None:
        if not self.closed:
            super().close()
            self._brick.file_close(self._handle)

    def readable(self) -> bool:
        return True

    def readinto(self, b: Buffer) -> int:
        rsize = min(self._brick._sock.bsize, self._remaining, len(b))
        if rsize == 0:
            return 0
        _, data = self._brick.file_read(self._handle, rsize)
        size = len(data)
        self._remaining -= size
        b[0:size] = data
        return size


class RawFileWriter(io.RawIOBase):
    """Implement RawIOBase for writing a file on the NXT brick."""

    def __init__(self, brick: "Brick", name: str, size: int) -> None:
        self._brick = brick
        self._handle = brick.file_open_write(name, size)
        self._remaining = size

    def close(self) -> None:
        if not self.closed:
            super().close()
            self._brick.file_close(self._handle)

    def writable(self) -> bool:
        return True

    def write(self, b: Buffer) -> int:
        if self.closed:
            raise ValueError("write to closed file")
        if self._remaining == 0:
            raise ValueError("write to a full file")
        wsize = min(self._brick._sock.bsize, self._remaining, len(b))
        _, size = self._brick.file_write(self._handle, bytes(b[:wsize]))
        self._remaining -= size
        return size


class Brick:
    """Object connected to a NXT brick.

    It provides low level access to brick commands and high level access to internal
    brick components (file system, modules...). It can be used to create motor or sensor
    objects.

    Create an instance with :func:`nxt.locator.find`.

    The :class:`Brick` object implements the context manager interface, so you can use
    it with the ``with`` syntax to close the connection when done with it.
    """

    def __init__(self, sock) -> None:
        self._sock = sock
        self._lock = threading.Lock()

    def play_tone_and_wait(self, frequency_hz: int, duration_ms: int) -> None:
        """Play a tone and wait until finished.

        :param frequency_hz: Tone frequency in Hertz.
        :param duration_ms: Tone duration in milliseconds.
        """
        self.play_tone(frequency_hz, duration_ms)
        time.sleep(duration_ms / 1000.0)

    def close(self) -> None:
        """Disconnect from the NXT brick."""
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def __enter__(self) -> "Brick":
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def open_file(
        self,
        name: str,
        mode: str = "r",
        size: Optional[int] = None,
        *,
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> io.IOBase:
        """Open a file and return a corresponding file-like object.

        :param name: Name of the file to open.
        :param mode: Specification of open mode.
        :param size: For writing, give the final size of the file.
        :param buffering: Buffering control.
        :param encoding: Encoding for text mode.
        :param errors: Encoding error handling for text mode.
        :param newline: Newline handling for text mode.
        :return: A file-like object connected to the file on the NXT brick.
        :raises nxt.error.FileNotFoundError: When file does not exists.
        :raises nxt.error.FileExistsError: When file already exists.
        :raises nxt.error.SystemProtocolError: When no space is available.

        `mode` is a string which specifies how the file should be open. You can combine
        several characters to build the specification:

        =========  =====================================
        Character  Meaning
        =========  =====================================
        'r'        open for reading (default)
        'w'        open for writing (`size` must be given)
        't'        use text mode (default)
        'b'        use binary mode
        =========  =====================================

        When writing a file, the NXT brick needs to know the total size when opening the
        file, so this must be given as parameter.

        Other parameters (`buffering`, `encoding`, `errors` and `newline`) have the same
        meaning as the standard :func:`open` function, they must be given as keyword
        parameters.

        When `encoding` is ``None`` or not given, it defaults to ``ascii`` as this is
        the only encoding understood by the NXT brick.
        """
        rw = None
        tb = None
        for c in mode:
            if c in "rw" and rw is None:
                rw = c
            elif c in "tb" and tb is None:
                tb = c
            else:
                raise ValueError("invalid mode")
        if rw is None:
            raise ValueError("must give read or write mode")
        if tb is None:
            tb = "t"
        if tb == "b":
            if encoding is not None:
                raise ValueError("invalid encoding argument for binary mode")
            if errors is not None:
                raise ValueError("invalid errors argument for binary mode")
            if newline is not None:
                raise ValueError("invalid newline argument for binary mode")
        else:
            if buffering == 0:
                raise ValueError("invalid buffering argument for text mode")
            if encoding is None:
                encoding = "ascii"
        if buffering == -1:
            buffering = self._sock.bsize
        raw: io.RawIOBase
        buf: io.BufferedIOBase
        if rw == "r":
            if size is not None:
                raise ValueError("size given for reading")
            raw = RawFileReader(self, name)
            if buffering == 0:
                return raw
            buf = io.BufferedReader(raw, buffering)
        else:
            if size is None:
                raise ValueError("size not given for writing")
            raw = RawFileWriter(self, name, size)
            if buffering == 0:
                return raw
            buf = io.BufferedWriter(raw, buffering)
        if tb == "t":
            return io.TextIOWrapper(
                cast(IO[bytes], buf), encoding, errors, newline, buffering == 1
            )
        else:
            return buf

    def find_files(self, pattern: str = "*.*") -> Iterator[tuple[str, int]]:
        """Find all files matching a pattern.

        :param pattern: Pattern to match files against.
        :return: An iterator on all matching files, returning file name and file size as
           a tuple.

        Accepted patterns are:

        - ``*.*``: to match anything (default),
        - ``<name>.*``: to match files with any extension,
        - ``*.<extension>``: to match files with given extension,
        - ``<name>.<extension>``: to match using full name.
        """
        try:
            handle, name, size = self.file_find_first(pattern)
        except nxt.error.FileNotFoundError:
            return None
        try:
            yield name, size
            while True:
                try:
                    _, name, size = self.file_find_next(handle)
                except nxt.error.FileNotFoundError:
                    break
                yield name, size
        finally:
            self.file_close(handle)

    def find_modules(self, pattern: str = "*.*") -> Iterator[tuple[str, int, int, int]]:
        """Find all modules matching a pattern.

        :param pattern: Pattern to match modules against, use ``*.*`` (default) to match
           any module.
        :return: An iterator on all matching modules, returning module name, identifier,
           size and IO map size as a tuple.
        """
        try:
            handle, mname, mid, msize, miomap_size = self.module_find_first(pattern)
        except nxt.error.ModuleNotFoundError:
            return None
        try:
            yield mname, mid, msize, miomap_size
            while True:
                try:
                    _, mname, mid, msize, miomap_size = self.module_find_next(handle)
                except nxt.error.ModuleNotFoundError:
                    break
                yield mname, mid, msize, miomap_size
        finally:
            self.module_close(handle)

    def get_motor(self, port: nxt.motor.Port) -> nxt.motor.Motor:
        """Return a motor object connected to one of the brick output port.

        :param port: Output port identifier.
        :return: The motor object.
        """
        return nxt.motor.Motor(self, port)

    def get_sensor(
        self,
        port: nxt.sensor.Port,
        cls: Optional[type[nxt.sensor.Sensor]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> nxt.sensor.Sensor:
        """Return a sensor object connected to one of the brick input port.

        :param port: Input port identifier.
        :param cls: Sensor class, or ``None`` to autodetect.
        :param args: Additional constructor positional arguments when `cls` is given.
        :param kwargs: Additional constructor keyword arguments when `cls` is given.
        :return: A sensor object.
        :raises nxt.sensor.digital.SearchError: When sensor can not be identified.

        When `cls` is not given or ``None``, try to detect the sensor type and return
        the correct sensor object. This only works for digital sensors with
        identification information.

        For autodetection to work, the module containing the sensor class must be
        imported at least once. See modules in :mod:`nxt.sensor`.
        """
        if cls is None:
            if args or kwargs:
                raise ValueError("extra arguments with autodetect")
            base_sensor = nxt.sensor.digital.BaseDigitalSensor(
                self, port, check_compatible=False
            )
            info = base_sensor.get_sensor_info()
            return nxt.sensor.digital.find_class(info)(
                self, port, check_compatible=False
            )
        else:
            return cls(self, port, *args, **kwargs)

    def _cmd(self, tgram: nxt.telegram.Telegram) -> nxt.telegram.Telegram:
        """Send a message to the NXT brick and read reply.

        :param tgram: Message to send.
        :return: Reply message after status has been checked.
        """
        assert tgram.reply_req
        with self._lock:
            self._sock.send(tgram.to_bytes())
            reply_tgram = Telegram(opcode=tgram.opcode, pkt=self._sock.recv())
        reply_tgram.check_status()
        return reply_tgram

    def _cmd_noreply(self, tgram: nxt.telegram.Telegram) -> None:
        """Send a message to the NXT brick with no reply.

        :param tgram: Message to send.
        """
        assert not tgram.reply_req
        with self._lock:
            self._sock.send(tgram.to_bytes())

    def start_program(self, name: str) -> None:
        """Start a program on the brick.

        :param name: Program file name (example: ``"myprogram.rxe"``).
        """
        tgram = Telegram(Opcode.DIRECT_START_PROGRAM)
        tgram.add_filename(name)
        self._cmd(tgram)

    def stop_program(self) -> None:
        """Stop the running program on the brick.

        :raises nxt.error.NoActiveProgramError: When no program is running.
        """
        tgram = Telegram(Opcode.DIRECT_STOP_PROGRAM)
        self._cmd(tgram)

    def play_sound_file(self, loop: bool, name: str) -> None:
        """Play a sound file on the brick.

        :param loop: Loop mode, play continuously.
        :param name: Sound file name.
        """
        tgram = Telegram(Opcode.DIRECT_PLAY_SOUND_FILE, reply_req=False)
        tgram.add_bool(loop)
        tgram.add_filename(name)
        self._cmd_noreply(tgram)

    def play_tone(self, frequency_hz: int, duration_ms: int) -> None:
        """Play a tone on the brick, do not wait until finished.

        :param frequency_hz: Tone frequency in Hertz.
        :param duration_ms: Tone duration in milliseconds.

        This function do not wait until finished, if you want to play several notes, you
        may need :func:`play_tone_and_wait`.
        """
        tgram = Telegram(Opcode.DIRECT_PLAY_TONE, reply_req=False)
        tgram.add_u16(frequency_hz)
        tgram.add_u16(duration_ms)
        self._cmd_noreply(tgram)

    def set_output_state(
        self,
        port: nxt.motor.Port,
        power: int,
        mode: nxt.motor.Mode,
        regulation_mode: nxt.motor.RegulationMode,
        turn_ratio: int,
        run_state: nxt.motor.RunState,
        tacho_limit: int,
    ) -> None:
        """Set output port state on the brick.

        :param port: Output port identifier.
        :param power: Motor speed or power level (-100 to 100).
        :param mode: Motor power mode.
        :param regulation_mode: Motor regulation mode.
        :param turn_ratio: Turn ratio (-100 to 100). Negative value shift power to the
           left motor.
        :param run_state: Motor run state.
        :param tacho_limit: Number of degrees the motor should rotate relative to the
           current position.

        .. warning:: This is a low level function, prefer to use
           :meth:`nxt.motor.Motor`, you can get one from :meth:`get_motor`.
        """
        tgram = Telegram(Opcode.DIRECT_SET_OUT_STATE, reply_req=False)
        tgram.add_u8(port.value)
        tgram.add_s8(power)
        tgram.add_u8(mode.value)
        tgram.add_u8(regulation_mode.value)
        tgram.add_s8(turn_ratio)
        tgram.add_u8(run_state.value)
        tgram.add_u32(tacho_limit)
        self._cmd_noreply(tgram)

    def set_input_mode(
        self,
        port: nxt.sensor.Port,
        sensor_type: nxt.sensor.Type,
        sensor_mode: nxt.sensor.Mode,
    ) -> None:
        """Set input port mode on the brick.

        :param port: Input port identifier.
        :param sensor_type: Sensor type.
        :param sensor_mode: Sensor mode.

        .. warning:: This is a low level function, prefer to use a :mod:`nxt.sensor`
           class.
        """
        tgram = Telegram(Opcode.DIRECT_SET_IN_MODE, reply_req=False)
        tgram.add_u8(port.value)
        tgram.add_u8(sensor_type.value)
        tgram.add_u8(sensor_mode.value)
        self._cmd_noreply(tgram)

    def get_output_state(
        self, port: nxt.motor.Port
    ) -> tuple[
        nxt.motor.Port,
        int,
        nxt.motor.Mode,
        nxt.motor.RegulationMode,
        int,
        nxt.motor.RunState,
        int,
        int,
        int,
        int,
    ]:
        """Get output port state from the brick.

        :param port: Output port identifier.
        :return: A tuple with `port`, `power`, `mode`, `regulation_mode`, `turn_ratio`,
           `run_state`, `tacho_limit`, `tacho_count`, `block_tacho_count`, and
           `rotation_count`.

        Return value details:

        - **port** Output port identifier.
        - **power** Motor speed or power level (-100 to 100).
        - **mode** Motor power mode.
        - **regulation_mode** Motor regulation mode.
        - **turn_ratio** Turn ratio (-100 to 100). Negative value shift power to the
          left motor.
        - **run_state** Motor run state.
        - **tacho_limit** Number of degrees the motor should rotate.
        - **block_tacho_count** Number of degrees the motor rotated relative to the
          "block" start.
        - **rotation_count** Number of degrees the motor rotated relative to the program
          start.

        .. warning:: This is a low level function, prefer to use
           :meth:`nxt.motor.Motor`, you can get one from :meth:`get_motor`.
        """
        tgram = Telegram(Opcode.DIRECT_GET_OUT_STATE)
        tgram.add_u8(port.value)
        tgram = self._cmd(tgram)
        port = nxt.motor.Port(tgram.parse_u8())
        power = tgram.parse_s8()
        mode = nxt.motor.Mode(tgram.parse_u8())
        regulation_mode = nxt.motor.RegulationMode(tgram.parse_u8())
        turn_ratio = tgram.parse_s8()
        run_state = nxt.motor.RunState(tgram.parse_u8())
        tacho_limit = tgram.parse_u32()
        tacho_count = tgram.parse_s32()
        block_tacho_count = tgram.parse_s32()
        rotation_count = tgram.parse_s32()
        return (
            port,
            power,
            mode,
            regulation_mode,
            turn_ratio,
            run_state,
            tacho_limit,
            tacho_count,
            block_tacho_count,
            rotation_count,
        )

    def get_input_values(
        self, port: nxt.sensor.Port
    ) -> tuple[
        nxt.sensor.Port,
        bool,
        bool,
        nxt.sensor.Type,
        nxt.sensor.Mode,
        int,
        int,
        int,
        int,
    ]:
        """Get input port values from the brick.

        :param port: Input port identifier.
        :return: A tuple with `port`, `valid`, `calibrated`, `sensor_type`,
           `sensor_mode`, `raw_value`, `normalized_value`, `scaled_value`, and
           `calibrated_value`. `rotation_count`.

        Return value details:

        - **port** Input port identifier.
        - **valid** ``True`` if the value is valid, else ``False``.
        - **calibrated** Always ``False``, there is no calibration in NXT firmware.
        - **sensor_type** Sensor type.
        - **sensor_mode** Sensor mode.
        - **raw_value** Raw analog to digital converter value.
        - **normalized_value** Normalized value.
        - **scaled_value** Scaled value.
        - **calibrated_value** Always normalized value, there is no calibration in NXT
          firmware.

        .. warning:: This is a low level function, prefer to use a :mod:`nxt.sensor`
           class.
        """
        tgram = Telegram(Opcode.DIRECT_GET_IN_VALS)
        tgram.add_u8(port.value)
        tgram = self._cmd(tgram)
        port = nxt.sensor.Port(tgram.parse_u8())
        valid = tgram.parse_bool()
        calibrated = tgram.parse_bool()
        sensor_type = nxt.sensor.Type(tgram.parse_u8())
        sensor_mode = nxt.sensor.Mode(tgram.parse_u8())
        raw_value = tgram.parse_u16()
        normalized_value = tgram.parse_u16()
        scaled_value = tgram.parse_s16()
        calibrated_value = tgram.parse_s16()
        return (
            port,
            valid,
            calibrated,
            sensor_type,
            sensor_mode,
            raw_value,
            normalized_value,
            scaled_value,
            calibrated_value,
        )

    def reset_input_scaled_value(self, port: nxt.sensor.Port) -> None:
        """Reset scaled value for an input port on the brick.

        :param port: Input port identifier.

        This can be used to reset accumulated value for some sensor modes.

        .. warning:: This is a low level function, prefer to use a :mod:`nxt.sensor`
           class.
        """
        tgram = Telegram(Opcode.DIRECT_RESET_IN_VAL)
        tgram.add_u8(port.value)
        self._cmd(tgram)

    def message_write(self, inbox: int, message: bytes) -> None:
        """Send a message to a brick mailbox.

        :param inbox: Mailbox number (0 to 19).
        :param message: Message to send (58 bytes maximum).
        """
        if len(message) > 58:
            raise ValueError("message too long")
        tgram = Telegram(Opcode.DIRECT_MESSAGE_WRITE)
        tgram.add_u8(inbox)
        tgram.add_u8(len(message) + 1)
        tgram.add_bytes(message)
        tgram.add_u8(0)
        self._cmd(tgram)

    def reset_motor_position(self, port: nxt.motor.Port, relative: bool) -> None:
        """Reset block or program motor position for a brick output port.

        :param port: Output port identifier.
        :param relative: If ``True``, reset block position, if ``False``, reset program
           position.

        .. warning:: This is a low level function, prefer to use
           :meth:`nxt.motor.Motor`, you can get one from :meth:`get_motor`.
        """
        tgram = Telegram(Opcode.DIRECT_RESET_POSITION)
        tgram.add_u8(port.value)
        tgram.add_bool(relative)
        self._cmd(tgram)

    def get_battery_level(self) -> int:
        """Get brick battery voltage.

        :return: Battery voltage in millivolt.
        """
        tgram = Telegram(Opcode.DIRECT_GET_BATT_LVL)
        tgram = self._cmd(tgram)
        millivolts = tgram.parse_u16()
        return millivolts

    def stop_sound_playback(self) -> None:
        """Stop currently running sound file on the brick."""
        tgram = Telegram(Opcode.DIRECT_STOP_SOUND)
        self._cmd(tgram)

    def keep_alive(self) -> int:
        """Reset the brick standby timer.

        :return: Sleep timeout in milliseconds.
        """
        tgram = Telegram(Opcode.DIRECT_KEEP_ALIVE)
        tgram = self._cmd(tgram)
        sleep_timeout = tgram.parse_u32()
        return sleep_timeout

    def ls_get_status(self, port: nxt.sensor.Port) -> int:
        """Get status of last low-speed transaction to a brick input port.

        :param port: Input port identifier.
        :return: Number of bytes to read as a result of the transaction.
        :raises nxt.error.I2CPendingError: When transaction is still in progress.
        :raises nxt.error.DirectProtocolError: When there is an error on the bus.

        .. warning:: This is a low level function, prefer to use a :mod:`nxt.sensor`
           class.
        """
        tgram = Telegram(Opcode.DIRECT_LS_GET_STATUS)
        tgram.add_u8(port.value)
        tgram = self._cmd(tgram)
        size = tgram.parse_u8()
        return size

    def ls_write(self, port: nxt.sensor.Port, tx_data: bytes, rx_bytes: int) -> None:
        """Write data to a brick input port using low speed transaction.

        :param port: Input port identifier.
        :param tx_data: Data to send.
        :param rx_bytes: Number of bytes to receive.

        Function returns immediately. Transaction status can be retrieved using
        :meth:`ls_get_status` and result must be read using :meth:`ls_read`.

        .. warning:: This is a low level function, prefer to use a :mod:`nxt.sensor`
           class.
        """
        tgram = Telegram(Opcode.DIRECT_LS_WRITE)
        tgram.add_u8(port.value)
        tgram.add_u8(len(tx_data))
        tgram.add_u8(rx_bytes)
        tgram.add_bytes(tx_data)
        self._cmd(tgram)

    def ls_read(self, port: nxt.sensor.Port) -> bytes:
        """Read result of low speed transaction.

        :param port: Input port identifier.
        :return: Data received.
        :raises nxt.error.I2CPendingError: When transaction is still in progress.
        :raises nxt.error.DirectProtocolError: When there is an error on the bus.

        The :meth:`ls_write` function must be called to initiate the transaction.

        .. warning:: This is a low level function, prefer to use a :mod:`nxt.sensor`
           class.
        """
        tgram = Telegram(Opcode.DIRECT_LS_READ)
        tgram.add_u8(port.value)
        tgram = self._cmd(tgram)
        size = tgram.parse_u8()
        rx_data = tgram.parse_bytes(size)
        return rx_data

    def get_current_program_name(self) -> str:
        """Return name of program currently running on the brick.

        :return: Program file name
        :raises nxt.error.NoActiveProgramError: When no program is running.
        """
        tgram = Telegram(Opcode.DIRECT_GET_CURR_PROGRAM)
        tgram = self._cmd(tgram)
        name = tgram.parse_filename()
        return name

    def message_read(
        self, remote_inbox: int, local_inbox: int, remove: bool
    ) -> tuple[int, bytes]:
        """Read a message from a brick mailbox.

        :param remote_inbox: Mailbox number (0 to 19).
        :param local_inbox: Local mailbox number, not used by brick.
        :param remove: Whether to remove the message from the mailbox.
        :return: A tuple with the local mailbox number and the read message.
        :raises nxt.error.EmptyMailboxError: When mailbox is empty.
        :raises nxt.error.NoActiveProgramError: When no program is running.
        """
        tgram = Telegram(Opcode.DIRECT_MESSAGE_READ)
        tgram.add_u8(remote_inbox)
        tgram.add_u8(local_inbox)
        tgram.add_bool(remove)
        tgram = self._cmd(tgram)
        local_inbox = tgram.parse_u8()
        size = tgram.parse_u8()
        message = tgram.parse_bytes(size)
        return local_inbox, message

    def file_open_read(self, name: str) -> tuple[int, int]:
        """Open file for reading.

        :param name: File name.
        :return: The file handle and the file size.
        :raises nxt.error.FileNotFoundError: When file does not exists.

        .. warning:: This is a low level function, prefer to use :meth:`open_file`.
        """
        tgram = Telegram(Opcode.SYSTEM_OPENREAD)
        tgram.add_filename(name)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        size = tgram.parse_u32()
        return handle, size

    def file_open_write(self, name: str, size: int) -> int:
        """Open file for writing.

        :param name: File name.
        :param size: Final file size.
        :return: The file handle.
        :raises nxt.error.FileExistsError: When file already exists.
        :raises nxt.error.SystemProtocolError: When no space is available.

        .. warning:: This is a low level function, prefer to use :meth:`open_file`.
        """
        tgram = Telegram(Opcode.SYSTEM_OPENWRITE)
        tgram.add_filename(name)
        tgram.add_u32(size)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        return handle

    def file_read(self, handle: int, size: int) -> tuple[int, bytes]:
        """Read data from open file.

        :param handle: Open file handle.
        :param size: Number of bytes to read.
        :return: The file handle and the read data.

        .. warning:: This is a low level function, prefer to use :meth:`open_file`.
        """
        tgram = Telegram(Opcode.SYSTEM_READ)
        tgram.add_u8(handle)
        tgram.add_u16(size)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        size = tgram.parse_u16()
        data = tgram.parse_bytes(size)
        return handle, data

    def file_write(self, handle: int, data: bytes) -> tuple[int, int]:
        """Write data to open file.

        :param handle: Open file handle.
        :param data: Data to write.
        :return: The file handle and the number of bytes written.

        .. warning:: This is a low level function, prefer to use :meth:`open_file`.
        """
        tgram = Telegram(Opcode.SYSTEM_WRITE)
        tgram.add_u8(handle)
        tgram.add_bytes(data)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        size = tgram.parse_u16()
        return handle, size

    def file_close(self, handle: int) -> int:
        """Close open file.

        :param handle: Open file handle.
        :return: The closed file handle.

        .. warning:: This is a low level function, prefer to use :meth:`open_file`.
        """
        tgram = Telegram(Opcode.SYSTEM_CLOSE)
        tgram.add_u8(handle)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        return handle

    def file_delete(self, name: str) -> str:
        """Delete a file on the brick.

        :param name: File name.
        :return: The deleted file name.
        :raises nxt.error.FileNotFoundError: When file does not exists.
        """
        tgram = Telegram(Opcode.SYSTEM_DELETE)
        tgram.add_filename(name)
        tgram = self._cmd(tgram)
        name = tgram.parse_filename()
        return name

    def file_find_first(self, pattern: str) -> tuple[int, str, int]:
        """Start finding files matching a pattern.

        :param pattern: Pattern to match files against.
        :return: A handle for the search, first file found name and size.
        :raises nxt.error.FileNotFoundError: When no file is found.

        .. warning:: This is a low level function, prefer to use :meth:`find_files`.
        """
        tgram = Telegram(Opcode.SYSTEM_FINDFIRST)
        tgram.add_filename(pattern)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        name = tgram.parse_filename()
        size = tgram.parse_u32()
        return handle, name, size

    def file_find_next(self, handle: int) -> tuple[int, str, int]:
        """Continue finding files.

        :param handle: Handle open with :meth:`file_find_first`.
        :return: The handle, next file found name and size.
        :raises nxt.error.FileNotFoundError: When no more file is found.

        .. warning:: This is a low level function, prefer to use :meth:`find_files`.
        """
        tgram = Telegram(Opcode.SYSTEM_FINDNEXT)
        tgram.add_u8(handle)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        name = tgram.parse_filename()
        size = tgram.parse_u32()
        return handle, name, size

    def get_firmware_version(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Get firmware version information.

        :return: Protocol and firmware versions, as two tuples with major and minor for
           each version.
        """
        tgram = Telegram(Opcode.SYSTEM_VERSIONS)
        tgram = self._cmd(tgram)
        prot_minor = tgram.parse_u8()
        prot_major = tgram.parse_u8()
        prot_version = (prot_major, prot_minor)
        fw_minor = tgram.parse_u8()
        fw_major = tgram.parse_u8()
        fw_version = (fw_major, fw_minor)
        return prot_version, fw_version

    def file_open_write_linear(self, name: str, size: int) -> int:
        """Open file for writing, reserve a linear space.

        :param name: File name.
        :param size: Final file size.
        :return: The file handle.
        :raises nxt.error.FileExistsError: When file already exists.
        :raises nxt.error.SystemProtocolError: When no space is available.

        Linear space is required for programs, but the brick will automatically use
        linear mode with :meth:`file_open_write` when extension is ``.rxe``, ``.sys`` or
        ``.rtm``.

        .. warning:: This is a low level function, prefer to use :meth:`open_file`.
        """
        tgram = Telegram(Opcode.SYSTEM_OPENWRITELINEAR)
        tgram.add_filename(name)
        tgram.add_u32(size)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        return handle

    def file_open_write_data(self, name: str, size: int) -> int:
        """Open file for writing, using data mode.

        :param name: File name.
        :param size: Maximum file size.
        :return: The file handle.
        :raises nxt.error.FileExistsError: When file already exists.
        :raises nxt.error.SystemProtocolError: When no space is available.

        A data file can be written in small chunks, and can grow later. It can be used
        for data logging.

        .. warning:: This is a low level function, however, there is no support yet for
           data files in :meth:`open_file`.
        """
        tgram = Telegram(Opcode.SYSTEM_OPENWRITEDATA)
        tgram.add_filename(name)
        tgram.add_u32(size)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        return handle

    def file_open_append_data(self, name: str) -> tuple[int, int]:
        """Open file for appending, using data mode.

        :param name: File name.
        :return: The file handle and available size
        :raises nxt.error.FileNotFoundError: When file does not exists.
        :raises nxt.error.SystemProtocolError: When file is full or file is not a data
           file.

        The file must be a data file. The available size is the size which has not been
        written to last time the file was open.

        .. warning:: This is a low level function, however, there is no support yet for
           data files in :meth:`open_file`.
        """
        tgram = Telegram(Opcode.SYSTEM_OPENAPPENDDATA)
        tgram.add_filename(name)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        available_size = tgram.parse_u32()
        return handle, available_size

    def module_find_first(self, pattern: str) -> tuple[int, str, int, int, int]:
        """Start finding modules matching a pattern.

        :param pattern: Pattern to match modules against.
        :return: A handle for the search, first module found name, identifier, size and
           IO map size.
        :raises nxt.error.ModuleNotFoundError: When no module is found.

        .. warning:: This is a low level function, prefer to use :meth:`find_modules`.
        """
        tgram = Telegram(Opcode.SYSTEM_FINDFIRSTMODULE)
        tgram.add_filename(pattern)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        name = tgram.parse_filename()
        mod_id = tgram.parse_u32()
        mod_size = tgram.parse_u32()
        mod_iomap_size = tgram.parse_u16()
        return handle, name, mod_id, mod_size, mod_iomap_size

    def module_find_next(self, handle: int) -> tuple[int, str, int, int, int]:
        """Continue finding modules.

        :param handle: Handle open with :meth:`module_find_first`.
        :return: The handle, next module found name, identifier, size and IO map size.
        :raises nxt.error.ModuleNotFoundError: When no more module is found.

        .. warning:: This is a low level function, prefer to use :meth:`find_modules`.
        """
        tgram = Telegram(Opcode.SYSTEM_FINDNEXTMODULE)
        tgram.add_u8(handle)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        name = tgram.parse_filename()
        mod_id = tgram.parse_u32()
        mod_size = tgram.parse_u32()
        mod_iomap_size = tgram.parse_u16()
        return handle, name, mod_id, mod_size, mod_iomap_size

    def module_close(self, handle: int) -> int:
        """Close module search.

        :param handle: Open module handle.
        :return: The closed module handle.

        .. warning:: This is a low level function, prefer to use :meth:`find_modules`.
        """
        tgram = Telegram(Opcode.SYSTEM_CLOSEMODHANDLE)
        tgram.add_u8(handle)
        tgram = self._cmd(tgram)
        handle = tgram.parse_u8()
        return handle

    def read_io_map(self, mod_id: int, offset: int, size: int) -> tuple[int, bytes]:
        """Read module IO map on the brick.

        :param mod_id: Module identifier.
        :param offset: Offset in IO map.
        :param size: Number of bytes to read.
        :return: Module identifier and read data.

        Module identifier can be found using :meth:`find_modules`. You need to know the
        structure of the module IO map. You can find it by reading the firmware source
        code.
        """
        tgram = Telegram(Opcode.SYSTEM_IOMAPREAD)
        tgram.add_u32(mod_id)
        tgram.add_u16(offset)
        tgram.add_u16(size)
        tgram = self._cmd(tgram)
        mod_id = tgram.parse_u32()
        size = tgram.parse_u16()
        data = tgram.parse_bytes(size)
        return mod_id, data

    def write_io_map(self, mod_id: int, offset: int, data: bytes) -> tuple[int, int]:
        """Write module IO map on the brick.

        :param mod_id: Module identifier.
        :param offset: Offset in IO map.
        :param data: Data to write.
        :return: Module identifier and written size.

        Module identifier can be found using :meth:`find_modules`. You need to know the
        structure of the module IO map. You can find it by reading the firmware source
        code.
        """
        tgram = Telegram(Opcode.SYSTEM_IOMAPWRITE)
        tgram.add_u32(mod_id)
        tgram.add_u16(offset)
        tgram.add_u16(len(data))
        tgram.add_bytes(data)
        tgram = self._cmd(tgram)
        mod_id = tgram.parse_u32()
        size = tgram.parse_u16()
        return mod_id, size

    def boot(self, *, sure: bool = False) -> bytes:
        """Erase NXT brick firmware and go to SAM-BA boot mode.

        :param sure: Set to ``True`` if you are really sure. Must be a keyword
           parameter.
        :return: Brick response, should be ``"Yes\0"``.

        This only works on USB connection.

        .. danger:: This **erases the firmware** of the brick, you need to send a new
           firmware to use it. Sending a firmware is not supported by NXT-Python. You
           can use the original LEGO software or `libnxt`_ for example. Be sure to know
           what you are doing.

        .. _libnxt: https://git.ni.fr.eu.org/libnxt.git/
        """
        if not sure:
            raise ValueError("this is dangerous, please read documentation")
        tgram = Telegram(Opcode.SYSTEM_BOOTCMD)
        tgram.add_bytes(b"Let's dance: SAMBA\0")
        tgram = self._cmd(tgram)
        resp = tgram.parse_bytes()
        return resp

    def set_brick_name(self, name: str) -> None:
        """Set brick name.

        :param name: New brick name.
        """
        tgram = Telegram(Opcode.SYSTEM_SETBRICKNAME)
        tgram.add_string(15, name)
        self._cmd(tgram)

    def get_device_info(self) -> tuple[str, str, tuple[int, int, int, int], int]:
        """Get brick information.

        :return: The brick name, Bluetooth address, Bluetooth signal strengths and free
           user flash.

        Bluetooth address uses this notation: ``00:16:53:xx:xx:xx``, where `xx` is the
        brick unique address part (`00:16:53` is the LEGO OUI used for the NXT bricks).
        """
        tgram = Telegram(Opcode.SYSTEM_DEVICEINFO)
        tgram = self._cmd(tgram)
        name = tgram.parse_string(15)
        a0 = tgram.parse_u8()
        a1 = tgram.parse_u8()
        a2 = tgram.parse_u8()
        a3 = tgram.parse_u8()
        a4 = tgram.parse_u8()
        a5 = tgram.parse_u8()
        # a6 is not used, should be zero.
        tgram.parse_u8()
        address = f"{a0:02X}:{a1:02X}:{a2:02X}:{a3:02X}:{a4:02X}:{a5:02X}"
        signal_strengths = (
            tgram.parse_u8(),
            tgram.parse_u8(),
            tgram.parse_u8(),
            tgram.parse_u8(),
        )
        user_flash = tgram.parse_u32()
        return name, address, signal_strengths, user_flash

    def delete_user_flash(self) -> None:
        """Erase the brick user flash."""
        tgram = Telegram(Opcode.SYSTEM_DELETEUSERFLASH)
        self._cmd(tgram)

    def poll_command_length(self, buf_num: int) -> tuple[int, int]:
        """Get number of bytes available in brick poll buffer.

        :param buf_num: Buffer number, 0 for USB, 1 for high speed.
        :return: Buffer number and number of available bytes.
        """
        tgram = Telegram(Opcode.SYSTEM_POLLCMDLEN)
        tgram.add_u8(buf_num)
        tgram = self._cmd(tgram)
        buf_num = tgram.parse_u8()
        size = tgram.parse_u8()
        return buf_num, size

    def poll_command(self, buf_num: int, size: int) -> tuple[int, bytes]:
        """Get bytes from brick poll buffer.

        :param buf_num: Buffer number, 0 for USB, 1 for high speed.
        :param size: Number of bytes to read.
        :return: Buffer number and read bytes.
        """
        tgram = Telegram(Opcode.SYSTEM_POLLCMD)
        tgram.add_u8(buf_num)
        tgram.add_u8(size)
        tgram = self._cmd(tgram)
        buf_num = tgram.parse_u8()
        size = tgram.parse_u8()
        command = tgram.parse_bytes(size)
        return buf_num, command

    def bluetooth_factory_reset(self) -> None:
        """Reset brick Bluetooth to factory settings.

        This only works on USB connection.
        """
        tgram = Telegram(Opcode.SYSTEM_BTFACTORYRESET)
        self._cmd(tgram)
