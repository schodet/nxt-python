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
import threading
import time

from nxt.error import FileNotFound, ModuleNotFound
from nxt.motcont import MotCont
from nxt.sensor import get_sensor
from nxt.telegram import OPCODES, Telegram


def _make_poller(opcode, poll_func, parse_func):
    def poll(self, *args, **kwargs):
        ogram = poll_func(opcode, *args, **kwargs)
        with self.lock:
            self.sock.send(ogram.bytes())
            if ogram.reply:
                igram = Telegram(opcode=opcode, pkt=self.sock.recv())
        if ogram.reply:
            return parse_func(igram)
        else:
            return None

    return poll


class _Meta(type):
    """Metaclass which adds one method for each telegram opcode"""

    def __init__(cls, name, bases, dict):
        super(_Meta, cls).__init__(name, bases, dict)
        for opcode in OPCODES:
            poll_func, parse_func = OPCODES[opcode][0:2]
            m = _make_poller(opcode, poll_func, parse_func)
            try:
                m.__doc__ = OPCODES[opcode][2]
            except IndexError:
                pass
            setattr(cls, poll_func.__name__, m)


class RawFileReader(io.RawIOBase):
    """Implement RawIOBase for reading a file on the NXT brick."""

    def __init__(self, brick, name):
        self._brick = brick
        self._handle, self._remaining = brick.open_read(name)

    def close(self):
        if not self.closed:
            super().close()
            self._brick.close(self._handle)

    def readable(self):
        return True

    def readinto(self, b):
        rsize = min(self._brick.sock.bsize, self._remaining, len(b))
        if rsize == 0:
            return 0
        _, data = self._brick.read(self._handle, rsize)
        size = len(data)
        self._remaining -= size
        b[0:size] = data
        return size


class RawFileWriter(io.RawIOBase):
    """Implement RawIOBase for writing a file on the NXT brick."""

    def __init__(self, brick, name, size):
        self._brick = brick
        self._handle = brick.open_write(name, size)
        self._remaining = size

    def close(self):
        if not self.closed:
            super().close()
            self._brick.close(self._handle)

    def writable(self):
        return True

    def write(self, b):
        if self.closed:
            raise ValueError("write to closed file")
        if self._remaining == 0:
            raise ValueError("write to a full file")
        wsize = min(self._brick.sock.bsize, self._remaining, len(b))
        _, size = self._brick.write(self._handle, bytes(b[:wsize]))
        self._remaining -= size
        return size


class Brick(object, metaclass=_Meta):  # TODO: this begs to have explicit methods
    """Main object for NXT Control"""

    def __init__(self, sock):
        self.sock = sock
        self.lock = threading.Lock()
        self.mc = MotCont(self)

    def play_tone_and_wait(self, frequency, duration):
        self.play_tone(frequency, duration)
        time.sleep(duration / 1000.0)

    def __del__(self):
        self.sock.close()

    def open_file(
        self,
        name,
        mode="r",
        size=None,
        *,
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None
    ):
        """Open a file and return a corresponding file-like object.

        :param str name: Name of the file to open.
        :param str mode: Specification of open mode.
        :param int size: For writing, give the final size of the file.
        :param int buffering: Buffering control.
        :param encoding: Encoding for text mode.
        :type encoding: str or None
        :param errors: Encoding error handling for text mode.
        :type errors: str or None
        :param newline: Newline handling for text mode.
        :type newline: str or None
        :return: A file-like object connected to the file on the NXT brick.
        :rtype: file-like

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

        When `encoding` is None or not given, it defaults to ``ascii`` as this is the
        only encoding understood by the NXT brick.
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
            buffering = self.sock.bsize
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
            return io.TextIOWrapper(buf, encoding, errors, newline, buffering == 1)
        else:
            return buf

    def find_files(self, pattern="*.*"):
        """Find all files matching a pattern.

        :param str pattern: Pattern to match files against.
        :return: An iterator on all matching files, returning file name and
            file size as a tuple.
        :rtype: Iterator[str, int]

        Accepted patterns are:

        - ``*.*``: to match anything (default),
        - ``<name>.*``: to match files with any extension,
        - ``*.<extension>``: to match files with given extension,
        - ``<name>.<extension>``: to match using full name.
        """
        try:
            handle, name, size = self.find_first(pattern)
        except FileNotFound:
            return None
        try:
            yield name, size
            while True:
                try:
                    _, name, size = self.find_next(handle)
                except FileNotFound:
                    break
                yield name, size
        finally:
            self.close(handle)

    def find_modules(self, pattern="*.*"):
        """Find all modules matching a pattern.

        :param str pattern: Pattern to match modules against, use ``*.*``
            (default) to match any module.
        :return: An iterator on all matching modules, returning module name,
            identifier, size and IO map size as a tuple.
        :rtype: Iterator[str, int, int, int]
        """
        try:
            handle, mname, mid, msize, miomap_size = self.request_first_module(pattern)
        except ModuleNotFound:
            return None
        try:
            yield mname, mid, msize, miomap_size
            while True:
                try:
                    _, mname, mid, msize, miomap_size = self.request_next_module(handle)
                except ModuleNotFound:
                    break
                yield mname, mid, msize, miomap_size
        finally:
            self.close_module_handle(handle)

    get_sensor = get_sensor
