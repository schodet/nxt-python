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

'''class SysProtError(ProtocolError):
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
    pass'''

class NXTResponseError(Exception):
    pass

CODES = {
0x20 : NXTResponseError("Pending communication transaction in progress"),
0x40 : NXTResponseError("Specified mailbox queue is empty"),
0xBD : NXTResponseError("Request failed (i.e. specified file not found)"),
0xBE : NXTResponseError("Unknown command opcode"),
0xBF : NXTResponseError("Insane packet"),
0xC0 : NXTResponseError("Data contains out-of-range values"),
0xDD : NXTResponseError("Communication bus error"),
0xDE : NXTResponseError("No free memory in communication buffer"),
0xDF : NXTResponseError("Specified channel/connection is not valid"),
0xE0 : NXTResponseError("Specified channel/connection not configured or busy"),
0xEC : NXTResponseError("No active program"),
0xED : NXTResponseError("Illegal size specified"),
0xEE : NXTResponseError("Illegal mailbox queue ID specified"),
0xEF : NXTResponseError("Attempted to access invalid field of a structure"),
0xF0 : NXTResponseError("Bad input or output specified"),
0xFB : NXTResponseError("Insufficient memory available"),
0xFF : NXTResponseError("Bad arguments"),
}

def check_status(status):
    if CODES.has_key(status):
        raise CODES[status]