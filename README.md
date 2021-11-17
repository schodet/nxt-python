# ![NXT-Python](./logo.svg)

**The NXT-Python v3 implementation is incomplete, but this is currently being
worked on. Stay tuned!**

NXT-Python is a package for controlling a LEGO NXT robot using the Python
programming language. It can communicate using either USB or Bluetooth. It is
based on Elvin Luff's work ending in 2021, based on Marcus Wanner's work
until 2013, which in turn is based on NXT\_Python, where releases halted in
May 2007.

## Requirements

- [Python 3.x](http://www.python.org)
- Bluetooth Communications:
    - [PyBluez](https://github.com/pybluez/pybluez)
- USB Communications:
    - [PyUSB](https://github.com/pyusb/pyusb)

## Installation

1. There is no release for Python 3 for the moment, please clone the master
   branch from [the repository](https://github.com/schodet/nxt-python).
2. Navigate to the package directory, and run `python3 setup.py install`
3. `import nxt` in your program and get going!

This is a quick overview, detailed instructions can be found on the
[wiki](https://github.com/schodet/nxt-python/wiki/Installation) page.

### Converting between versions

Since the 3.x and 2.x series use the same API, in most cases code can be
automatically converted. Python 2 and Python 3 include a built in
[2to3](https://docs.python.org/2/library/2to3.html) script which will
automatically modify the program.

## Contact

NXT-Python repository maintainer: [schodet](https://github.com/schodet) - New
maintainer since 2021-11-06, currently working on a first release for Python 3.

[Github issues page](https://github.com/schodet/nxt-python/issues): Send all
questions, bugs and requests here!

Please read the [issue
rules](https://github.com/schodet/nxt-python/wiki/Issue-Rules) before posting
here.

## Thanks to:

- Doug Lau for writing NXT\_Python, our starting point.
- rhn for creating what would become v2, making lots of smaller changes, and
  reviewing tons of code.
- Marcus Wanner for maintaining NXT-Python up to v2.2.2, his work has been
  amazing!
- Elvin Luff for taking over the project after Marcus, making a lot of work
  for the port to Python 3.
- mindsensors.com (esp. Ryan Kneip) for helping out with the code for a lot of
  their sensors, expanding the sensors covered by the type checking database,
  and providing hardware for testing.
- HiTechnic for providing identification information for their sensors. I note
  that they have now included this information in their website. ;)
- Linus Atorf, Samuel Leeman-Munk, melducky, Simon Levy, Steve Castellotti,
  Paulo Vieira, zonedabone, migpics, TC Wan, jerradgenson, henryacev, Paul
  Hollensen, and anyone else I forgot for various fixes and additions.
- Goldsloth for making some useful changes and keeping the tickets moving
  after the migration to Github.
- All our users for their interest and support!
