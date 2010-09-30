# nxt.sensor module -- Classes to read LEGO Mindstorms NXT sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010  Marcus Wanner
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

from .common import *
from .analog import BaseAnalogSensor
from .digital import BaseDigitalSensor, find_class
from .generic import Touch, Light, Sound, Ultrasonic, Color20
import mindsensors
MSSumoEyes = mindsensors.SumoEyes
MSCompassv2 = mindsensors.Compassv2
MSDIST = mindsensors.DIST
MSRTC = mindsensors.RTC
MSACCL = mindsensors.ACCL
MSServo = mindsensors.Servo
MSMTRMUX = mindsensors.MTRMUX
MSLineLeader = mindsensors.LineLeader
MSMMX = mindsensors.MMX
MSPS2 = mindsensors.PS2
MSHID = mindsensors.HID
import hitechnic
HTCompass = hitechnic.Compass
HTAccelerometer = hitechnic.Accelerometer
HTGyro = hitechnic.Gyro
HTColorv2 = hitechnic.Colorv2
HTEOPD = hitechnic.EOPD
HTIRReceiver = hitechnic.IRReceiver
HTIRSeekerv2 = hitechnic.IRSeekerv2
HTPrototype = hitechnic.Prototype


def get_sensor(brick, port):
    """Tries to detect the sensor type and return the correct sensor
object. Does not work for sensors with no identification information (such as
all analog sensors or the MindSensors RTC.
    """
    base_sensor = BaseDigitalSensor(brick, port, False)
    info = base_sensor.get_sensor_info()
    return find_class(info)(brick, port, check_compatible=False)
