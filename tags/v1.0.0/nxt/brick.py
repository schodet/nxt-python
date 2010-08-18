# nxt.brick module -- Classes to represent LEGO Mindstorms NXT bricks
# Copyright (C) 2006  Douglas P Lau
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

from time import sleep
from nxt.error import FileNotFound, ModuleNotFound
from nxt.telegram import OPCODES, Telegram

def _make_poller(opcode, poll_func, parse_func):
	def poll(self, *args, **kwargs):
		ogram = poll_func(opcode, *args, **kwargs)
		self.sock.send(str(ogram))
		igram = Telegram(opcode=opcode, pkt=self.sock.recv())
		return parse_func(igram)
	return poll

class _Meta(type):
	'Metaclass which adds one method for each telegram opcode'

	def __init__(cls, name, bases, dict):
		super(_Meta, cls).__init__(name, bases, dict)
		for opcode in OPCODES:
			poll_func, parse_func = OPCODES[opcode]
			m = _make_poller(opcode, poll_func, parse_func)
			setattr(cls, poll_func.__name__, m)

class Brick(object):
        'Main object for NXT Control'

	__metaclass__ = _Meta

	def __init__(self, sock):
		self.sock = sock

	def play_tone_and_wait(self, frequency, duration):
		self.play_tone(frequency, duration)
		sleep(duration / 1000.0)

class FileFinder(object):
	'Context manager to find files on a NXT brick'

	def __init__(self, brick, pattern):
		self.brick = brick
		self.pattern = pattern
		self.handle = None

	def __enter__(self):
		return self

	def __exit__(self, etp, value, tb):
		if self.handle:
			self.brick.close(self.handle)

	def __iter__(self):
		self.handle, fname, size = self.brick.find_first(self.pattern)
		yield (fname, size)
		while True:
			try:
				handle, fname, size = self.brick.find_next(
					self.handle)
				yield (fname, size)
			except FileNotFound:
				break

class FileReader(object):
	'Context manager to read a file on a NXT brick'

	def __init__(self, brick, fname):
		self.brick = brick
		self.fname = fname

	def __enter__(self):
		self.handle, self.size = self.brick.open_read(self.fname)
		return self

	def __exit__(self, etp, value, tb):
		self.brick.close(self.handle)

	def __iter__(self):
		rem = self.size
		bsize = self.brick.sock.bsize
		while rem > 0:
			handle, bsize, data = self.brick.read(self.handle,
				min(bsize, rem))
			yield data
			rem -= len(data)

class FileWriter(object):
	'Context manager to write a file to a NXT brick'

	def __init__(self, brick, fname, fil):
		self.brick = brick
		self.fname = fname
		self.fil = fil
		fil.seek(0, 2)	# seek to end of file
		self.size = fil.tell()
		fil.seek(0)	# seek to start of file

	def __enter__(self):
		self.handle = self.brick.open_write(self.fname, self.size)
		return self

	def __exit__(self, etp, value, tb):
		self.brick.close(self.handle)

	def __iter__(self):
		rem = self.size
		bsize = self.brick.sock.bsize
		while rem > 0:
			b = min(bsize, rem)
			handle, size = self.brick.write(self.handle,
				self.fil.read(b))
			yield size
			rem -= b

class ModuleFinder(object):
	'Context manager to lookup modules on a NXT brick'

	def __init__(self, brick, pattern):
		self.brick = brick
		self.pattern = pattern
		self.handle = None

	def __enter__(self):
		return self

	def __exit__(self, etp, value, tb):
		if self.handle:
			self.brick.close(self.handle)

	def __iter__(self):
		self.handle, mname, mid, msize, miomap_size = \
			self.brick.request_first_module(self.pattern)
		yield (mname, mid, msize, miomap_size)
		while True:
			try:
				handle, mname, mid, msize, miomap_size = \
					self.brick.request_next_module(
					self.handle)
				yield (mname, mid, msize, miomap_size)
			except ModuleNotFound:
				break
