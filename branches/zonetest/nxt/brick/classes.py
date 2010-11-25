# nxt.classes module -- classes for advanced control of nxt
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

from nxt.constants import *
from struct import pack,unpack

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

def parse_in(cmdtype,cmd,*args):
    output=[cmdtype,cmd]
    packtypes = (S_CHAR,U_CHAR,S_SHT,U_SHT,S_INT,U_INT)
    for item in args:
        if item[0] in packtypes:
            output.append(pack(item[0],item[1]))
        elif item[0] == F_BYTE:
            output.append(NULL*item[1])
        elif item[0] == RAW:
            output.append(item[1])
    return ''.join(output)

def parse_out(data,*args):
    packtypes={S_CHAR:1,U_CHAR:1,S_SHT:2,U_SHT:2,S_INT:4,U_INT:4}
    output=[]
    index = 3
    for item in args:
        if item in packtypes.keys():
            output.append(unpack(item,data[index:index+packtypes[item]])[0])
            index += packtypes[item]
        elif type(item) == type(()) and len(item) == 2:
            if item[0] == F_BYTE:
                index += item[1]
            elif item[0] == RAW:
                output.append(data[index:index+item[1]])
                index += item[1]
    return tuple(output)