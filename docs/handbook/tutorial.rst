Tutorial
========

First, make sure that NXT-Python is installed correctly, see
:doc:`/installation`.

This is not a Python tutorial, you must know how to program using Python to
use NXT-Python.

First step when writing a NXT-Python script is to find the brick.  This is the
role of the :func:`nxt.locator.find` function:

.. literalinclude:: ../../examples/tutorial/find.py

Once the brick is found, the :func:`nxt.locator.find` function returns an
object to interact with it: the :class:`~nxt.brick.Brick` object. Here the
script query device information and play a tone.

Now something a little bit more interesting, plug a motor on the port A and
try the following script:

.. literalinclude:: ../../examples/tutorial/motor.py

Try changing the parameters and see what happen. You can of course drive
several motors, just use the :func:`~nxt.brick.Brick.get_motor` function for
each one.

You can also get information from sensors:

.. literalinclude:: ../../examples/tutorial/sensor_us.py

Digital sensors can be automatically detected as long as the corresponding
module is loaded. In the retail set, only the ultra-sound distance sensor is
digital, all the other sensors are analog. When using an analog sensor, you
must give the sensor class explicitly:

.. literalinclude:: ../../examples/tutorial/sensor_touch.py

If you run into problems, you can increase the log level. NXT-Python is using
the :mod:`logging` module from the standard Python distribution. Try this
script:

.. literalinclude:: ../../examples/tutorial/debug.py

You should now have enough information to start playing with NXT-Python. See
the :doc:`/api/index`, or the :doc:`/handbook/tips` pages for more informations.
