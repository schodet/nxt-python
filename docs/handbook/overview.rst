Overview
========

Using NXT-Python, you can control one or several NXT bricks from your
computer. The program you write is running on your computer, not on the NXT
brick, so the computer must be able to communicate with the brick during the
whole program lifetime.

Communication is done through USB or Bluetooth. You can also relay
communication over the network through another computer running the
:command:`nxt_server` program which is part of NXT-Python.


The Brick Object
----------------

All interaction with the NXT brick is done using the :class:`~nxt.brick.Brick`
class. You will first have to find a brick using the :func:`nxt.locator.find`
function which will return an instance of this class.

The :class:`~nxt.brick.Brick` object have functions to access the brick
capabilities. There is a function for every low level system and direct
command exposed by the NXT brick.

There are also higher level functions to access the brick file system for
example.

You could do everything just using low level functions, but to access motors
and sensors, you will likely prefer to use the motors and sensors objects.


Motor Control
-------------

You can make an instance of the :class:`~nxt.motor.Motor` class for each
connected motor. This allows to control the motors with a nicer interface than
using the low level function.

Keep in mind that as the program is running on your computer, there can be a
delay which will reduce the motor control precision. To solve this problem,
you can use the :class:`~nxt.motcont.MotCont` class which cooperates with a
program running on the NXT brick to allow fine control.

The situation could be improved by using an improved firmware for the NXT
brick, but this is not supported yet.


Sensors
-------

Many different sensors can be connected to the NXT brick. This is supported in
NXT-Python thanks to the :mod:`~nxt.sensor` classes hierarchy. There is a
class for every LEGO official sensor, and also classes for HiTechnic and
Mindsensors sensors.

If your sensor is not supported, please contribute its support!
