# nxt.locator module -- Locate LEGO Minstorms NXT bricks via USB or Bluetooth
# Copyright (C) 2006, 2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner
# Copyright (C) 2013  Dave Churchill, Marcus Wanner
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

import traceback, ConfigParser, os

class BrickNotFoundError(Exception):
    pass

class NoBackendError(Exception):
    pass

class Method():
    """Used to indicate which comm backends should be tried by find_bricks/
find_one_brick. Any or all can be selected."""
    def __init__(self, usb=True, bluetooth=True, fantomusb=False, fantombt=False, device=False):
        #new method options MUST default to False!
        self.usb = usb
        self.bluetooth = bluetooth
        self.fantom = fantomusb or fantombt
        self.fantomusb = fantomusb
        self.fantombt = fantombt
        self.device = device

def find_bricks(host=None, name=None, silent=False, method=Method()):
    """Used by find_one_brick to look for bricks ***ADVANCED USERS ONLY***"""
    methods_available = 0

    if method.usb:
        try:
            import usbsock
            methods_available += 1
            socks = usbsock.find_bricks(host, name)
            for s in socks:
                yield s
        except ImportError:
            import sys
            if not silent: print >>sys.stderr, "USB module unavailable, not searching there"
    
    if method.bluetooth:
        try:
            import bluesock
            methods_available += 1
            try:
                socks = bluesock.find_bricks(host, name)
                for s in socks:
                    yield s
            except (bluesock.bluetooth.BluetoothError, IOError): #for cases such as no adapter, bluetooth throws IOError, not BluetoothError
                pass
        except ImportError:
            import sys
            if not silent: print >>sys.stderr, "Bluetooth module unavailable, not searching there"
    
    if method.device:
        try:
            import devsock
            methods_available += 1
            socks = devsock.find_bricks(name=name)
            for s in socks:
                yield s
        except IOError:
            pass

    if method.fantom:
        try:
            import fantomsock
            methods_available += 1
            if method.fantomusb:
                usbsocks = fantomsock.find_bricks(host, name, False)
                for s in usbsocks:
                    yield s
            if method.fantombt:
                btsocks = fantomsock.find_bricks(host, name, True)
                for s in btsocks:
                    yield s
        except ImportError:
            import sys
            if not silent: print >>sys.stderr, "Fantom module unavailable, not searching there"
    
    if methods_available == 0:
        raise NoBackendError("No selected backends are available! Did you install the comm modules?")


def find_one_brick(host=None, name=None, silent=False, strict=None, debug=False, method=None, confpath=None):
    """Use to find one brick. The host and name args limit the search to 
a given MAC or brick name. Set silent to True to stop nxt-python from 
printing anything during the search. This function by default 
automatically checks to see if the brick found has the correct host/name 
(if either are provided) and will not return a brick which doesn't 
match. This can be disabled (so the function returns any brick which can 
be connected to and provides a valid reply to get_device_info()) by 
passing strict=False. This will, however, still tell the comm backends 
to only look for devices which match the args provided. The confpath arg 
specifies the location of the configuration file which brick location 
information will be read from if no brick location directives (host, 
name, strict, or method) are provided."""
    if debug and silent:
        silent=False
        print "silent and debug can't both be set; giving debug priority"

    conf = read_config(confpath, debug)
    if not (host or name or strict or method):
        host	= conf.get('Brick', 'host')
        name	= conf.get('Brick', 'name')
        strict	= bool(int(conf.get('Brick', 'strict')))
        method	= eval('Method(%s)' % conf.get('Brick', 'method'))
    if not strict: strict = True
    if not method: method = Method()
    if debug:
        print "Host: %s Name: %s Strict: %s" % (host, name, str(strict))
        print "USB: %s BT: %s Fantom: %s FUSB: %s FBT: %s" % (method.usb, method.bluetooth, method.fantom, method.fantombt, method.fantomusb)
    
    for s in find_bricks(host, name, silent, method):
        try:
            if host and 'host' in dir(s) and s.host != host:
                if debug:
                    print "Warning: the brick found does not match the host provided (s.host)."
                if strict: continue
            b = s.connect()
            info = b.get_device_info()
            if host and info[1] != host:
                if debug:
                    print "Warning: the brick found does not match the host provided (get_device_info)."
                if strict:
                    s.close()
                    continue
            if name and info[0].strip('\0') != name:
                if debug:
                    print "Warning; the brick found does not match the name provided."
                if strict:
                    s.close()
                    continue
            return b
        except:
            if debug:
                traceback.print_exc()
                print "Failed to connect to possible brick"
    raise BrickNotFoundError


def server_brick(host, port = 2727):
    import ipsock
    sock = ipsock.IpSock(host, port)
    return sock.connect()

def device_brick(filename):
    import devsock
    sock = devsock.find_bricks(filename=filename)
    return sock.connect()


def read_config(confpath=None, debug=False):
    conf = ConfigParser.RawConfigParser({'host': None, 'name': None, 'strict': True, 'method': ''})
    if not confpath: confpath = os.path.expanduser('~/.nxt-python')
    if conf.read([confpath]) == [] and debug:
        print "Warning: Config file (should be at %s) was not read. Use nxt.locator.make_config() to create a config file." % confpath
    if conf.has_section('Brick') == False:
        conf.add_section('Brick')
    return conf

def make_config(confpath=None):
    conf = ConfigParser.RawConfigParser()
    if not confpath: confpath = os.path.expanduser('~/.nxt-python')
    print "Welcome to the nxt-python config file generator!"
    print "This function creates an example file which find_one_brick uses to find a brick."
    try:
        if os.path.exists(confpath): raw_input("File already exists at %s. Press Enter to overwrite or Ctrl+C to abort." % confpath)
    except KeyboardInterrupt:
        print "Not writing file."
        return
    conf.add_section('Brick')
    conf.set('Brick', 'name', 'MyNXT')
    conf.set('Brick', 'host', '54:32:59:92:F9:39')
    conf.set('Brick', 'strict', 0)
    conf.set('Brick', 'method', 'usb=True, bluetooth=False, fantomusb=True')
    conf.write(open(confpath, 'w'))
    print "The file has been written at %s" % confpath
    print "The file contains less-than-sane default values to get you started."
    print "You must now edit the file with a text editor and change the values to match what you would pass to find_one_brick"
    print "The fields for name, host, and strict correspond to the similar args accepted by find_one_brick"
    print "The method field contains the string which would be passed to Method()"
    print "Any field whose corresponding option does not need to be passed to find_one_brick should be commented out (using a # at the start of the line) or simply removed."
    print "If you have questions, check the wiki and then ask on the mailing list."
