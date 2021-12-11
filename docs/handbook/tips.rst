Tips and Tricks
===============

Make Bluetooth Connection Faster
--------------------------------

When looking for a NXT brick, the :mod:`~nxt.backend.bluetooth` backend will
first try to discover which device is available. If you know the Bluetooth
address of your brick, you can skip this step.

First connect to your brick to get its address::

    import nxt.locator
    with nxt.locator.find() as b:
        print(b.get_device_info()[0:2])

You should see something like::

    ('NXT', '00:16:53:01:02:03')

Now you can use the address in your programs::

    import nxt.locator
    with nxt.locator.find(host="00:16:53:01:02:03") as b:
        b.play_tone(440, 1000)

Or in your configuration::

    # .nxt-python.conf
    [default]
    host = 00:16:53:01:02:03


How to read inputs while controlling a motor?
---------------------------------------------

When using :meth:`!nxt.motor.Motor.turn`, NXT-Python is kept active while
watching the motor. If you need to read sensors at the same time, you can:

- use non blocking functions, like :meth:`nxt.motor.Motor.run`,
- use threads,
- or use :class:`nxt.motcont.MotCont`.
