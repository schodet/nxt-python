Manual page for nxt-test
========================

Synopsis
--------

**nxt-test**
[**--backend** *NAME*]
[**--config** *NAME*]
[**--config-filename** *PATH*]
[**--name** *NAME*]
[**--host** *ADDRESS*]
[**--server-host** *HOST*]
[**--server-port** *PORT*]
[**--filename** *FILENAME*]
[**--no-sound**]
[**--log-level** *LEVEL*]

Description
-----------

:command:`nxt-test` tests connection with a NXT brick. It allows to debug the
NXT-Python setup.

The NXT brick can be connected using USB, Bluetooth or over the network.


Options
-------

--no-sound
   Be quiet, disable the sound test.

--log-level LEVEL
   Set the log level. One of **DEBUG**, **INFO**, **WARNING**, **ERROR**, or
   **CRITICAL**. Messages whose level is below the current log level will not
   be displayed.


.. include:: common_options.rst

Examples
--------

Running for a NXT brick connected using USB::

   $ nxt-test
   Finding brick...
   NXT brick name: NXT
   Host address: 00:16:53:01:02:03
   Bluetooth signal strengths: (0, 0, 0, 0)
   Free user flash: 48480
   Protocol version 1.124
   Firmware version 1.29
   Battery level 8433 mV
   Play test sound...done

To report problems, please enable debug logs::

   $ nxt-test --log-level DEBUG

When debugging Bluetooth connection problems, try to give the address
explicitly::

   $ nxt-test --log-level DEBUG --host 00:16:53:01:02:03

The address can be found in the "Settings" menu, under "NXT Version" screen,
it is the last line labeled "ID". Add the colon to separate each pair of
digits.


.. include:: common_see_also.rst
