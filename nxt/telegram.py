# nxt.telegram module -- NXT brick telegram formatting and parsing
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
from io import BytesIO
from struct import pack, unpack

import nxt.error

CODES = {
    0x00: None,
    0x20: nxt.error.I2CPendingError("pending communication transaction in progress"),
    0x40: nxt.error.DirectProtocolError("specified mailbox queue is empty"),
    0x81: nxt.error.SystemProtocolError("no more handles"),
    0x82: nxt.error.SystemProtocolError("no space"),
    0x83: nxt.error.SystemProtocolError("no more files"),
    0x84: nxt.error.SystemProtocolError("end of file expected"),
    0x85: nxt.error.SystemProtocolError("end of file"),
    0x86: nxt.error.SystemProtocolError("not a linear file"),
    0x87: nxt.error.FileNotFoundError("file not found"),
    0x88: nxt.error.SystemProtocolError("handle already closed"),
    0x89: nxt.error.SystemProtocolError("no linear space"),
    0x8A: nxt.error.SystemProtocolError("undefined error"),
    0x8B: nxt.error.SystemProtocolError("file is busy"),
    0x8C: nxt.error.SystemProtocolError("no write buffers"),
    0x8D: nxt.error.SystemProtocolError("append not possible"),
    0x8E: nxt.error.SystemProtocolError("file is full"),
    0x8F: nxt.error.FileExistsError("file exists"),
    0x90: nxt.error.ModuleNotFoundError("module not found"),
    0x91: nxt.error.SystemProtocolError("out of bounds"),
    0x92: nxt.error.SystemProtocolError("illegal file name"),
    0x93: nxt.error.SystemProtocolError("illegal handle"),
    0xBD: nxt.error.DirectProtocolError(
        "request failed (i.e. specified file not found)"
    ),
    0xBE: nxt.error.DirectProtocolError("unknown command opcode"),
    0xBF: nxt.error.DirectProtocolError("insane packet"),
    0xC0: nxt.error.DirectProtocolError("data contains out-of-range values"),
    0xDD: nxt.error.DirectProtocolError("communication bus error"),
    0xDE: nxt.error.DirectProtocolError("no free memory in communication buffer"),
    0xDF: nxt.error.DirectProtocolError("specified channel/connection is not valid"),
    0xE0: nxt.error.I2CError("specified channel/connection not configured or busy"),
    0xEC: nxt.error.DirectProtocolError("no active program"),
    0xED: nxt.error.DirectProtocolError("illegal size specified"),
    0xEE: nxt.error.DirectProtocolError("illegal mailbox queue ID specified"),
    0xEF: nxt.error.DirectProtocolError(
        "attempted to access invalid field of a structure"
    ),
    0xF0: nxt.error.DirectProtocolError("bad input or output specified"),
    0xFB: nxt.error.DirectProtocolError("insufficient memory available"),
    0xFF: nxt.error.DirectProtocolError("bad arguments"),
}


class Telegram:

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
                raise nxt.error.ProtocolError("not a reply reply")
            if self.opcode != opcode:
                raise nxt.error.ProtocolError(
                    f"invalid reply opcode {self.opcode:#02x}"
                )
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
            raise ValueError("string too long")
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
        status = self.parse_u8()
        if status:
            ex = CODES.get(status)
            if ex:
                raise ex
            else:
                raise nxt.error.ProtocolError(f"unknown status code: {status:#02x}")

import nxt.direct
import nxt.system

OPCODES = dict(nxt.system.OPCODES)
OPCODES.update(nxt.direct.OPCODES)
