Installation
============

Install NXT-Python with :command:`pip`::

    python3 -m pip install --upgrade nxt-python

To check that NXT-Python is correctly installed, connect your NXT brick using
a USB cable, and run::

    nxt_test

In case of problem, enable debugging for extra diagnostics::

    nxt_test --log-level=debug


USB
---

USB support is provided by PyUSB which is installed automatically with
NXT-Python. You can also use the package from your Linux distribution if you
wish, in this case, install it before installing NXT-Python.

PyUSB requires libusb or OpenUSB running on your system.

- For Linux users, you can install it from your package manager if not
  installed yet.
- For MacOS users, you can use ``brew install libusb`` to install it using
  Homebrew.
- For Windows users, libusb 1.0 DLLs are provided in the releases. Check the
  `PyUSB FAQ`_.

.. _PyUSB FAQ: https://github.com/pyusb/pyusb/blob/master/docs/faq.rst#how-do-i-install-libusb-on-windows


USB access permissions for Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You need to allow connection to the NXT brick for your user. If you install
any package interacting with the NXT brick from your distribution, this is
usually already done for you (for example, nbc, or libnxt).

In other cases, copy `contrib/60-libnxt.rules` from the NXT-Python source
distribution to your `/etc/udev/rules.d` directory, then make sure that udev
see the change: restart your computer or use the following commands::

    sudo udevadm control --reload
    sudo udevadm trigger


Bluetooth
---------

NXT-Python is only installed with USB by default, you need to install
Bluetooth support explicitly.


Installation from Linux Distribution Package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The easiest solution is to install PyBluez from your distribution.

On Debian based distributions, like Ubuntu::

    apt install python3-bluez

On ArchLinux::

    pacman -S python-pybluez

On Fedora::

    dnf install python3-bluez


Installation Using Pip
^^^^^^^^^^^^^^^^^^^^^^

You can install PyBluez using :command:`pip`. This is easy if there is a
pre-build package for your system and python version. This is much harder if
this is not the case.

Try this::

    python3 -m pip install PyBluez
