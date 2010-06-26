# nxt.sensor.common module -- submodule with stuff useful in all sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
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

PORT_1 = 0x00
PORT_2 = 0x01
PORT_3 = 0x02
PORT_4 = 0x03

class Type(object):
    'Namespace for enumeration of the type of sensor'
    # NOTE: just a namespace (enumeration)
    NO_SENSOR = 0x00
    SWITCH = 0x01       # Touch sensor
    TEMPERATURE = 0x02
    REFLECTION = 0x03
    ANGLE = 0x04
    LIGHT_ACTIVE = 0x05 # Light sensor (illuminated)
    LIGHT_INACTIVE = 0x06   # Light sensor (ambient)
    SOUND_DB = 0x07     # Sound sensor (unadjusted)
    SOUND_DBA = 0x08    # Sound sensor (adjusted)
    CUSTOM = 0x09
    LOW_SPEED = 0x0A
    LOW_SPEED_9V = 0x0B # Low-speed I2C (Ultrasonic sensor)
    HIGH_SPEED = 0x0C #Possibly other mode for I2C; may be used by future sensors.
    COLORFULL = 0x0D  #NXT 2.0 color sensor in full color mode (color sensor mode)
    COLORRED = 0x0E   #NXT 2.0 color sensor with red light on  (light sensor mode)
    COLORGREEN = 0x0F #NXT 2.0 color sensor with green light on (light sensor mode)
    COLORBLUE = 0x10  #NXT 2.0 color sensor in with blue light on (light sensor mode)
    COLORNONE = 0x11  #NXT 2.0 color sensor in with light off (light sensor mode)
    COLOREXIT = 0x12  #NXT 2.0 color sensor internal state  (not sure what this is for yet)


class Mode(object):
    'Namespace for enumeration of the mode of sensor'
    # NOTE: just a namespace (enumeration)
    RAW = 0x00
    BOOLEAN = 0x20
    TRANSITION_CNT = 0x40
    PERIOD_COUNTER = 0x60
    PCT_FULL_SCALE = 0x80
    CELSIUS = 0xA0
    FAHRENHEIT = 0xC0
    ANGLE_STEPS = 0xE0
    MASK = 0xE0
    MASK_SLOPE = 0x1F   # Why isn't this slope thing documented?


class Sensor(object):
    'Main sensor object'

    def __init__(self, brick, port):
        self.brick = brick
        self.port = port

    def set_input_mode(self, type_, mode):
        self.brick.set_input_mode(self.port, type_, mode)
