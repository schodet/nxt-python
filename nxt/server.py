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

'''Use for socked-driven communications with the NXT. Functional, but not
complete.'''

import nxt.locator
from nxt.motor import *
from nxt.sensor import *
import socket, thread, sys

host = ''
port = 54174
outport = 54374

def _process_command(cmd):
    retcode = 0
    retmsg = ''
    #act on messages, these conditions can be in no particular order
    #it should send a return code on port 54374. 0 for success, 1 for failure
    #then maybe an error message?
    #find_brick
    if cmd == 'find_brick':
        try:
            brick = nxt.locator.find_one_brick()
            brick.connect()
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])

    #get_light_sample
    elif cmd == 'get_light_sample':
        try:
            retmsg = str(LightSensor(brick, PORT_3).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
        
    #get_sound_sample
    elif cmd == 'get_sound_sample':
        try:
            retmsg = str(SoundSensor(brick, PORT_2).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
    
    #get_ultrasonic_sample
    elif cmd == 'get_ultrasonic_sample':
        try:
            retmsg = str(UltrasonicSensor(brick, PORT_4).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
    
    #get_touch_sample
    elif cmd == 'get_touch_sample':
        try:
            retmsg = str(TouchSensor(brick, PORT_1).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
    
    #set_motor This one will require some extra complexity...
    elif cmd == 'get_touch_sample':
        retmsg = 'Not imlemented yet.'
        retcode = 1
    
    #play_tone This one too...it will return after the tone function does
    elif cmd == 'get_touch_sample':
        retmsg = 'Not imlemented yet.'
        retcode = 1

    #close_brick
    elif cmd == 'close_brick':
        try:
            brick.close()
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
    
    #command not recognised
    else:
        retmsg = 'Command not found.'
        retcode = 1
    
    #then return 1 or 0 and a message
    return retcode, retmsg

def serve_forever():
    'Serve clients until the window is closed or there is an unhandled error.'
    #make sockets
    rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    while 1:
        #get a message from port on any host
        inmsg, addr = sock.recvfrom(100) #no commands can be longer than 100 chars
        print addr
        
        #process it
        code, message = _process_command(inmsg)
        
        #send return code to the computer that send the request
        rsock.sendto(str(code) + message, addr[1])
        
        #do again
