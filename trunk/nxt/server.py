# nxt.server module -- LEGO Mindstorms NXT socket interface module
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

'''Use for a socket-interface NXT driver. Command and protocol docs at:
http://code.google.com/p/nxt-python/wiki/ServerUsage'''

import nxt.locator
from nxt.motor import *
from nxt.sensor import *
from nxt.compass import *
import socket, string, sys
global brick

host = ''
port = 54174
outport = 54374

def _process_port(nxtport):
    if nxtport == 'A' or nxtport == 'a':
        nxtport = PORT_A
    elif nxtport == 'B' or nxtport == 'b':
        nxtport = PORT_B
    elif nxtport == 'C' or nxtport == 'c':
        nxtport = PORT_C

    elif nxtport == '1':
        nxtport = PORT_1
    elif nxtport == '2':
        nxtport = PORT_2
    elif nxtport == '3':
        nxtport = PORT_3
    elif nxtport == '4':
        nxtport = PORT_4

    else:
        raise ValueError, 'Invalid port.'

    return nxtport

def _process_command(cmd):
    global brick
    retcode = 0
    retmsg = ''
    #act on messages, these conditions can be in no particular order
    #it should send a return code on port 54374. 0 for success, 1 for failure
    #then an error message
    #find_brick
    if cmd.startswith('find_brick'):
        try:
            brick = nxt.locator.find_one_brick()
            brick = brick.connect()
            retmsg = 'Connected to brick.'
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
    
    #get_touch_sample
    elif cmd.startswith('get_touch_sample'):
        try:
            port = string.split(cmd, ':')[1]
            port = _process_port(port)
            retmsg = str(TouchSensor(brick, port).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
        
    #get_sound_sample
    elif cmd.startswith('get_sound_sample'):
        try:
            port = string.split(cmd, ':')[1]
            port = _process_port(port)
            retmsg = str(SoundSensor(brick, port).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])

    #get_light_sample
    elif cmd.startswith('get_light_sample'):
        try:
            port = string.split(cmd, ':')[1]
            port = _process_port(port)
            retmsg = str(LightSensor(brick, port).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
    
    #get_ultrasonic_sample
    elif cmd.startswith('get_ultrasonic_sample'):
        try:
            port = string.split(cmd, ':')[1]
            port = _process_port(port)
            retmsg = str(UltrasonicSensor(brick, port).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])

    elif cmd.startswith('get_accelerometer_sample'):
        try:
            port = string.split(cmd, ':')[1]
            port = _process_port(port)
            retmsg = str(AccelerometerSensor(brick, port).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])

    #get_compass_sample
    elif cmd.startswith('get_compass_sample'):
        try:
            port = string.split(cmd, ':')[1]
            port = _process_port(port)
            retmsg = str(CompassSensor(brick, port).get_sample())
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
    
    #update_motor
    elif cmd.startswith('update_motor:'):
        try:
            #separate the information from the command keyword
            info = string.split(cmd, ':')[1]
            [port, power, tacholim] = string.split(info, ',')
        
            #process the port
            port = _process_port(port)

            Motor(brick, port).update(int(power), int(tacholim))
            retmsg = 'Motor command succeded.'
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])
    
    #play_tone
    elif cmd.startswith('play_tone:'):
        try:
            #separate the information from the command keyword
            info = string.split(cmd, ':')[1]
            [freq, dur] = string.split(info, ',')

            #call the function

            brick.play_tone_and_wait(int(freq), int(dur))
            retmsg = 'Tone command succeded.'
            retcode = 0
        except:
            retcode = 1
            retmsg = str(sys.exc_info()[1])

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

def serve_forever(password=None, authorizedips = []):
    '''Serve clients until the window is closed or there is an unhandled error.
If you supply a password, then any ip that wants to control the NXT will have
to send the password once to be authorized before any of the commands it sends
will be carried out.
authorizedips is a list of the ips that can have access to the NXT without
supplying a password. Normally, this is left blank.'''
    #make sockets
    outsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    insock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    insock.bind((host, port))
    while 1:
        #get a message from port on any host
        inmsg, (clientip,assignedport) = insock.recvfrom(100) #no commands can be longer than 100 chars

        #print a helpful message to the console.
        print 'Got command '+inmsg+' from '+clientip

        #process command
        if password:
            #password protection enabled
            try:
                authorizedips.index(clientip)
                #ip is authorized, and is therefore in the list of authorized ip
                code, message = _process_command(inmsg) #process the command as normal
            except ValueError:
                #ip not authorized, and therefore cannot be found in the list of authorized ips
                if inmsg == str(password):
                    #command is the correct password
                    authorizedips.append(clientip)
                    code = 0
                    message = 'Authorization successful.'
                else:
                    #command is not the password
                    code = 1
                    message = 'NXT access on this server is password protected, please send correct password to be authorized.'

        else:
            #not password protected
            code, message = _process_command(inmsg)
        
        #send return code to the computer that send the request
        outsock.sendto(str(code) + message, (clientip, 54374))

        #print a summany of the response
        print 'Sent return code '+str(code)+' with message "'+message+'" to '+clientip
        print ''
        
        #do again

#serve automatically if the script is started
#by double-clicking or by command line.
if __name__ == '__main__':
    try:
        password = sys.argv[1]
    except:
        password = None
    
    serve_forever(password)
