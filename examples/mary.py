#!/usr/bin/env python
#
# Converted from mary.rb found in ruby_nxt package
# Plays "Mary Had A Little Lamb"
# Author: Christopher Continanza <christopher.continanza@villanova.edu>
# Refactored: christophegranic@gmail.com

from time import sleep
import nxt.locator

C = 523
D = 587
E = 659
G = 784
R = None

def play(note):
    if note:
        b.play_tone_and_wait(note, 500)
    else:
        sleep(0.5)

b = nxt.locator.find_one_brick()

for note in [E, D, C, D, E, E, E, R,
             D, D, D, R,
             E, G, G, R, E, D, C, D, E, E, E, E, D, D, E, D, C]:
    play(note)
