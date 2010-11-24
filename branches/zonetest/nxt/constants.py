# nxt.brick module -- Constants used by other modules
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

# Telegram Types

DIRECT_REPLY = '\x00'
SYSTEM_REPLY = '\x01'
REPLY = '\x02'
DIRECT_NOREPLY = '\x80'
SYSTEM_NOREPLY = '\x81'

# Command Types

SET_BRICK_NAME = '\x98'
GET_DEVICE_INFO = '\x9B'
GET_FIRMWARE_VERSION = '\x88'
DEL_USER_FLASH = '\xA0'
GET_OUTPUT_STATE = '\x06'

# Struct Constants

S_CHAR = '<b'
U_CHAR = '<B'
S_INT  = '<i'
U_INT  = '<I'
S_LONG = '<l'
U_LONG = '<L'


# Other Constants

NULL = '\x00'