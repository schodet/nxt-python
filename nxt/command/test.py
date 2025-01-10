# nxt.command.test module -- Test command
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
"""Test the NXT-Python setup."""

import argparse
import logging

import nxt.locator


def get_parser() -> argparse.ArgumentParser:
    """Return argument parser."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--no-sound",
        action="store_false",
        dest="sound",
        default=True,
        help="disable sound test",
    )
    nxt.locator.add_arguments(p)
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    p.add_argument("--log-level", type=str.upper, choices=levels, help="set log level")
    return p


def run() -> None:
    """Run command."""
    options = get_parser().parse_args()

    if options.log_level:
        logging.basicConfig(level=options.log_level)

    print("Finding brick...")
    with nxt.locator.find_with_options(options) as b:
        name, host, signal_strengths, user_flash = b.get_device_info()
        print(f"NXT brick name: {name}")
        print(f"Host address: {host}")
        print(f"Bluetooth signal strengths: {signal_strengths!r}")
        print(f"Free user flash: {user_flash}")
        prot_version, fw_version = b.get_firmware_version()
        print(f"Protocol version {prot_version[0]}.{prot_version[1]}")
        print(f"Firmware version {fw_version[0]}.{fw_version[1]}")
        millivolts = b.get_battery_level()
        print(f"Battery level {millivolts} mV")
        if options.sound:
            print("Play test sound...", end="", flush=True)
            b.play_tone_and_wait(300, 50)
            b.play_tone_and_wait(400, 50)
            b.play_tone_and_wait(500, 50)
            b.play_tone_and_wait(600, 50)
            print("done.")


if __name__ == "__main__":
    run()
