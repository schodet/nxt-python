#!/usr/bin/env python

import time
import nxt.locator
from nxt.sensor import *

def time_touch(b):
	touch = TouchSensor(b, PORT_1)
	start = time.time()
	for i in range(100):
		touch.get_sample()
	stop = time.time()
	print 'touch latency: %d ms' % (1000 * (stop - start) / 100.)

def time_ultrasonic(b):
	ultrasonic = UltrasonicSensor(b, PORT_4)
	start = time.time()
	for i in range(100):
		ultrasonic.get_sample()
	stop = time.time()
	print 'ultrasonic latency: %d ms' % (1000 * (stop - start) / 100.)

sock = nxt.locator.find_one_brick()
if sock:
	b = sock.connect()
	time_touch(b)
	time_ultrasonic(b)
	sock.close()
else:
	print 'No NXT bricks found'
