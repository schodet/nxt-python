# nxt.command.screenshot module -- Capture the NXT screen content
# Copyright (C) 2010-2025  Nicolas Schodet
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
"""Screen capture utility for the NXT brick."""

import argparse
import logging
import struct

from PIL import Image

import nxt.locator

# Those are extracted from firmware sources.
DISPLAY_MODULE_ID = 0x000A0001
DISPLAY_SCREEN_OFFSET = 119
DISPLAY_WIDTH = 100
DISPLAY_HEIGHT = 64

# Read no more than 32 bytes per request.
IOM_CHUNK = 32


def get_parser() -> argparse.ArgumentParser:
    """Return argument parser."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", help="image file name to write to")
    nxt.locator.add_arguments(p)
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    p.add_argument("--log-level", type=str.upper, choices=levels, help="set log level")
    return p


def screenshot(b: nxt.brick.Brick) -> Image.Image:
    """Take a screenshot, return a PIL image.

    See https://ni.fr.eu.org/lego/nxt_screenshot/ for explanations.
    """
    # Read pixels.
    pixels = bytes()
    for i in range(0, DISPLAY_WIDTH * DISPLAY_HEIGHT // 8, IOM_CHUNK):
        mod_id, contents = b.read_io_map(
            DISPLAY_MODULE_ID, DISPLAY_SCREEN_OFFSET + i, IOM_CHUNK
        )
        pixels += contents
    # Transform to a PIL format.
    pilpixels = []
    bit = 1
    linebase = 0
    for y in range(0, DISPLAY_HEIGHT):
        # Read line by line.
        for x in range(0, DISPLAY_WIDTH):
            if pixels[linebase + x] & bit:
                pilpixels.append(0)
            else:
                pilpixels.append(255)
        bit <<= 1
        # When 8 lines have been read, go on with the next byte line.
        if bit == (1 << 8):
            bit = 1
            linebase += DISPLAY_WIDTH
    # Return a PIL image.
    pilbuffer = struct.pack("%dB" % DISPLAY_WIDTH * DISPLAY_HEIGHT, *pilpixels)
    pilimage = Image.frombuffer(
        "L", (DISPLAY_WIDTH, DISPLAY_HEIGHT), pilbuffer, "raw", "L", 0, 1
    )
    return pilimage


def run() -> None:
    """Run command."""
    options = get_parser().parse_args()

    if options.log_level:
        logging.basicConfig(level=options.log_level)

    print("Finding brick...")
    with nxt.locator.find_with_options(options) as brick:
        image = screenshot(brick)
        image.save(options.image)


if __name__ == "__main__":
    run()
