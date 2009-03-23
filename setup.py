#!/usr/bin/env python

from distutils.core import setup

setup(
	name='NXT_Master',
	version='0.7',
	author='Douglas Lau',
	author_email='dplau@comcast.net',
	description='LEGO Mindstorms NXT Control Package',
	packages=['nxt'],
	scripts=['scripts/nxt_push', 'scripts/nxt_test', 'scripts/nxt_filer']
)
