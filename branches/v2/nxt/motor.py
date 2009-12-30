# nxt.motor module -- Class to control LEGO Mindstorms NXT motors
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
# Copyright (C) 2009  rhn
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

'Use for motor control'

import time
import warnings

PORT_A = 0x00
PORT_B = 0x01
PORT_C = 0x02
PORT_ALL = 0xFF

MODE_IDLE = 0x00
MODE_MOTOR_ON = 0x01
MODE_BRAKE = 0x02
MODE_REGULATED = 0x04

REGULATION_IDLE = 0x00
REGULATION_MOTOR_SPEED = 0x01
REGULATION_MOTOR_SYNC = 0x02

RUN_STATE_IDLE = 0x00
RUN_STATE_RAMP_UP = 0x10
RUN_STATE_RUNNING = 0x20
RUN_STATE_RAMP_DOWN = 0x40

LIMIT_RUN_FOREVER = 0

class BlockedException(Exception):
    pass

class OutputState(object):
    """An object holding the internal state of a motor, not including counters.
    """
    def __init__(self, values):
        (self.power, self.mode, self.regulation,
            self.turn_ratio, self.run_state, self.tacho_limit,
) = values
    
    def to_list(self):
        """Returns a list of properties that can be used with set_output_state.
        """
        return [self.power, self.mode, self.regulation,
            self.turn_ratio, self.run_state, self.tacho_limit]
        
    def __str__(self):
        modes = []
        if self.mode & MODE_MOTOR_ON:
            modes.append('on')
        if self.mode & MODE_BRAKE:
            modes.append('brake')
        if self.mode & MODE_REGULATED:
            modes.append('regulated')
        if not modes:
            modes.append('idle')
        mode = '&'.join(modes)
        regulation = 'regulation: ' + \
                            ['idle', 'speed', 'sync'][self.regulation]
        run_state = 'run state: ' + {0: 'idle', 0x10: 'ramp_up',
                            0x20: 'running', 0x40: 'ramp_down'}[self.run_state]
        return ', '.join([mode, regulation, str(self.turn_ratio), run_state] + [str(self.tacho_limit)])


class TachoInfo:
    """An object containing the information about the state of a motor"""
    def __init__(self, values):
        self.tacho_count, self.block_tacho_count, self.rotation_count = values
    
    def __str__(self):
        return str((self.tacho_count, self.block_tacho_count,
                   self.rotation_count))
    

def get_tacho_and_state(values):
    """A convenience function. values is the list of values from
    get_output_state. Returns both OutputState and TachoInfo.
    """
    return OutputState(values[1:7]), TachoInfo(values[7:])


class Motor(object):
    debug = 0
    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self._read_state()

    def _debug_out(self, message):
        if self.debug:
            print message

    def set_state(self, state):
        self._debug_out('Setting brick output state...')
        list_state = [self.port] + state.to_list()
        self.brick.set_output_state(*list_state)
        self._state = state
        self._debug_out('State set.')

    def _read_state(self):
        self._debug_out('Getting brick output state...')
        values = self.brick.get_output_state(self.port)
        self._debug_out('State got.')
        self._state, tacho = get_tacho_and_state(values)
        return self._state, tacho
    
    #def get_tacho_and_state here would allow tacho manipulation
    
    def get_state(self):
        """Returns a copy of the current motor state for manipulation."""
        return OutputState(self._state.to_list())
        
    def get_tacho(self):
        return self._read_state()[1]
    
    def reset_tacho(self):
        pass
        
    def reset_position(self, relative):
        """What does it do?"""
        self.brick.reset_motor_position(self.port, relative)

    def run(self, power=100, regulated=False):
        '''Tells the motor to run continuously. If regulated is True, then the
        rotation speed seems to decrease after a few seconds.
        '''
        state = self.get_state()
        state.power = power
        if regulated:
            state.mode = MODE_MOTOR_ON | MODE_REGULATED
            state.regulation = REGULATION_MOTOR_SPEED
        else:
            state.mode = MODE_MOTOR_ON
            state.regulation = REGULATION_IDLE
        state.turn_ratio = 0
        state.run_state = RUN_STATE_RUNNING
        state.tacho_limit = LIMIT_RUN_FOREVER
        self.set_state(state)

    def hold(self):
        """Holds the motor in place"""
        state = self.get_state()
        state.power = 0
        state.mode = MODE_MOTOR_ON | MODE_BRAKE | MODE_REGULATED
        state.regulation = REGULATION_MOTOR_SPEED
        state.run_state = RUN_STATE_RUNNING
        state.turn_ratio = 0
        state.tacho_limit = LIMIT_RUN_FOREVER
        self.set_state(state)
        

    def stop(self):
        '''Tells the motor to stop whatever it's doing'''
        state = self.get_state()
        state.power = 0
        state.mode = MODE_IDLE
        state.regulation = REGULATION_IDLE
        state.run_state = RUN_STATE_IDLE
        state.turn_ratio = 0
        state.tacho_limit = LIMIT_RUN_FOREVER
        self.set_state(state)
    
    release = stop # hold-release pair
    
    def weak_turn(self, power, tacho_units):
        """Tries to turn a motor for the specified distance. This function
        returns immediately, and it's not guaranteed that the motor turns that
        distance. This is an interface to use tacho_limit without
        REGULATION_MODE_SPEED
        """
        tacho_limit = tacho_units
        tacho = self.get_tacho()
        state = self.get_state()

        # Update modifiers even if they aren't used, might have been changed
        state.mode = MODE_MOTOR_ON
        state.regulation = REGULATION_IDLE
        state.turn_ratio = 0
        state.run_state = RUN_STATE_RUNNING
        state.power = power
        state.tacho_limit = tacho_limit

        self._debug_out('Updating motor information...')
        self.set_state(state)
        

    def turn(self, power, tacho_units, brake=True, timeout=1):
        """Use this to turn a motor. power is a value between -127 and 128,
        The motor will not stop until it turns the desired distance. Brake is
        whether or not to stop the motor after the function exits (either by
        reaching the distance or throwing an exception). timeout is the amount
        of time after which a BlockedException is raised if the motor hasn't
        moved.
        """
        def eta(tacho, power):
            """Returns time in seconds. Do not trust it too much"""
            return (float(tacho) / power) / 5
 
        tacho_limit = tacho_units
        tacho = self.get_tacho()
        state = self.get_state()

        # Update modifiers even if they aren't used, might have been changed
        state.mode = MODE_MOTOR_ON
        state.regulation = REGULATION_MOTOR_SPEED
        state.turn_ratio = 0
        state.run_state = RUN_STATE_RUNNING
        state.power = power
        state.tacho_limit = tacho_limit

        self._debug_out('Updating motor information...')
        self.set_state(state)
       
        direction = 1 if power > 0 else -1
        self._debug_out('tachocount: ' + str(tacho))
        tacho_target = tacho.tacho_count + tacho_limit*direction
        self._debug_out('tacho target: ' + str(tacho_target))
        current_time = time.time()
        remaining_tacho = tacho_target - tacho.tacho_count
            
        blocked = False
            
        while True:
            self._debug_out('tachocount: ' + str(tacho.tacho_count))                
            self._debug_out('tachocount: ' + str(tacho_target))
            
            if remaining_tacho * direction <= 0:
                break
            time.sleep(eta(remaining_tacho, power) / 2)
            
            if not blocked: # if already blocked, don't reset the counter
                last_remaining_tacho = remaining_tacho
                last_time = current_time
            
            tacho = self.get_tacho()
            current_time = time.time()
            remaining_tacho = tacho_target - tacho.tacho_count
            
            blocked = (last_remaining_tacho - remaining_tacho) * direction <= 0
            if blocked:
#                print 'not advancing', last_remaining_tacho, remaining_tacho    
                if current_time - last_time > timeout:
                    if brake:
                        self.hold()
                    else:
                        self.stop()
                    raise BlockedException("Blocked!")
  #          else:
    #            print 'advancing', last_remaining_tacho, remaining_tacho

        if brake:
            self.hold()
