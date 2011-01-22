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
            message = parse_in(SYSTEM_REPLY, SET_BRICK_NAME, (RAW,name))
            data = self.sock.send_and_recv(message)
            check_status(data[2])
        else:
            message = SYSTEM_NOREPLY + SET_BRICK_NAME + name
            self.sock.send(message)

    def get_device_info(self):
        data = self.sock.send_and_recv(parse_in(SYSTEM_REPLY,GET_DEVICE_INFO))
        self.data=data
        if self.debug != 0:
            check_status(data[2])
        info = parse_out(data,(RAW,15), U_CHAR, U_CHAR, U_CHAR, U_CHAR, U_CHAR,
            U_CHAR,(F_BYTE,1),U_INT,U_INT)
        address = '%02X:%02X:%02X:%02X:%02X:%02X' % (info[1], info[2], info[3], info[4], info[5], info[6])
        btsignal = info[7]
        freeflash = info[8]
        return (info[0],address,btsignal,freeflash)

    def get_firmware_version(self):
        """Returns ((ProtocolMaj,ProtocolMin),(FirmwareMaj,FirmwareMin))"""
        message = parse_in(SYSTEM_REPLY, GET_FIRMWARE_VERSION)
        data = self.sock.send_and_recv(message)
        if self.debug != 0:
            check_status(data[2])
        info = parse_in(U_CHAR,U_CHAR,U_CHAR,U_CHAR)
        return (info[1],info[0],info[3],info[2])

    def del_user_flash(self):
        message = parse_in(SYSTEM_REPLY, DEL_USER_FLASH)
        self.sock.send_and_recv(message)

    def get_output_state(self,port):
        message = parse_in(DIRECT_REPLY,GET_OUTPUT_STATE,(U_CHAR,port))
        data = self.sock.send_and_recv(message)
        if self.debug != 0:
            check_status(data[2])
        info = parse_out(data,U_CHAR,S_CHAR,U_CHAR,U_CHAR,S_CHAR,U_CHAR,U_INT,
            S_INT,S_INT,S_INT)
        return info

    def set_output_state(self, port, power, mode, regulation, turn_ratio, run_state, tacho_limit):
        if self.debug == 2:
            type = DIRECT_REPLY
        else:
            type = DIRECT_NOREPLY
        data = parse_in(type,SET_OUTPUT_STATE,(U_CHAR,port),(S_CHAR,power),
            (U_CHAR,mode),(U_CHAR,regulation),(S_CHAR,turn_ratio),
            (U_CHAR,run_state),(U_INT,tacho_limit))
        if self.debug == 2:
            result = self.sock.send_and_recv(data)
            check_status(result[2])
        else:
            self.sock.send(data)

    def set_input_mode(self, port, type, mode):
        if self.debug == 2:
            msgtype = DIRECT_REPLY
        else:
            msgtype = DIRECT_NOREPLY
        message = parse_in(msgtype,SET_INPUT_MODE,(U_CHAR,port),(U_CHAR,type),
            (U_CHAR,mode))
        if self.debug == 2:
            data=self.sock.send_and_recv(message)
            check_status(data[2])
        else:
            self.sock.send(message)

    def get_input_values(self, port):
        message = parse_in(DIRECT_REPLY,GET_INPUT_VALUES,(U_CHAR,port))
        data = self.sock.send_and_recv(message)
        if self.debug != 0: check_status(data[2])
        final = parse_out(data,U_CHAR,U_CHAR,U_CHAR,U_CHAR,U_CHAR,U_SHT,U_SHT,S_SHT,S_SHT)
        return final

    def ls_get_status(self,port):
        message = parse_in(DIRECT_REPLY,LS_GET_STATUS,(U_CHAR,port))
        data = self.sock.send_and_recv(message)
        if self.debug != 0: check_status(data[2])
        return ord(data[3])

    def ls_write(self, port, tx_data, rx_bytes):
        if self.debug == 2:
            type = DIRECT_REPLY
        else:
            type = DIRECT_NOREPLY
        message = parse_in(type,LS_WRITE,(U_CHAR,port),(U_CHAR,rx_bytes),
            (RAW,tx_data))
        if self.debug == 2:
            data = self.sock.send_and_recv(message)
            check_status(data)
        else:
            self.sock.send(message)

    def ls_read(self, port):
        message = parse_in(DIRECT_REPLY,LS_READ,(U_CHAR,port))
        data = self.sock.send_and_recv(message)
        if debug != 0: check_status(data[2])
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
