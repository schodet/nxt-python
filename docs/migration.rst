Migrating to 3.0
================

If you have a working program using NXT-Python 2, you will have to make
changes to port it to NXT-Python 3.


Porting to Python 3
-------------------

First of all you need to port your code to Python 3, there is an `guide`_ in
Python documentation. You do not need to worry about keeping the code
compatible with Python 2 as it is no longer supported.

There is also an automatic script to ease the porting, called `2to3`_.

.. _guide: https://docs.python.org/3/howto/pyporting.html
.. _2to3: https://docs.python.org/3/library/2to3.html

One major change in Python is the distinction between text string
(:class:`str`) and binary string (:class:`bytes`). This means that you need to
make sure to use the right one when passing arguments to NXT-Python functions.


Porting to NXT-Python 3
-----------------------

Next step is to adapt the code for NXT-Python.


Major Changes
^^^^^^^^^^^^^

The :func:`!nxt.locator.find_one_brick` function has been removed and replaced
with the simpler :func:`nxt.locator.find` function. Actually, the whole
:mod:`nxt.locator` has been replaced.

Many `debug` arguments have been removed, now NXT-Python uses the
:mod:`logging` module to log messages. If you want to enable debug messages,
use this code before calling any NXT-Python function::

    import logging
    logging.basicConfig(level=logging.DEBUG)

The :mod:`!nxt` and :mod:`nxt.sensor` modules no longer exports name from
sub-modules. In general, NXT-Python now avoids to have two names for the same
object.

Output port constants are replaced by enumerations, using the :mod:`enum`
module:

.. py:currentmodule:: nxt.motor

===============================  ============================
NXT-Python 2                     NXT-Python 3
===============================  ============================
:data:`!PORT_A`                  :attr:`Port.A`
:data:`!PORT_B`                  :attr:`Port.B`
:data:`!PORT_C`                  :attr:`Port.C`
:data:`!MODE_IDLE`               :attr:`Mode.IDLE`
:data:`!MODE_MOTOR_ON`           :attr:`Mode.ON`
:data:`!MODE_BRAKE`              :attr:`Mode.BRAKE`
:data:`!MODE_REGULATED`          :attr:`Mode.REGULATED`
:data:`!REGULATION_IDLE`         :attr:`RegulationMode.IDLE`
:data:`!REGULATION_MOTOR_SPEED`  :attr:`RegulationMode.SPEED`
:data:`!REGULATION_MOTOR_SYNC`   :attr:`RegulationMode.SYNC`
:data:`!RUN_STATE_IDLE`          :attr:`RunState.IDLE`
:data:`!RUN_STATE_RAMP_UP`       :attr:`RunState.RAMP_UP`
:data:`!RUN_STATE_RUNNING`       :attr:`RunState.RUNNING`
:data:`!RUN_STATE_RAMP_DOWN`     :attr:`RunState.RAMP_DOWN`
===============================  ============================

You can now create :class:`nxt.motor.Motor` objects using
:meth:`nxt.brick.Brick.get_motor`, however direct creation still works.

Input port constants are replaced by enumerations, using the :mod:`enum`
module. The :mod:`!nxt.sensor.common` module has been removed, its content is
directly available in :mod:`nxt.sensor`:

.. py:currentmodule:: nxt.sensor

===============================  ============================
NXT-Python 2                     NXT-Python 3
===============================  ============================
:data:`!PORT_1`                  :attr:`Port.S1`
:data:`!PORT_2`                  :attr:`Port.S2`
:data:`!PORT_3`                  :attr:`Port.S3`
:data:`!PORT_4`                  :attr:`Port.S4`
:attr:`!Type.NO_SENSOR`          :attr:`Type.NO_SENSOR`
:attr:`!Type.SWITCH`             :attr:`Type.SWITCH`
:attr:`!Type.TEMPERATURE`        :attr:`Type.TEMPERATURE`
:attr:`!Type.REFLECTION`         :attr:`Type.REFLECTION`
:attr:`!Type.ANGLE`              :attr:`Type.ANGLE`
:attr:`!Type.LIGHT_ACTIVE`       :attr:`Type.LIGHT_ACTIVE`
:attr:`!Type.LIGHT_INACTIVE`     :attr:`Type.LIGHT_INACTIVE`
:attr:`!Type.SOUND_DB`           :attr:`Type.SOUND_DB`
:attr:`!Type.SOUND_DBA`          :attr:`Type.SOUND_DBA`
:attr:`!Type.CUSTOM`             :attr:`Type.CUSTOM`
:attr:`!Type.LOW_SPEED`          :attr:`Type.LOW_SPEED`
:attr:`!Type.LOW_SPEED_9V`       :attr:`Type.LOW_SPEED_9V`
:attr:`!Type.HIGH_SPEED`         :attr:`Type.HIGH_SPEED`
:attr:`!Type.COLORFULL`          :attr:`Type.COLOR_FULL`
:attr:`!Type.COLORRED`           :attr:`Type.COLOR_RED`
:attr:`!Type.COLORGREEN`         :attr:`Type.COLOR_GREEN`
:attr:`!Type.COLORBLUE`          :attr:`Type.COLOR_BLUE`
:attr:`!Type.COLORNONE`          :attr:`Type.COLOR_NONE`
:attr:`!Type.COLOREXIT`          :attr:`Type.COLOR_EXIT`
:attr:`!Mode.RAW`                :attr:`Mode.RAW`
:attr:`!Mode.BOOLEAN`            :attr:`Mode.BOOL`
:attr:`!Mode.TRANSITION_CNT`     :attr:`Mode.EDGE`
:attr:`!Mode.PERIOD_COUNTER`     :attr:`Mode.PULSE`
:attr:`!Mode.PCT_FULL_SCALE`     :attr:`Mode.PERCENT`
:attr:`!Mode.CELSIUS`            :attr:`Mode.CELSIUS`
:attr:`!Mode.FAHRENHEIT`         :attr:`Mode.FAHRENHEIT`
:attr:`!Mode.ANGLE_STEPS`        :attr:`Mode.ROTATION`
:attr:`!Mode.MASK`               Removed
:attr:`!Mode.MASK_SLOPE`         Removed
===============================  ============================

You can now create :mod:`~nxt.sensor` objects using
:meth:`nxt.brick.Brick.get_sensor`, however direct creation still works. For
digital sensors with identification information, this can automatically detect
the sensor type as with previous version. The new `cls` argument allows
creating a sensor object using another class.


Text String or Binary String
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The NXT brick only understands ASCII, so this is the default encoding used in
NXT-Python.

From :class:`nxt.brick.Brick`:

.. py:currentmodule:: nxt.brick

- :meth:`~Brick.get_device_info` now returns a :class:`str` for the brick
  name.
- :meth:`~Brick.file_write`, :meth:`~Brick.write_io_map` and
  :meth:`~Brick.message_write` now take :class:`bytes` instead of a
  :class:`str`.
- :meth:`~Brick.file_read`, :meth:`~Brick.read_io_map` and
  :meth:`~Brick.poll_command` no longer return the read size, but the returned
  :class:`bytes` object is cut to the right size.
- :meth:`~Brick.get_current_program_name` returns a :class:`str`.
- :meth:`~Brick.file_delete` is fixed and returns a :class:`str`.
- :meth:`~Brick.find_files` and :meth:`~Brick.find_modules` use :class:`str`
  for file and module names.


File Access
^^^^^^^^^^^

File reading and writing are now implemented using classes implementing
:class:`io.RawIOBase`. When using :meth:`~nxt.brick.Brick.open_file`,
depending of the parameters, the raw file-like object is returned directly, or
wrapped in a :class:`io.BufferedIOBase` or :class:`io.TextIOBase` object.

Default access mode is now text with ASCII encoding, you need to ask
explicitly for binary if needed.

This means that file access should be similar to regular Python file access.


Renamed
^^^^^^^

From :class:`nxt.brick.Brick`:

.. py:currentmodule:: nxt.brick

- :meth:`!delete` has been renamed to :meth:`~Brick.file_delete`.
- Many low level file and module access methods now have a ``file_`` or
  ``module_`` prefix. They are however not supposed to be used directly.

From :mod:`nxt.error`:

.. py:currentmodule:: nxt.error

- :exc:`!DirProtError` and :exc:`!SysProtError` have been renamed to
  :exc:`DirectProtocolError` and :exc:`SystemProtocolError`.
- :exc:`!FileNotFound` has been renamed to :exc:`FileNotFoundError`.
- :exc:`!ModuleNotFound` has been renamed to :exc:`ModuleNotFoundError`.

Sensors:

- :class:`!nxt.sensor.generic.Color20` has been renamed to
  :class:`nxt.sensor.generic.Color`.


Removed
^^^^^^^

Some attributes are now private (prefixed with ``_``).

Support for the lightblue module has been removed. It has been integrated into
`PyBluez`_.

.. _PyBluez: https://github.com/pybluez/pybluez

From :mod:`nxt.brick`:

.. py:currentmodule:: nxt.brick

- :meth:`!Brick.open_read_linear` has been removed, it has never been
  accessible from outside the NXT brick.
- :class:`!File`, :class:`!FileReader` and :class:`!FileWriter` have been
  removed, use :meth:`Brick.open_file`.
- :class:`!FileFinder` has been removed, use :meth:`Brick.find_files`.
- :class:`!ModuleFinder` has been removed, use :meth:`Brick.find_modules`.
- :attr:`!Brick.mc` has been removed, make an instance using::

    mc = nxt.motcont.MotCont(the_brick)

From other modules:

- :meth:`!nxt.motcont.MotCont.move_to` has been removed as it is not part of
  `MotorControl` interface and its role was not clear.
- :exc:`!nxt.motcont.MotorConError` has been removed and replaced with
  :exc:`nxt.error.ProtocolError`.
- :exc:`!nxt.telegram.InvalidReplyError` and
  :exc:`!nxt.telegram.InvalidOpcodeError` have been removed and replaced with
  :exc:`nxt.error.ProtocolError`.

Module :mod:`!nxt.utils` has been removed, use :mod:`argparse`.


Other Changes
^^^^^^^^^^^^^

From :class:`nxt.brick.Brick`:

.. py:currentmodule:: nxt.brick

- :meth:`~Brick.get_device_info` returns a tuple for the Bluetooth signal
  strength values instead of a single 32 bit value.
- :meth:`~Brick.find_files` and :meth:`~Brick.find_modules` return an empty
  iterator instead of raising an exception when no file or module is found.
- :meth:`~Brick.close` now closes the connection to the NXT brick. Also
  :class:`Brick` now implements the context manager interface so that it can
  be used with the ``with`` syntax.
- :meth:`~Brick.boot` now takes a argument to avoid accidental firmware
  erasure.

Other:

- :class:`nxt.motcont.MotCont` methods accept tuple as argument to control
  several ports.
- Scripts command line interface has changed.
