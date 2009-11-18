# nxt.sensor module -- Classes to read LEGO Mindstorms NXT sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira
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

from .common import *
from .analog import BaseAnalogSensor
from .digital import BaseDigitalSensor
from .generic import Touch, Light, Sound, Ultrasonic, Accelerometer
import mindsensors
MSSumoEyes = mindsensors.SumoEyes
MSCompass = mindsensors.Compass
MSIRLong = mindsensors.IRLong
import hitechnic
HTCompass = hitechnic.Compass

