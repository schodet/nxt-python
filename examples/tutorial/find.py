#!/usr/bin/python3
"""NXT-Python tutorial: find the brick."""
import nxt.locator

# Find a brick.
with nxt.locator.find() as b:
    # Once found, print its name.
    print("Found brick:", b.get_device_info()[0])
    # And play a recognizable note.
    b.play_tone(440, 250)
