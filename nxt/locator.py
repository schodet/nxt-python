# nxt.locator module -- Locate LEGO Minstorms NXT bricks via USB or Bluetooth
# Copyright (C) 2006-2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
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

class BrickNotFoundError(Exception):
	pass

def find_bricks(host=None, name=None):
        'Used by find_one_brick to look for bricks ***ADVANCED USERS ONLY***'
	try:
		import usbsock
		socks = usbsock.find_bricks(host, name)
		for s in socks:
			yield s
	except ImportError:
		pass
	try:
		import bluesock
		from bluetooth import BluetoothError
		try:
			socks = bluesock.find_bricks(host, name)
			for s in socks:
				yield s
		except BluetoothError:
			pass
	except ImportError:
		pass

def find_one_brick(host=None, name=None):
        'Use to find one brick. After it returns a usbsock object or a bluesock object, use .connect() to connect to the brick, which returns a brick object.'
	for s in find_bricks(host, name):
		return s
	raise BrickNotFoundError
