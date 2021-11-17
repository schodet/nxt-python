# nxt.motcont module -- Interface to Linus Atorf's MotorControl NXC
# Copyright (C) 2011  Marcus Wanner
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

import nxt
import nxt.error
import time
from threading import Lock

class MotorConError(nxt.error.ProtocolError):
    pass

def _power(power):
    pw = abs(power)
    psign = int(power >= 0) * 2 - 1
    if psign == -1:
        pw += 100
    pw = str(pw)
    pw = '0'*(3-len(pw))+pw #pad front with 0s to make 3 chars
    return pw

def _tacho(tacholimit):
    tacho = str(tacholimit)
    tacho = '0'*(6-len(tacho))+tacho #pad front with 0s to make 6 chars
    return tacho

class MotCont():
    '''
This class provides an interface to Linus Atorf's MotorControl NXC
program. It is a wrapper which follows the documentation at 
http://www.mindstorms.rwth-aachen.de/trac/wiki/MotorControl
and provides command strings and timing intervals as dictated there. To
use this module, you will need to put MotorControl22.rxe on your NXT
brick. This file and its corresponding source can be found at
http://www.mindstorms.rwth-aachen.de/trac/browser/trunk/tools/MotorControl
You can use nxt_push or any other nxt file manager to put the file on
the NXT. Before using any of the functions here, use MotCont.start() to
start the program. You can also start it manually my using the menu on
the brick. When your script exits, it would be a good idea to do
b.stop_program().
'''
    def __init__(self, brick):
        self.brick = brick
        self.is_ready_lock = Lock()
        self.last_is_ready = time.time()-1
        self.last_cmd = {}

    def _interval_is_ready(self):
        delay = 0.010
        diff = time.time() - self.last_is_ready
        if diff < delay:
            time.sleep(delay - diff)

    def _interval_motors(self, ports):
        delay = 0.015
        now = time.time()
        diff = delay
        for port in ports:
            if port in self.last_cmd:
                diff = min(diff, now - self.last_cmd[port])
        if diff < delay:
            time.sleep(delay - diff)

    def _record_time_motors(self, ports):
        now = time.time()
        for port in ports:
            self.last_cmd[port] = now

    def _decode_ports(self, ports, max_ports):
        try:
            ports = frozenset(ports)
        except TypeError:
            ports = frozenset((ports, ))
        mapping = {
            frozenset((nxt.motor.PORT_A, )): "0",
            frozenset((nxt.motor.PORT_B, )): "1",
            frozenset((nxt.motor.PORT_C, )): "2",
            frozenset((nxt.motor.PORT_A, nxt.motor.PORT_B)): "3",
            frozenset((nxt.motor.PORT_A, nxt.motor.PORT_C)): "4",
            frozenset((nxt.motor.PORT_B, nxt.motor.PORT_C)): "5",
            frozenset((nxt.motor.PORT_A, nxt.motor.PORT_B, nxt.motor.PORT_C)): "6",
        }
        if ports not in mapping or len(ports) > max_ports:
            raise ValueError("invalid combination of ports")
        return ports, mapping[ports]
    
    def cmd(self, ports, power, tacholimit, speedreg=1, smoothstart=0, brake=0):
        '''
Sends a "CONTROLLED_MOTORCMD" to MotorControl. port is
nxt.motor.PORT_[A-C], power is -100-100, tacholimit is 0-999999,
speedreg is whether to try to maintain speeds under load, and brake is
whether to enable active braking after the motor is in the specified
place (DIFFERENT from the nxt.motor.turn() function's brake arg).'''
        self._interval_is_ready()
        ports, strports = self._decode_ports(ports, 2)
        self._interval_motors(ports)
        mode = str(
            0x01*int(brake)+
            0x02*int(speedreg)+
            0x04*int(smoothstart)
            )
        command = '1'+strports+_power(power)+_tacho(tacholimit)+mode
        self.brick.message_write(1, command.encode("ascii"))
        self._record_time_motors(ports)
    
    def reset_tacho(self, ports):
        '''
Sends a "RESET_ERROR_CORRECTION" to MotorControl, which causes it to
reset the current tacho count for that motor.'''
        self._interval_is_ready()
        ports, strports = self._decode_ports(ports, 3)
        command = '2'+strports
        self.brick.message_write(1, command.encode("ascii"))
        self._record_time_motors(ports)
    
    def is_ready(self, port):
        '''
Sends an "ISMOTORREADY" to MotorControl and returns the reply.'''
        self._interval_is_ready()
        ports, strports = self._decode_ports(port, 1)
        with self.is_ready_lock:
            command = '3'+strports
            self.brick.message_write(1, command.encode("ascii"))
            time.sleep(0.015) #10ms pause from the docs seems to not be adequate
            reply = self.brick.message_read(0, 1, 1)[1]
            if chr(reply[0]) != strports:
                raise MotorConError('wrong port returned from ISMOTORREADY')
        self.last_is_ready = time.time()
        return bool(int(chr(reply[1])))

    def set_output_state(self, ports, power, tacholimit, speedreg=1):
        '''
Sends a "CLASSIC_MOTORCMD" to MotorControl. Brick is a brick object,
port is nxt.motor.PORT_[A-C], power is -100-100, tacholimit is 0-999999,
speedreg is whether to try to maintain speeds under load, and brake is
whether to enable active braking after the motor is in the specified
place (DIFFERENT from the nxt.motor.turn() function's brake arg).'''
        self._interval_is_ready()
        ports, strports = self._decode_ports(ports, 2)
        self._interval_motors(ports)
        command = '4'+strports+_power(power)+_tacho(tacholimit)+str(speedreg)
        self.brick.message_write(1, command.encode("ascii"))
        self._record_time_motors(ports)

    def start(self, version=22):
        '''
Starts the MotorControl program on the brick. It needs to already be
present on the brick's flash and named MotorControlXX.rxc, where XX is
the version number passed as the version arg (default is whatever is
bundled with this version of nxt-python).'''
        try:
            self.brick.stop_program()
            time.sleep(1)
        except nxt.error.DirProtError:
            pass
        self.brick.start_program('MotorControl%d.rxe' % version)
        time.sleep(0.1)
    
    def stop(self):
        '''
Used to stop the MotorControl program. All this actually does is stop
the currently running rxe.'''
        self.brick.stop_program()
