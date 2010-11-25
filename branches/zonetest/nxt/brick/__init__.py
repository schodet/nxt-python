# nxt.brick module -- Classes to represent LEGO Mindstorms NXT bricks
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, rhn
# Copyright (C) 2010  rhn, Marcus Wanner, zonedabone
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

from time import sleep
from threading import RLock
from nxt.error import check_status
from nxt.constants import *
from struct import pack,unpack
#from .telegram import OPCODES, Telegram
#from .sensor import get_sensor

from classes import * #For compatibility

class Brick(object): #TODO: this begs to have explicit methods
    'Main object for NXT Control'
    debug = 1
    #0 = NO DEBUG ; 1 = DEBUG if already getting reply ; 2 = FORCE DEBUG

    def set_brick_name(self,name):
        if len(name) > 15:
            name = name[0:14]
        name = name + NULL * (16 - len(name))
        if self.debug == 2:
            message = SYSTEM_REPLY + SET_BRICK_NAME + name
            data = self.sock.send_and_recv(message)
            check_status(data[2])
        else:
            message = SYSTEM_NOREPLY + SET_BRICK_NAME + name
            self.sock.send(message)

    def get_device_info(self):
        data = self.sock.send_and_recv(SYSTEM_REPLY+GET_DEVICE_INFO)
        if self.debug != 0:
            check_status(data[2])
        info = {}
        info['name'] = ''.join(data[3:17].split(NULL))
        info['btaddr'] = list(data[18:24])
        info['btsignal'] = ord(data[25]) + (ord(data[28]) << 8)
        info['freeflash'] = ord(data[29]) + (ord(data[32]) << 8)
        return info

    def get_firmware_version(self):
        """Returns ((ProtocolMaj,ProtocolMin),(FirmwareMaj,FirmwareMin))"""
        message = SYSTEM_REPLY+GET_FIRMWARE_VERSION
        data = self.sock.send_and_recv(message)
        if self.debug != 0:
            check_status(data[2])
        return ((ord(data[4]),ord(data[3])),(ord(data[6]),ord(data[5])))

    def del_user_flash(self):
        message = SYSTEM_REPLY+DEL_USER_FLASH
        self.sock.send_and_recv(message)

    def get_output_state(self,port):
        message = DIRECT_REPLY+GET_OUTPUT_STATE+chr(port)
        data = self.sock.send_and_recv(message)
        if self.debug != 0:
            check_status(data[2])
        final = [None]*10
        final[0] = ord(data[3])
        final[1] = unpack(S_CHAR,data[4])[0]
        final[2] = ord(data[5])
        final[3] = ord(data[6])
        final[4] = unpack(S_CHAR,data[7])[0]
        final[5] = ord(data[8])
        final[6] = unpack(U_LONG,data[9:13])[0]
        final[7] = unpack(S_LONG,data[13:17])[0]
        final[8] = unpack(S_LONG,data[17:21])[0]
        final[9] = unpack(S_LONG,data[21:])[0]
        return tuple(final)

    def set_output_state(self, port, power, mode, regulation, turn_ratio, run_state, tacho_limit):
        if self.debug == 2:
            data = DIRECT_REPLY
        else:
            data = DIRECT_NOREPLY
        data += SET_OUTPUT_STATE
        data += chr(port)
        data += pack(S_CHAR, power)
        data += chr(mode)
        data += chr(regulation)
        data += pack(S_CHAR, turn_ratio)
        data += chr(run_state)
        data += pack(U_LONG, tacho_limit)
        if self.debug == 2:
            result = self.sock.send_and_recv(data)
            check_status(result[2])
        else:
            self.sock.send(data)

    def set_input_mode(self, port, type, mode):
        if self.debug == 2:
            message = DIRECT_REPLY
        else:
            message = DIRECT_NOREPLY
        message += SET_INPUT_MODE
        message += chr(port)
        message += chr(type)
        message += chr(mode)
        if self.debug == 2:
            data=self.sock.send_and_recv(message)
            check_status(data[2])
        else:
            self.sock.send(message)

    def get_input_values(self, port):
        message = DIRECT_REPLY+GET_INPUT_VALUES+chr(port)
        data = self.sock.send_and_recv(message)
        if self.debug != 0: check_status(data[2])
        final = [None] * 9
        final[0] = ord(data[3])
        final[1] = ord(data[4])
        final[2] = ord(data[5])
        final[3] = ord(data[6])
        final[4] = ord(data[7])
        final[5] = unpack(U_SHT,data[8:10])[0]
        final[6] = unpack(U_SHT,data[10:12])[0]
        final[7] = unpack(S_SHT,data[12:14])[0]
        final[8] = unpack(S_SHT,data[14:])[0]
        return tuple(final)


    def ls_get_status(self,port):
        message = DIRECT_REPLY+LS_GET_STATUS+chr(port)
        data = self.sock.send_and_recv(message)
        if self.debug != 0: check_status(data[2])
        return ord(data[3])

    def ls_write(self, port, tx_data, rx_bytes):
        if self.debug == 2:
            message = DIRECT_REPLY
        else:
            message = DIRECT_NOREPLY
        message += chr(port)
        message += chr(rx_bytes)
        message += tx_data
        if self.debug == 2:
            data = self.sock.send_and_recv(message)
            check_status(data)
        else:
            self.sock.send(message)

    def ls_read(self, port):
        message = DIRECT_REPLY+LS_READ+chr(port)
        data = self.sock.send_and_recv(message)
        if debug != 0:
            check_status(data[2])
        length = ord(data[3])
        return data[4:4+length]
    #__metaclass__ = _Meta

    def __init__(self, sock):
        self.sock = sock
        self.lock = RLock()
        self.sock.lock = self.lock

    #def play_tone_and_wait(self, frequency, duration):
    #    self.play_tone(frequency, duration)
    #    sleep(duration / 1000.0)

    def __del__(self):
        self.sock.close()

    #find_files = FileFinder
    #find_modules = ModuleFinder
    #open_file = File
    #get_sensor = get_sensor
