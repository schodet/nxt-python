#!/usr/bin/env python

from distutils.core import setup

setup(
	name='NXT-Python',
	version='0.7',
	author='Douglas Lau, Marcus Wanner',
	author_email='dplau@comcast.net, marcusw@cox.net',
	description='LEGO Mindstorms NXT Control Package',
	packages=['nxt'],
	scripts=['scripts/nxt_push', 'scripts/nxt_test', 'scripts/nxt_filer']
)
