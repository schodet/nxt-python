# Copyright (C) 2009  Marcus Wanner
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

'Use for socked-driven communications with the NXT. Not done yet.'

import nxt.locator
from nxt.motor import *
from nxt.sensor import *
import socket, thread

def SENDRESULT(csock,ip,result):
        try:
            csock.send(result)
        except:
            print 'connection to '+ip+' terminated. unable to send command result code.'

def SERVECLIENT(csock,info,ip):
    exitcode = 0
    
    try:
        csock.send('0')
    except:
        print 'connection to '+ip+' terminated. unable to send connection success code.'
        csock.close()
        thread.exit_thread()

    while exitcode = 0:
        try:
            cmd = csock.recv(100)
        except:
            print 'connection to '+ip+' terminated. unable to recieve command data.'
            exitcode = 1
        if cmd == 'find_brick':
            try:
                b = nxt.locator.find_one_brick()
                b.connect()
            except:
        elif cmd == 'close_brick':
            try:
                b.close()
                try:
                    csock.send('0')
                except:
                    print 'connection to '+ip+' terminated. unable to send command success code.'
            except:
                try:
                    csock.send('1')
                except:
                    print 'connection to '+ip+' terminated. unable to send command failure code.'
            

def NEWCLIENTS(sock):
    while 1:
        client, info = sock.accept()
        print 'new client with info: ' + info
        thread.start_new_thread(SERVECLIENT,(client,info,info[0]))

def serve_forever():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 54174))
    sock.listen(5)
    thread.start_new_thread(NEWCLIENTS, (sock,))
