#!/usr/bin/env python

from distutils.core import setup

try:
    readme = open('README', 'r')
    ldesc = readme.read(20000)
    readme.close()
except:
    ldesc = ""

setup(
    name='nxt-python',
    version='2.2',
    author='Marcus Wanner',
    author_email='marcus@wanners.net',
    description='LEGO Mindstorms NXT Control Package',
    url='http://code.google.com/p/nxt-python/',
    license='Gnu GPL v3',
    packages=['nxt', 'nxt.sensor'],
    scripts=['scripts/nxt_push', 'scripts/nxt_test', 'scripts/nxt_filer', 'scripts/nxt_server'],
    long_description=ldesc
)
