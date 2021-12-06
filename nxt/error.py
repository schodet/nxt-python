# nxt.error module -- NXT brick error handling
# Copyright (C) 2006, 2007  Douglas P Lau
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


class ProtocolError(Exception):
    """Raised on error with the NXT brick protocol."""

    pass


class SystemProtocolError(ProtocolError):
    """Raised on error with the NXT brick protocol for a system command."""

    pass


class FileExistsError(SystemProtocolError):
    """Raised when trying to create a file which already exists."""

    pass


class FileNotFoundError(SystemProtocolError):
    """Raised when trying to access a file which does not exists."""

    pass


class ModuleNotFoundError(SystemProtocolError):
    """Raised when trying to access a module which does not exists."""

    pass


class DirectProtocolError(ProtocolError):
    """Raised on error with the NXT brick protocol for a direct command."""

    pass


class I2CError(DirectProtocolError):
    """Raised on I2C error on a sensor port."""

    pass


class I2CPendingError(I2CError):
    """Raised when an I2C transaction on a sensor port is still in progress."""

    pass
