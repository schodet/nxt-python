Configuration files
===================

Description
-----------

The NXT-Python configuration files allow you to define the NXT bricks you want
to connect to, so that you do not need to give the needed argument for every
scripts.

You can place a :file:`.nxt-python.conf` in your home directory, or in the
current directory. You can also explicitly give configuration file name to the
invoked script or function.


Format
------

The configuration format is a INI-style format. It consists of several
sections introduced by the section name in square brackets on its line. Each
section contains a set of key/value pairs. The key and value are separated by
a equal sign ('=').

Configuration may include comments which are introduced by a '#' character.

When looking for a brick, you can request NXT-Python to use a specific
section, or :code:`[default]` if not specified. If the section is missing, or
if a value is missing, the :code:`[DEFAULT]` section (note the uppercase) is
used as a fallback.

The following values can be defined:

backends
   This is the space separated list of backends to use to find and connect to
   the brick. When not specified, a default list of backends is used:

   - :mod:`~nxt.backend.devfile` if :code:`filename` is given,
   - :mod:`~nxt.backend.socket` if :code:`server_host` or :code:`server_port`
     is given,
   - :mod:`~nxt.backend.usb` and,
   - :mod:`~nxt.backend.bluetooth`.

name
   Brick name which is used to find the brick (for example: NXT). The brick
   name can be configured using the NXT brick menus.

host
   Bluetooth address which is used to find the brick (for example:
   00:16:53:01:02:03). When using Bluetooth backend, this allows a direct
   connection without having to scan to find the brick. For other backends, it
   can be used to select the right brick when several bricks are found.

   The address can be found in the "Settings" menu, under "NXT Version"
   screen, it is the last line labeled "ID". Add the colon to separated each
   pair of digits.

server_host
   Server address or name (example: 192.168.1.3, or localhost).

   This is used by the :code:`socket` backend.

   .. only:: man

      The server is provided by the :manpage:`nxt-server(1)` command.

   .. only:: not man

      The server is provided by the :doc:`nxt-server </commands/nxt-server>`
      command.

server_port
   Server connection port (default: 2727).

   This is used by the :code:`socket` backend.

   .. only:: man

      The server is provided by the :manpage:`nxt-server(1)` command.

   .. only:: not man

      The server is provided by the :doc:`nxt-server </commands/nxt-server>`
      command.

filename
   Device file name (default is platform specific).

   This is used by the :mod:`~nxt.backend.devfile` backend to locate the
   RFCOMM device file.

   .. only:: man

      Please see NXT-Python documentation for more details on how to use this.

Other values
   Other values are passed as-is to backends.


Example
-------

Given the following configuration file:

.. code:: ini

   [DEFAULT]
   # Defines a fallback for every configuration name.
   backends = usb

   [default]
   # My default NXT, sitting on my desk.
   host = 00:16:53:01:02:03
   name = NXT

   [lab]
   # When working at the lab, use my second NXT.
   name = NXT2

   [robot]
   # Use Bluetooth for my third NXT, which is embedded in a robot, but try USB
   # first as this is faster.
   backends = usb bluetooth
   host = 00:16:53:aa:bb:cc
   name = ROBOT

When using the command line, NXT-Python will connect to my default NXT if I
do not give more options::

   $ nxt-test
   Finding brick...
   NXT brick name: NXT
   ...

I can request to connect to my robot NXT brick like this::

   $ nxt-test --config robot
   Finding brick...
   NXT brick name: ROBOT
   ...

Or when using a script:

.. code:: python

   import nxt.locator
   b = nxt.locator.find(config="robot")


Files
-----

:file:`$HOME/.nxt-python.conf`
   Per user configuration file.

:file:`.nxt-python.conf`
   Configuration file in current directory.


.. only:: man

   See also
   --------

   :manpage:`nxt-test(1)`

   NXT-Python documentation <https://ni.srht.site/nxt-python/latest/>
