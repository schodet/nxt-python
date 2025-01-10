Common options
--------------

Those options are common to programs using NXT-Python.

--backend NAME
   Enable given backend. Can be used several times to enable several backends.
   One of :mod:`~nxt.backend.usb`, :mod:`~nxt.backend.bluetooth`,
   :mod:`~nxt.backend.socket` or :mod:`~nxt.backend.devfile`.

--config NAME
   Name of configuration file section to use.

--config-filename PATH
   Path to configuration file. Can be used several times to use several
   configuration files.

--name NAME
   Name of NXT brick (for example: NXT). Useful to find the right brick if
   several bricks are connected.

--host ADDRESS
   Bluetooth address of the NXT brick (for example: 00:16:53:01:02:03).

--server-host HOST
   Server address or name to connect to when using :mod:`~nxt.backend.socket`
   backend.

--server-port PORT
   Server port to connect to when using :mod:`~nxt.backend.socket` backend.

--filename FILENAME
   Device filename (for example: :file:`/dev/rfcomm0`), when using
   `~nxt.backend.devfile` backend.
