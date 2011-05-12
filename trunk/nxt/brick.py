# nxt.brick module -- Classes to represent LEGO Mindstorms NXT bricks
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, rhn
# Copyright (C) 2010  rhn, Marcus Wanner, zonedabone
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

from time import sleep
from threading import Lock
from nxt.error import FileNotFound, ModuleNotFound
from nxt.telegram import OPCODES, Telegram
from nxt.sensor import get_sensor
from nxt.motcont import MotCont

def _make_poller(opcode, poll_func, parse_func):
    def poll(self, *args, **kwargs):
        ogram = poll_func(opcode, *args, **kwargs)
        with self.lock:
            self.sock.send(str(ogram))
            if ogram.reply:
                igram = Telegram(opcode=opcode, pkt=self.sock.recv())
        if ogram.reply:
            return parse_func(igram)
        else:
            return None
    return poll

class _Meta(type):
    'Metaclass which adds one method for each telegram opcode'

    def __init__(cls, name, bases, dict):
        super(_Meta, cls).__init__(name, bases, dict)
        for opcode in OPCODES:
            poll_func, parse_func = OPCODES[opcode][0:2]
            m = _make_poller(opcode, poll_func, parse_func)
            try:
                m.__doc__ = OPCODES[opcode][2]
            except:
                pass
            setattr(cls, poll_func.__name__, m)


class FileFinder(object):
    'A generator to find files on a NXT brick.'

    def __init__(self, brick, pattern):
        self.brick = brick
        self.pattern = pattern
        self.handle = None

    def _close(self):
        if self.handle is not None:
            self.brick.close(self.handle)
            self.handle = None

    def __del__(self):
        self._close()

    def __iter__(self):
        results = []
        self.handle, fname, size = self.brick.find_first(self.pattern)
        results.append((fname, size))
        while True:
            try:
                handle, fname, size = self.brick.find_next(self.handle)
                results.append((fname, size))
            except FileNotFound:
                self._close()
                break
        for result in results:
            yield result


def File(brick, name, mode='r', size=None):
    """Opens a file for reading/writing. Mode is 'r' or 'w'. If mode is 'w',
    size must be provided.
    """
    if mode == 'w':
        if size is not None:
            return FileWriter(brick, name, size)
        else:
            return ValueError('Size not specified')
    elif mode == 'r':
        return FileReader(brick, name)
    else:
        return ValueError('Mode ' + str(mode) + ' not supported')


class FileReader(object):
    """Context manager to read a file on a NXT brick. Do use the iterator or
    the read() method, but not both at the same time!
    The iterator returns strings of an arbitrary (short) length.
    """

    def __init__(self, brick, fname):
        self.brick = brick
        self.handle, self.size = brick.open_read(fname)

    def read(self, bytes=None):
        if bytes is not None:
            remaining = bytes
        else:
            remaining = self.size
        bsize = self.brick.sock.bsize
        data = []
        while remaining > 0:
            handle, bsize, buffer_ = self.brick.read(self.handle,
                min(bsize, remaining))
            remaining -= len(buffer_)
            data.append(buffer_)
        return ''.join(data)

    def close(self):
        if self.handle is not None:
            self.brick.close(self.handle)
            self.handle = None

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, etp, value, tb):
        self.close()

    def __iter__(self):
        rem = self.size
        bsize = self.brick.sock.bsize
        while rem > 0:
            handle, bsize, data = self.brick.read(self.handle,
                min(bsize, rem))
            yield data
            rem -= len(data)


class FileWriter(object):
    "Object to write to a file on a NXT brick"

    def __init__(self, brick, fname, size):
        self.brick = brick
        self.handle = self.brick.open_write(fname, size)
        self._position = 0
        self.size = size

    def __del__(self):
        self.close()

    def close(self):
        if self.handle is not None:
            self.brick.close(self.handle)
            self.handle = None

    def tell(self):
        return self._position

    def write(self, data):
        remaining = len(data)
        if remaining > self.size - self._position:
            raise ValueError('Data will not fit into remaining space')
        bsize = self.brick.sock.bsize
        data_position = 0

        while remaining > 0:
            batch_size = min(bsize, remaining)
            next_data_position = data_position + batch_size
            buffer_ = data[data_position:next_data_position]

            handle, size = self.brick.write(self.handle, buffer_)

            self._position += batch_size
            data_position = next_data_position
            remaining -= batch_size


class ModuleFinder(object):
    'Iterator to lookup modules on a NXT brick'

    def __init__(self, brick, pattern):
        self.brick = brick
        self.pattern = pattern
        self.handle = None

    def _close(self):
        if self.handle:
            self.brick.close(self.handle)
            self.handle = None

    def __del__(self):
        self._close()

    def __iter__(self):
        self.handle, mname, mid, msize, miomap_size = \
            self.brick.request_first_module(self.pattern)
        yield (mname, mid, msize, miomap_size)
        while True:
            try:
                handle, mname, mid, msize, miomap_size = \
                    self.brick.request_next_module(
                    self.handle)
                yield (mname, mid, msize, miomap_size)
            except ModuleNotFound:
                self._close()
                break


class Brick(object): #TODO: this begs to have explicit methods
    'Main object for NXT Control'

    __metaclass__ = _Meta

    def __init__(self, sock):
        self.sock = sock
        self.lock = Lock()
        self.mc = MotCont(self)

    def play_tone_and_wait(self, frequency, duration):
        self.play_tone(frequency, duration)
        sleep(duration / 1000.0)

    def __del__(self):
        self.sock.close()

    find_files = FileFinder
    find_modules = ModuleFinder
    open_file = File
    get_sensor = get_sensor
