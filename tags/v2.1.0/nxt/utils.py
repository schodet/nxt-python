# nxt.utils module -- Generic utilities to support other modules
# Copyright (C) 2010  Vladimir Moskva
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

from collections import defaultdict

def parse_command_line_arguments(arguments):
    keyword_parameters = defaultdict(lambda: None)
    parameters = []
    current_key = None

    for argument in arguments[1:]:
        if argument in ('-h', '--host'):
            current_key = 'host'
        else:
            if current_key is not None:
                if argument.startswith('-'):
                    raise Exception('Invalid arguments')
                keyword_parameters[current_key] = argument
                current_key = None
            else:
                parameters.append(argument)
    return parameters, keyword_parameters

