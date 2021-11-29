# nxt.locator module -- Locate LEGO Mindstorms NXT bricks
# Copyright (C) 2006, 2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
# Copyright (C) 2013  Dave Churchill, Marcus Wanner
# Copyright (C) 2015, 2016, 2017, 2018 Multiple Authors
# Copyright (C) 2021  Nicolas Schodet
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import configparser
import logging
import os

logger = logging.getLogger(__name__)

class BrickNotFoundError(Exception):
    pass


class NoBackendError(Exception):
    pass


class Method():
    """Used to indicate which comm backends should be tried by find_bricks/
find_one_brick. Any or all can be selected."""
    def __init__(self, usb=True, bluetooth=True, device=False):
        #new method options MUST default to False!
        self.usb = usb
        self.bluetooth = bluetooth
        self.device = device


def find_bricks(host=None, name=None, method=Method()):
    """Used by find_one_brick to look for bricks ***ADVANCED USERS ONLY***"""
    methods_available = 0

    if method.usb:
        try:
            import nxt.backend.usb
            backend = nxt.backend.usb.get_backend()
            methods_available += 1
            socks = backend.find()
            for s in socks:
                yield s
        except ImportError:
            logging.warning("usb module unavailable, not searching there")

    if method.bluetooth:
        try:
            import nxt.backend.bluetooth
            backend = nxt.backend.bluetooth.get_backend()
            if backend is not None:
                methods_available += 1
                try:
                    socks = backend.find(host=host, name=name)
                    for s in socks:
                        yield s
                # For cases such as no adapter, bluetooth throws IOError, not BluetoothError.
                except (backend._bluetooth.BluetoothError, IOError):
                    pass
        except ImportError:
            logging.warning("bluetooth module unavailable, not searching there")

    if method.device:
        try:
            import nxt.backend.devfile
            backend = nxt.backend.devfile.get_backend()
            methods_available += 1
            socks = backend.find(name=name)
            for s in socks:
                yield s
        except IOError:
            pass

    if methods_available == 0:
        raise NoBackendError("No selected backends are available! Did you install the comm modules?")


def find_one_brick(host=None, name=None, strict=None, method=None, confpath=None):
    """Use to find one brick. The host and name args limit the search to
a given MAC or brick name. This function by default
automatically checks to see if the brick found has the correct host/name
(if either are provided) and will not return a brick which doesn't
match. This can be disabled (so the function returns any brick which can
be connected to and provides a valid reply to get_device_info()) by
passing strict=False. This will, however, still tell the comm backends
to only look for devices which match the args provided. The confpath arg
specifies the location of the configuration file which brick location
information will be read from if no brick location directives (host,
name, strict, or method) are provided."""
    conf = read_config(confpath)
    if not (host or name or strict or method):
        host	= conf.get('Brick', 'host')
        name	= conf.get('Brick', 'name')
        strict	= bool(int(conf.get('Brick', 'strict')))
        method_value = conf.get('Brick', 'method')
        if method_value:
            methods = map(lambda x: x.strip().split('='),
                          method_value.split(','))
            method = Method(**{k: v == 'True' for k, v in methods
                               if k in ('bluetooth', 'usb', 'device')})
    if not strict: strict = True
    if not method: method = Method()

    logger.debug("host: %s name: %s strict: %s", host, name, strict)
    logger.debug("usb: %s bt: %s", method.usb, method.bluetooth)

    for s in find_bricks(host, name, method):
        try:
            b = s.connect()
            info = b.get_device_info()
            logger.debug("info: %s", info)

            strict = False

            if host and info[1] != host:
                logger.warning("the brick found does not match the host provided (get_device_info)")
                logger.warning("  host: %s", host)
                logger.warning("  info[1]: %s", info[1])
                if strict:
                    s.close()
                    continue

            if name and info[0] != name:
                logger.warning("the brick found does not match the name provided")
                logger.warning("  host: %s", host)
                logger.warning("  info[0]: %s", info[0])
                logger.warning("  name: %s", name)
                if strict:
                    s.close()
                    continue

            return b
        except:
            logger.debug("failed to connect to possible brick", exc_info=True)

    logger.warning("no brick was found, is the brick turned on?")
    raise BrickNotFoundError


def server_brick(host, port=2727):
    import nxt.backend.socket
    sock = nxt.backend.socket.SocketSock(host, port)
    return sock.connect()


def device_brick(filename):
    import nxt.backend.devfile
    backend = nxt.backend.devfile.get_backend()
    for sock in backend.find(filename=filename):
        return sock.connect()


def read_config(confpath=None):
    conf = configparser.RawConfigParser({'host': None, 'name': None, 'strict': True, 'method': ''})
    if not confpath: confpath = os.path.expanduser('~/.nxt-python')
    if conf.read([confpath]) == []:
        logger.debug("config file (should be at %s) was not read", confpath)
    if conf.has_section('Brick') == False:
        conf.add_section('Brick')
    return conf


def make_config(confpath=None):
    conf = configparser.RawConfigParser()
    if not confpath: confpath = os.path.expanduser('~/.nxt-python')
    print("Welcome to the nxt-python config file generator!")
    print("This function creates an example file which find_one_brick uses to find a brick.")
    try:
        if os.path.exists(confpath): input("File already exists at %s. Press Enter to overwrite or Ctrl+C to abort." % confpath)
    except KeyboardInterrupt:
        print("Not writing file.")
        return
    conf.add_section('Brick')
    conf.set('Brick', 'name', 'MyNXT')
    conf.set('Brick', 'host', '54:32:59:92:F9:39')
    conf.set('Brick', 'strict', 0)
    conf.set('Brick', 'method', 'usb=True, bluetooth=False')
    conf.write(open(confpath, 'w'))
    print("The file has been written at %s" % confpath)
    print("The file contains less-than-sane default values to get you started.")
    print("You must now edit the file with a text editor and change the values to match what you would pass to find_one_brick")
    print("The fields for name, host, and strict correspond to the similar args accepted by find_one_brick")
    print("The method field contains the string which would be passed to Method()")
    print("Any field whose corresponding option does not need to be passed to find_one_brick should be commented out (using a # at the start of the line) or simply removed.")
    print("If you have questions, check the wiki and then ask on the mailing list.")
