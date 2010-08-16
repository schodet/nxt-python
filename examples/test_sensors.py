#!/usr/bin/env python

import nxt.locator
from nxt.sensor import *

b = nxt.locator.find_one_brick()

print 'Touch:', Touch(b, PORT_1).get_sample()
print 'Sound:', Sound(b, PORT_2).get_sample()
print 'Light:', Light(b, PORT_3).get_sample()
print 'Ultrasonic:', Ultrasonic(b, PORT_4).get_sample()
