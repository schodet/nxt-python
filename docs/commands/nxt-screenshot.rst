Manual page for nxt-screenshot
==============================

Synopsis
--------

**nxt-screenshot**
[**--backend** *NAME*]
[**--config** *NAME*]
[**--config-filename** *PATH*]
[**--name** *NAME*]
[**--host** *ADDRESS*]
[**--server-host** *HOST*]
[**--server-port** *PORT*]
[**--filename** *FILENAME*]
[**--log-level** *LEVEL*]
*FILE*

Description
-----------

:command:`nxt-screenshot` takes a capture of a connected NXT brick and write
the captured image to a *FILE*.

The NXT brick can be connected using USB, Bluetooth or over the network.

A wide range of image formats is supported, thanks to the Python Imaging
Library.


Options
-------

*FILE*
   Filename to write captured image to.

--log-level LEVEL
   Set the log level. One of **DEBUG**, **INFO**, **WARNING**, **ERROR**, or
   **CRITICAL**. Messages whose level is below the current log level will not
   be displayed.


.. include:: common_options.rst


Example
-------

``nxt-screenshot --host 00:16:53:01:02:03 capture.png``
   Capture screen from connected NXT using its Bluetooth address. Save the
   result image in ``capture.png``.


.. include:: common_see_also.rst
