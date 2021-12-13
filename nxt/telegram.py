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

import enum
from io import BytesIO
from struct import pack, unpack

import nxt.error


class Opcode(enum.Enum):
    """Command codes."""

    DIRECT_START_PROGRAM = 0x00
    DIRECT_STOP_PROGRAM = 0x01
    DIRECT_PLAY_SOUND_FILE = 0x02
    DIRECT_PLAY_TONE = 0x03
    DIRECT_SET_OUT_STATE = 0x04
    DIRECT_SET_IN_MODE = 0x05
    DIRECT_GET_OUT_STATE = 0x06
    DIRECT_GET_IN_VALS = 0x07
    DIRECT_RESET_IN_VAL = 0x08
    DIRECT_MESSAGE_WRITE = 0x09
    DIRECT_RESET_POSITION = 0x0A
    DIRECT_GET_BATT_LVL = 0x0B
    DIRECT_STOP_SOUND = 0x0C
    DIRECT_KEEP_ALIVE = 0x0D
    DIRECT_LS_GET_STATUS = 0x0E
    DIRECT_LS_WRITE = 0x0F
    DIRECT_LS_READ = 0x10
    DIRECT_GET_CURR_PROGRAM = 0x11
    DIRECT_GET_BUTTON_STATE = 0x12
    DIRECT_MESSAGE_READ = 0x13
    DIRECT_DATALOG_READ = 0x19
    DIRECT_DATALOG_SET_TIMES = 0x1A
    DIRECT_BT_GET_CONTACT_COUNT = 0x1B
    DIRECT_BT_GET_CONTACT_NAME = 0x1C
    DIRECT_BT_GET_CONN_COUNT = 0x1D
    DIRECT_BT_GET_CONN_NAME = 0x1E
    DIRECT_SET_PROPERTY = 0x1F
    DIRECT_GET_PROPERTY = 0x20
    DIRECT_UPDATE_RESET_COUNT = 0x21
    SYSTEM_OPENREAD = 0x80
    SYSTEM_OPENWRITE = 0x81
    SYSTEM_READ = 0x82
    SYSTEM_WRITE = 0x83
    SYSTEM_CLOSE = 0x84
    SYSTEM_DELETE = 0x85
    SYSTEM_FINDFIRST = 0x86
    SYSTEM_FINDNEXT = 0x87
    SYSTEM_VERSIONS = 0x88
    SYSTEM_OPENWRITELINEAR = 0x89
    SYSTEM_OPENREADLINEAR = 0x8A
    SYSTEM_OPENWRITEDATA = 0x8B
    SYSTEM_OPENAPPENDDATA = 0x8C
    SYSTEM_CROPDATAFILE = 0x8D
    SYSTEM_FINDFIRSTMODULE = 0x90
    SYSTEM_FINDNEXTMODULE = 0x91
    SYSTEM_CLOSEMODHANDLE = 0x92
    SYSTEM_IOMAPREAD = 0x94
    SYSTEM_IOMAPWRITE = 0x95
    SYSTEM_BOOTCMD = 0x97
    SYSTEM_SETBRICKNAME = 0x98
    SYSTEM_BTGETADR = 0x9A
    SYSTEM_DEVICEINFO = 0x9B
    SYSTEM_DELETEUSERFLASH = 0xA0
    SYSTEM_POLLCMDLEN = 0xA1
    SYSTEM_POLLCMD = 0xA2
    SYSTEM_RENAMEFILE = 0xA3
    SYSTEM_BTFACTORYRESET = 0xA4

    def is_system(self):
        return (self.value & 0x80) != 0


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

    TYPE_DIRECT = 0x00
    TYPE_SYSTEM = 0x01
    TYPE_REPLY = 0x02
    TYPE_REPLY_NOT_REQUIRED = 0x80

    def __init__(self, opcode, reply_req=True, pkt=None):
        if pkt:
            self.pkt = BytesIO(pkt)
            pkt_type = self.parse_u8()
            if pkt_type != self.TYPE_REPLY:
                raise nxt.error.ProtocolError("not a reply")
            pkt_opcode = self.parse_u8()
            if pkt_opcode != opcode.value:
                raise nxt.error.ProtocolError(f"invalid reply opcode {pkt_opcode:#02x}")
            self.opcode = opcode
            self.reply_req = False
        else:
            self.pkt = BytesIO()
            if opcode.is_system():
                typ = self.TYPE_SYSTEM
            else:
                typ = self.TYPE_DIRECT
            if not reply_req:
                typ |= self.TYPE_REPLY_NOT_REQUIRED
            self.opcode = opcode
            self.reply_req = reply_req
            self.add_u8(typ)
            self.add_u8(opcode.value)

    def bytes(self):
        return self.pkt.getvalue()

    def add_bytes(self, b):
        self.pkt.write(b)

    def add_string(self, size, v):
        b = v.encode("ascii")
        if len(b) > size - 1:
            raise ValueError("string too long")
        self.pkt.write(pack("%ds" % size, b))

    def add_filename(self, fname):
        self.add_string(20, fname)

    def add_bool(self, v):
        self.pkt.write(pack("<?", v))

    def add_s8(self, v):
        self.pkt.write(pack("<b", v))

    def add_u8(self, v):
        self.pkt.write(pack("<B", v))

    def add_u16(self, v):
        self.pkt.write(pack("<H", v))

    def add_u32(self, v):
        self.pkt.write(pack("<I", v))

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

    def parse_bool(self):
        return unpack("<?", self.pkt.read(1))[0]

    def parse_s8(self):
        return unpack("<b", self.pkt.read(1))[0]

    def parse_u8(self):
        return unpack("<B", self.pkt.read(1))[0]

    def parse_s16(self):
        return unpack("<h", self.pkt.read(2))[0]

    def parse_u16(self):
        return unpack("<H", self.pkt.read(2))[0]

    def parse_s32(self):
        return unpack("<i", self.pkt.read(4))[0]

    def parse_u32(self):
        return unpack("<I", self.pkt.read(4))[0]

    def check_status(self):
        status = self.parse_u8()
        if status:
            ex = CODES.get(status)
            if ex:
                raise ex
            else:
                raise nxt.error.ProtocolError(f"unknown status code: {status:#02x}")
