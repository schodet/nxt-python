Manual page for nxt-push
========================

Synopsis
--------

**nxt-push**
[**--backend** *NAME*]
[**--config** *NAME*]
[**--config-filename** *PATH*]
[**--name** *NAME*]
[**--host** *ADDRESS*]
[**--server-host** *HOST*]
[**--server-port** *PORT*]
[**--filename** *FILENAME*]
[**--log-level** *LEVEL*]
*FILE*...

Description
-----------

:program:`nxt-push` uploads files to a connected NXT brick file system.

The NXT brick can be connected using USB, Bluetooth or over the network.


Options
-------

*FILE*...
   Names of files to send to the NXT brick.

--log-level LEVEL
   Set the log level. One of **DEBUG**, **INFO**, **WARNING**, **ERROR**, or
   **CRITICAL**. Messages whose level is below the current log level will not
   be displayed.


.. include:: common_options.rst


Example
-------

``nxt-push --host 00:16:53:01:02:03 MotorControl22.rxe``
   Sends the ``MotorControl22.rxe`` file to a connected NXT using its
   Bluetooth address to find it.


.. include:: common_see_also.rst
