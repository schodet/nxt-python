#!/usr/bin/env python

import nxt.locator

s = nxt.locator.find_one_brick()
b = s.connect()
for box in range(10):
	b.message_write(box, 'message test %d' % box)
for box in range(10):
	local_box, message = b.message_read(box, box, True)
	print local_box, message
print 'Test succeeded!'
