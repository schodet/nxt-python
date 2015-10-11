# nxt.error module -- LEGO Mindstorms NXT error handling
# Copyright (C) 2006, 2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
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

'Declarations for the errors'

class ProtocolError(Exception):
    pass

class SysProtError(ProtocolError):
    pass

class FileExistsError(SysProtError):
    pass

class FileNotFound(SysProtError):
    pass

class ModuleNotFound(SysProtError):
    pass

class DirProtError(ProtocolError):
    pass

class I2CError(DirProtError):
    pass

class I2CPendingError(I2CError):
    pass

CODES = {
    0x00: None,
    0x20: I2CPendingError('Pending communication transaction in progress'),
    0x40: DirProtError('Specified mailbox queue is empty'),
    0x81: SysProtError('No more handles'),
    0x82: SysProtError('No space'),
    0x83: SysProtError('No more files'),
    0x84: SysProtError('End of file expected'),
    0x85: SysProtError('End of file'),
    0x86: SysProtError('Not a linear file'),
    0x87: FileNotFound('File not found'),
    0x88: SysProtError('Handle already closed'),
    0x89: SysProtError('No linear space'),
    0x8A: SysProtError('Undefined error'),
    0x8B: SysProtError('File is busy'),
    0x8C: SysProtError('No write buffers'),
    0x8D: SysProtError('Append not possible'),
    0x8E: SysProtError('File is full'),
    0x8F: FileExistsError('File exists'),
    0x90: ModuleNotFound('Module not found'),
    0x91: SysProtError('Out of bounds'),
    0x92: SysProtError('Illegal file name'),
    0x93: SysProtError('Illegal handle'),
    0xBD: DirProtError('Request failed (i.e. specified file not found)'),
    0xBE: DirProtError('Unknown command opcode'),
    0xBF: DirProtError('Insane packet'),
    0xC0: DirProtError('Data contains out-of-range values'),
    0xDD: DirProtError('Communication bus error'),
    0xDE: DirProtError('No free memory in communication buffer'),
    0xDF: DirProtError('Specified channel/connection is not valid'),
    0xE0: I2CError('Specified channel/connection not configured or busy'),
    0xEC: DirProtError('No active program'),
    0xED: DirProtError('Illegal size specified'),
    0xEE: DirProtError('Illegal mailbox queue ID specified'),
    0xEF: DirProtError('Attempted to access invalid field of a structure'),
    0xF0: DirProtError('Bad input or output specified'),
    0xFB: DirProtError('Insufficient memory available'),
    0xFF: DirProtError('Bad arguments'),
}

def check_status(status):
    if status:
        ex = CODES.get(status)
        if ex:
            raise ex
        else:
            raise ProtocolError(status)
