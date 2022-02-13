#!/usr/bin/python3
"""NXT-Python tutorial: increase log level."""
import logging

import nxt.locator

# Increase the log level, must be done before using any NXT-Python function. See logging
# documentation for details.
logging.basicConfig(level=logging.DEBUG)

with nxt.locator.find() as b:
    b.play_tone(440, 250)
