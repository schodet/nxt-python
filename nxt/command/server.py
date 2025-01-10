# nxt.command.server module -- Serve an interface to the NXT brick
# Copyright (C) 2011  zonedabone, Marcus Wanner
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
"""Network server for the NXT brick."""

import argparse
import logging
import socket
import traceback

import nxt.locator


def get_parser() -> argparse.ArgumentParser:
    """Return argument parser."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-p", "--port", type=int, default=2727, help="bind port")
    nxt.locator.add_arguments(p)
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    p.add_argument("--log-level", type=str.upper, choices=levels, help="set log level")
    return p


def serve(
    brick: nxt.brick.Brick, channel: socket.socket, details: tuple[str, int]
) -> None:
    """Handles serving the client."""
    print(f"Connection from {details[0]}.")
    run = True
    try:
        while run:
            data = channel.recv(1024)
            if not data:
                break
            code = data[0]
            if code == 0x00 or code == 0x01 or code == 0x02:
                brick._sock.send(data)
                reply = brick._sock.recv()
                channel.send(reply)
            elif code == 0x80 or code == 0x81:
                brick._sock.send(data)
            elif code == 0x98:
                channel.send(brick._sock.type.encode("ascii"))
            elif code == 0x99:
                run = False
            else:
                raise RuntimeError("Bad protocol")
    except Exception:
        traceback.print_exc()
    finally:
        channel.close()
        print("Connection closed.")


def run() -> None:
    """Run command."""
    options = get_parser().parse_args()

    if options.log_level:
        logging.basicConfig(level=options.log_level)

    print("Finding brick...")
    with nxt.locator.find_with_options(options) as brick:
        print(f"Brick found, starting server on port {options.port}.")
        print("Use Ctrl-C to interrupt.")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("", options.port))
        server.listen(1)
        try:
            # Have the server serve "forever":
            while True:
                channel, details = server.accept()
                serve(brick, channel, details)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    run()
