#!/usr/bin/env python

import time
import nxt.locator
from nxt.sensor import *

b = nxt.locator.find_one_brick()

#Touch sensor latency test
touch = Touch(b, PORT_1)
start = time.time()
for i in range(100):
    touch.get_sample()
stop = time.time()
print 'touch latency: %s ms' % (1000 * (stop - start) / 100.0)

#Ultrasonic sensor latency test
ultrasonic = Ultrasonic(b, PORT_4)
start = time.time()
for i in range(100):
    ultrasonic.get_sample()
stop = time.time()
print 'ultrasonic latency: %s ms' % (1000 * (stop - start) / 100.0)
