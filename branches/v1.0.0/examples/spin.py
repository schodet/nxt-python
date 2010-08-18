#!/usr/bin/env python

import nxt.locator
from nxt.motor import *

def spin_around(b):
	m_left = Motor(b, PORT_B)
	m_left.update(100, 360)
	m_right = Motor(b, PORT_C)
	m_right.update(-100, 360)

sock = nxt.locator.find_one_brick()
if sock:
	spin_around(sock.connect())
	sock.close()
else:
	print 'No NXT bricks found'
