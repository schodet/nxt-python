#!/usr/bin/env python
#
# Converted from mary.rb found in ruby_nxt package
# Plays "Mary Had A Little Lamb"
# Author: Christopher Continanza <christopher.continanza@villanova.edu>

from time import sleep
import nxt.locator

FREQ_C = 523
FREQ_D = 587
FREQ_E = 659
FREQ_G = 784

b = nxt.locator.find_one_brick()

b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_D, 500)
b.play_tone_and_wait(FREQ_C, 500)
b.play_tone_and_wait(FREQ_D, 500)
b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_E, 500)
sleep(0.5)
b.play_tone_and_wait(FREQ_D, 500)
b.play_tone_and_wait(FREQ_D, 500)
b.play_tone_and_wait(FREQ_D, 500)
sleep(0.5)
b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_G, 500)
b.play_tone_and_wait(FREQ_G, 500)
sleep(0.5)
b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_D, 500)
b.play_tone_and_wait(FREQ_C, 500)
b.play_tone_and_wait(FREQ_D, 500)
b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_D, 500)
b.play_tone_and_wait(FREQ_D, 500)
b.play_tone_and_wait(FREQ_E, 500)
b.play_tone_and_wait(FREQ_D, 500)
b.play_tone_and_wait(FREQ_C, 750)
