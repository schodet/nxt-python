# nxt.telegram module -- LEGO Mindstorms NXT telegram formatting and parsing
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
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

'Used by nxt.system for sending telegrams to the NXT'

from io import BytesIO
from struct import pack, unpack
import nxt.error

class InvalidReplyError(Exception):
    pass

class InvalidOpcodeError(Exception):
    pass

class Telegram(object):

    TYPE = 0    # type byte offset
    CODE = 1    # code byte offset
    DATA = 2    # data byte offset

    TYPE_NOT_DIRECT = 0x01          # system vs. direct type
    TYPE_REPLY = 0x02               # reply type (from NXT brick)
    TYPE_REPLY_NOT_REQUIRED = 0x80  # reply not required flag

    def __init__(self, direct=False, opcode=0, reply_req=True, pkt=None):
        self.reply = True
        if pkt:
            self.pkt = BytesIO(pkt)
            self.typ = self.parse_u8()
            self.opcode = self.parse_u8()
            if not self.is_reply():
                raise InvalidReplyError
            if self.opcode != opcode:
                raise InvalidOpcodeError(self.opcode)
        else:
            self.pkt = BytesIO()
            typ = 0
            if not direct:
                typ |= Telegram.TYPE_NOT_DIRECT
            if not reply_req:
                typ |= Telegram.TYPE_REPLY_NOT_REQUIRED
                self.reply = False
            self.add_u8(typ)
            self.add_u8(opcode)

    def bytes(self):
        return self.pkt.getvalue()

    def is_reply(self):
        return self.typ == Telegram.TYPE_REPLY

    def add_bytes(self, b):
        self.pkt.write(b)

    def add_string(self, size, v):
        b = v.encode("ascii")
        if len(b) > size - 1:
            raise ValueError("String too long")
        self.pkt.write(pack("%ds" % size, b))

    def add_filename(self, fname):
        self.add_string(20, fname)

    def add_s8(self, v):
        self.pkt.write(pack('<b', v))

    def add_u8(self, v):
        self.pkt.write(pack('<B', v))

    def add_u16(self, v):
        self.pkt.write(pack('<H', v))

    def add_u32(self, v):
        self.pkt.write(pack('<I', v))

    def parse_bytes(self, size=-1):
        b = self.pkt.read()
        if size != -1:
            b = b[:size]
        return b

    def parse_string(self, size=-1):
        b = self.pkt.read(size).rstrip(b"\0")
        return b.decode("ascii")

    def parse_filename(self):
        return self.parse_string(20)

    def parse_s8(self):
        return unpack('<b', self.pkt.read(1))[0]

    def parse_u8(self):
        return unpack('<B', self.pkt.read(1))[0]

    def parse_s16(self):
        return unpack('<h', self.pkt.read(2))[0]

    def parse_u16(self):
        return unpack('<H', self.pkt.read(2))[0]

    def parse_s32(self):
        return unpack('<i', self.pkt.read(4))[0]

    def parse_u32(self):
        return unpack('<I', self.pkt.read(4))[0]

    def check_status(self):
        nxt.error.check_status(self.parse_u8())

import nxt.direct
import nxt.system

OPCODES = dict(nxt.system.OPCODES)
OPCODES.update(nxt.direct.OPCODES)
