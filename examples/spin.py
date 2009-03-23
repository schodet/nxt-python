#!/usr/bin/env python

import nxt.locator
from nxt.motor import *

def spin_around(b):
	m_left = Motor(b, PORT_B)
	m_left.power = 50
	m_left.mode = MODE_MOTOR_ON
	m_left.run_state = RUN_STATE_RUNNING
	m_left.tacho_limit = 360
	m_left.set_output_state()
	m_right = Motor(b, PORT_C)
	m_right.power = -50
	m_right.mode = MODE_MOTOR_ON
	m_right.run_state = RUN_STATE_RUNNING
	m_right.tacho_limit = 360
	m_right.set_output_state()

sock = nxt.locator.find_one_brick()
if sock:
	spin_around(sock.connect())
	sock.close()
else:
	print 'No NXT bricks found'
