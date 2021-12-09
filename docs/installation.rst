Installation
============

Install NXT-Python with :command:`pip`::

    python3 -m pip install --upgrade --pre nxt-python

As there is only pre-releases for the moment, you need the ``--pre`` option.
Without this option, an old NXT-Python version would be installed for
Python 2, which is no longer supported.

You can check that NXT-Python is correctly installed and can connect to your
NXT brick using::

    nxt_test

In case of problem, enable debugging for extra diagnostics::

    nxt_test --log-level=debug
