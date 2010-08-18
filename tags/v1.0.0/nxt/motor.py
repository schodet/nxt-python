# nxt.motor module -- Class to control LEGO Mindstorms NXT motors
# Copyright (C) 2006  Douglas P Lau
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

'Use for motor control'

import time

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

class Motor(object):

    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self.power = 0
        self.mode = MODE_IDLE
        self.regulation = REGULATION_IDLE
        self.turn_ratio = 0
        self.run_state = RUN_STATE_IDLE
        self.tacho_limit = LIMIT_RUN_FOREVER
        self.tacho_count = 0
        self.block_tacho_count = 0
        self.rotation_count = 0
        self.debug = 0

    def _debug_out(self, message):
        if self.debug:
            print message

    def set_output_state(self):
        self._debug_out('Setting brick output state...')
        self.brick.set_output_state(self.port, self.power, self.mode, self.regulation, self.turn_ratio, self.run_state, self.tacho_limit)
        self._debug_out('State set.')

    def get_output_state(self):
        self._debug_out('Getting brick output state...')
        values = self.brick.get_output_state(self.port)
        (self.port, self.power, self.mode, self.regulation,
            self.turn_ratio, self.run_state, self.tacho_limit,
            self.tacho_count, self.block_tacho_count,
            self.rotation_count) = values
        self._debug_out('State got.')
        return values

        def reset_position(self, relative):
            self.brick.reset_motor_position(self.port, relative)

    def update(self, power, tacho_limit, braking=False):
        '''Use this to run a motor. power is a value between -127 and 128, tacho_limit is the
number of degrees to apply power for. Braking is wether or not to stop the motor
after turning the specified degrees (Under construction).'''

        if braking:
            direction = (power > 0)*2-1
            self.get_output_state()
            starting_tacho_count = self.tacho_count

            self._debug_out('tachocount: '+str(starting_tacho_count))
            
            tacho_target = starting_tacho_count + tacho_limit*direction
            
            self._debug_out('tacho target: '+str(tacho_target))

        self.mode = MODE_MOTOR_ON
        self.run_state = RUN_STATE_RUNNING
        self.power = power
        self.tacho_limit = tacho_limit
        
        self._debug_out('Updating motor information...')
        
        if braking:

            self.update(power, 1, 0)
            
            current_tacho = 0
            
            while 1:
                
                self._debug_out('checking tachocount...')

                olderTachoCount = current_tacho
                self.get_output_state()
                current_tacho = self.tacho_count
                
                self._debug_out('tachocount: '+str(current_tacho))
                
                if current_tacho<tacho_target+10 and current_tacho>tacho_target-10:
                    
                    self._debug_out('tachocount good, breaking from loop...')
                    
                    break
                
                else:
                    if current_tacho==olderTachoCount: #motor hasn't moved
                    
                        self._debug_out('tachocount bad, giving extra power...')

                        self.update(power, 1, 0)
                    else:
                        self._debug_out('tachocount bad, waiting...')

            self._debug_out('going in reverse...')
            
            self.update(direction*60, 1)
            time.sleep(0.01)
            self.mode = MODE_BRAKE
            self.set_output_state()

            self._debug_out('difference from goal: '+str(self.get_output_state()[7]-tacho_target))

        self.set_output_state()
        self._debug_out('Updating finished. ending tachocount: '+str(self.get_output_state()[7]))
