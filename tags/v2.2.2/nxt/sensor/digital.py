# nxt.sensor module -- Classes to read LEGO Mindstorms NXT sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010,2011,2012  Marcus Wanner
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

from nxt.error import I2CError, I2CPendingError, DirProtError

from common import *
from time import sleep, time
import struct


class SensorInfo:
    def __init__(self, version, product_id, sensor_type):
        self.version = version
        self.product_id = product_id
        self.sensor_type = sensor_type
    
    def clarifybinary(self, instr, label):
        outstr = ''
        outstr += (label + ': `' + instr + '`\n')
        for char in instr:
            outstr += (hex(ord(char))+', ')
        outstr += ('\n')
        return outstr
    
    def __str__(self):
        outstr = ''
        outstr += (self.clarifybinary(str(self.version), 'Version'))
        outstr += (self.clarifybinary(str(self.product_id), 'Product ID'))
        outstr += (self.clarifybinary(str(self.sensor_type), 'Type'))
        return outstr

class BaseDigitalSensor(Sensor):
    """Object for digital sensors. I2C_ADDRESS is the dictionary storing name
    to i2c address mappings. It should be updated in every subclass. When
    subclassing this class, make sure to call add_compatible_sensor to add
    compatible sensor data.
    """
    I2C_DEV = 0x02
    I2C_ADDRESS = {'version': (0x00, '8s'),
        'product_id': (0x08, '8s'),
        'sensor_type': (0x10, '8s'),
#        'factory_zero': (0x11, 1),      # is this really correct?
        'factory_scale_factor': (0x12, 'B'),
        'factory_scale_divisor': (0x13, 'B'),
    }
    
    def __init__(self, brick, port, check_compatible=True):
        """Creates a BaseDigitalSensor. If check_compatible is True, queries
        the sensor for its name, and if a wrong sensor class was used, prints
        a warning.
        """
        super(BaseDigitalSensor, self).__init__(brick, port)
        self.set_input_mode(Type.LOW_SPEED_9V, Mode.RAW)
        self.last_poll = time()
        self.poll_delay = 0.01
        sleep(0.1)  # Give I2C time to initialize
        #Don't do type checking if this class has no compatible sensors listed.
        try: self.compatible_sensors
        except AttributeError: check_compatible = False
        if check_compatible:
            sensor = self.get_sensor_info()
            if not sensor in self.compatible_sensors:
                print ('WARNING: Wrong sensor class chosen for sensor ' + 
                          str(sensor.product_id) + ' on port ' + str(port) + '. ' + """
You may be using the wrong type of sensor or may have connected the cable
incorrectly. If you are sure you're using the correct sensor class for the
sensor, this message is likely in error and you should disregard it and file a
bug report, including the output of get_sensor_info(). This message can be
suppressed by passing "check_compatible=False" when creating the sensor object.""")

    def _ls_get_status(self, n_bytes):
        for n in range(30): #https://code.google.com/p/nxt-python/issues/detail?id=35
            try:
                b = self.brick.ls_get_status(self.port)
                if b >= n_bytes:
                    return b
            except I2CPendingError:
                pass
        raise I2CError, 'ls_get_status timeout'

    def _i2c_command(self, address, value, format):
        """Writes an i2c value to the given address. value must be a string. value is
        a tuple of values corresponding to the given format.
        """
        value = struct.pack(format, *value)
        msg = chr(self.I2C_DEV) + chr(address) + value
        now = time()
        if self.last_poll+self.poll_delay > now:
            diff = now - self.last_poll
            sleep(self.poll_delay - diff)
        self.last_poll = time()
        self.brick.ls_write(self.port, msg, 0)

    def _i2c_query(self, address, format):
        """Reads an i2c value from given address, and returns a value unpacked
        according to the given format. Format is the same as in the struct
        module. See http://docs.python.org/library/struct.html#format-strings
        """
        n_bytes = struct.calcsize(format)
        msg = chr(self.I2C_DEV) + chr(address)
        now = time()
        if self.last_poll+self.poll_delay > now:
            diff = now - self.last_poll
            sleep(self.poll_delay - diff)
        self.last_poll = time()
        self.brick.ls_write(self.port, msg, n_bytes)
        try:
            self._ls_get_status(n_bytes)
        finally:
            #we should clear the buffer no matter what happens
            data = self.brick.ls_read(self.port)
        if len(data) < n_bytes:
            raise I2CError, 'Read failure: Not enough bytes'
        data = struct.unpack(format, data[-n_bytes:])
        return data
        
    def read_value(self, name):
        """Reads a value from the sensor. Name must be a string found in
        self.I2C_ADDRESS dictionary. Entries in self.I2C_ADDRESS are in the
        name: (address, format) form, with format as in the struct module.
        Be careful on unpacking single variables - struct module puts them in
        tuples containing only one element.
        """
        address, fmt = self.I2C_ADDRESS[name]
        for n in range(3):
            try:
                return self._i2c_query(address, fmt)
            except DirProtError:
                pass
        raise I2CError, "read_value timeout"

    def write_value(self, name, value):
        """Writes value to the sensor. Name must be a string found in
        self.I2C_ADDRESS dictionary. Entries in self.I2C_ADDRESS are in the
        name: (address, format) form, with format as in the struct module.
        value is a tuple of values corresponding to the format from
        self.I2C_ADDRESS dictionary.
        """
        address, fmt = self.I2C_ADDRESS[name]
        self._i2c_command(address, value, fmt)
    
    def get_sensor_info(self):
        version = self.read_value('version')[0].split('\0')[0]
        product_id = self.read_value('product_id')[0].split('\0')[0]
        sensor_type = self.read_value('sensor_type')[0].split('\0')[0]
        return SensorInfo(version, product_id, sensor_type)
        
    @classmethod
    def add_compatible_sensor(cls, version, product_id, sensor_type):
        """Adds an entry in the compatibility table for the sensor. If version
        is None, then it's the default class for this model. If product_id is
        None, then this is the default class for this vendor.
        """
        try:
            cls.compatible_sensors
        except AttributeError:
            cls.compatible_sensors = []
        finally:
            cls.compatible_sensors.append(SCompatibility(version, product_id,
                                                                            sensor_type))
            add_mapping(cls, version, product_id, sensor_type)
            
            
class SCompatibility(SensorInfo):
    """An object that helps manage the sensor mappings"""
    def __eq__(self, other):
        if self.product_id is None:
            return self.product_id == other.product_id
        elif self.version is None:
            return (self.product_id == other.product_id and
                    self.sensor_type == other.sensor_type)
        else:
            return (self.version == other.version and
                    self.product_id == other.product_id and
                    self.sensor_type == other.sensor_type)

sensor_mappings = {}


def add_mapping(cls, version, product_id, sensor_type):
    "None means any other value"
    if product_id not in sensor_mappings:
        sensor_mappings[product_id] = {}
    models = sensor_mappings[product_id]
       
    if sensor_type is None:
        if sensor_type in models:
            raise ValueError('Already registered!')
        models[sensor_type] = cls
        return

    if sensor_type not in models:
        models[sensor_type] = {}
    versions = models[sensor_type]
    
    if version in versions:
        raise ValueError('Already registered!')
    else:
        versions[version] = cls


class SearchError(Exception):
    pass


def find_class(info):
    """Returns an appropriate class for the given SensorInfo"""
    dic = sensor_mappings
    for val, msg in zip((info.product_id, info.sensor_type, info.version),
                                    ('Vendor', 'Model', 'Version')):
        if val in dic:
            dic = dic[val]
        elif None in dic:
            dic = dic[None]
        else:
            raise SearchError(msg + ' not found')
        return dic[info.sensor_type][None]
