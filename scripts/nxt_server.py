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

def serve(channel, details):
    'handles serving the client'
    run = True
    while run:
        data = channel.recv(1024)
        code =  data[0]
        if code == '\x00' or code == '\x01' or code == '\x02':
            brick.sock.send(data)
            reply = brick.sock.recv()
            channel.send(reply)
        elif code == '\x80' or code == '\x81':
            brick.sock.send(data)
        elif code == '\x99':
            run = False
            channel.slose()

if __name__ == "__main__":
    print "Connecting to NXT..."
    brick = nxt.find_one_brick()
    print "Brick found."
    print "Starting server..."
    server = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    server.bind ( ( '', 2727 ) )
    server.listen ( 5 )
    # Have the server serve "forever":
    while True:
        channel, details = server.accept()
        serve(channel, details)
