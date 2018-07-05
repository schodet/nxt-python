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
    version='3.0',
    author='Elvin Luff',
    author_email='elvinluff@gmail.com',
    description='LEGO Mindstorms NXT Control Package',
    url='https://github.com/Eelviny/nxt-python/',
    license='Gnu GPL v3',
    packages=['nxt', 'nxt.sensor'],
    scripts=['scripts/nxt_push', 'scripts/nxt_test', 'scripts/nxt_server', 'scripts/nxt_filer'],
    long_description=ldesc
)
