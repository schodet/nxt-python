Manual page for nxt-server
==========================

Synopsis
--------

**nxt-server**
[**--backend** *NAME*]
[**--config** *NAME*]
[**--config-filename** *PATH*]
[**--name** *NAME*]
[**--host** *ADDRESS*]
[**--server-host** *HOST*]
[**--server-port** *PORT*]
[**--filename** *FILENAME*]
[**-p|--port** *PORT*]
[**--log-level** *LEVEL*]

Description
-----------

:command:`nxt-server` serves an interface to a connected NXT brick over the
network.

The NXT brick can be connected using USB, Bluetooth or over the network.


Options
-------

-p|--port *PORT*
   Set the bind port. Same value must be given to the client using
   **--server-port** or inside Python code. Default port is 2727.

--log-level LEVEL
   Set the log level. One of **DEBUG**, **INFO**, **WARNING**, **ERROR**, or
   **CRITICAL**. Messages whose level is below the current log level will not
   be displayed.


.. include:: common_options.rst

Example
-------

``nxt-server --host 00:16:53:01:02:03``
   Starting the server on a computer connected to a NXT brick, accepting
   connection on default port 2727.

``nxt-test --server-host 192.168.1.2``
   Assuming the first computer has address 192.168.1.2, remotely connect to
   the server to run a test.


.. include:: common_see_also.rst
