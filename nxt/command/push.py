# nxt.command.push module -- Push a file to the NXT brick
# Copyright (C) 2006  Douglas P Lau
# Copyright (C) 2010  rhn
# Copyright (C) 2025  Nicolas Schodet
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
"""Push files to a NXT brick."""

import argparse
import logging
import os.path

import nxt.locator
from nxt.error import FileNotFoundError


def write_file(b: nxt.brick.Brick, fname: str) -> None:
    """Write file to NXT brick from file system."""
    oname = os.path.basename(fname)
    # Read input file.
    with open(fname, "rb") as f:
        data = f.read()
    # Remove existing file.
    try:
        b.file_delete(oname)
        print(f"Overwriting {oname} on NXT")
    except FileNotFoundError:
        pass
    # Write new file.
    print(f"Pushing {oname} ({len(data)} bytes) ...", end=" ", flush=True)
    with b.open_file(oname, "wb", len(data)) as w:
        w.write(data)
    print("done.")


def get_parser() -> argparse.ArgumentParser:
    """Return argument parser."""
    p = argparse.ArgumentParser(description=__doc__)
    nxt.locator.add_arguments(p)
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    p.add_argument("--log-level", type=str.upper, choices=levels, help="set log level")
    p.add_argument("file", nargs="+", help="file to transfer")
    return p


def run() -> None:
    """Run command."""
    options = get_parser().parse_args()

    if options.log_level:
        logging.basicConfig(level=options.log_level)

    print("Finding brick...")
    with nxt.locator.find_with_options(options) as brick:
        for filename in options.file:
            write_file(brick, filename)


if __name__ == "__main__":
    run()
