#!/usr/bin/env python
#
# nxt_push program -- Serve an interface to the NXT brick
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2010  rhn
# Copyright (C) 2011  zonedabone
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import nxt
import socket
from nxt.utils import parse_command_line_arguments
import sys

def serve(brick, channel, details):
    'handles serving the client'
    print "Connection started (" + details[0] + ')'
    run = True
    try:
        while run:
            data = channel.recv(1024)
            code =  data[0]
            if code == '\x00' or code == '\x01' or code == '\x02':
                brick.sock.send(data)
                reply = brick.sock.recv()
                channel.send(reply)
            elif code == '\x80' or code == '\x81':
                brick.sock.send(data)
            elif code == '\x98':
                channel.send(brick.sock.type)
            elif code == '\x99':
                run = False
                channel.close()
    except:
        channel.close()

if __name__ == "__main__":
    arguments, keyword_arguments = parse_command_line_arguments(sys.argv)
    if '--help' in arguments:
        print """nxt_server -- command server for NXT brick
Usage: nxt_server.py [--host <macaddress>][--name <name>]
[--iphost <server ip>][--ipport <server port>]"""
    print "Connecting to NXT..."
    brick = nxt.find_one_brick(keyword_arguments.get('host',None),keyword_arguments.get('name',None))
    print "Brick found."
    print "Starting server..."
    server = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    server.bind ((keyword_arguments.get('iphost',''), int(keyword_arguments.get('ipport','2727'))))
    server.listen (1)
    # Have the server serve "forever":
    while True:
        channel, details = server.accept()
        serve(brick, channel, details)
