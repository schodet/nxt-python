#!/usr/bin/env python3
import sys

import pygame

import nxt.locator
import nxt.motor
from nxt.error import DirectProtocolError

""" example that reads out the memory region used for the display content
("framebuffer") of a USB-connected NXT

useful for those bricks with displays that died of old age (the display is
probably still fine, but the glue on the ribbon cable usually isn't)

this code basically reimplements what
https://bricxcc.sourceforge.net/utilities.html -> "NeXTScreen"
in a less obscure programming language ;-)

"""


PIXEL_SIZE = 6
WINDOW_WIDTH = 100 * PIXEL_SIZE
WINDOW_HEIGHT = (64 + 32) * PIXEL_SIZE  # Additional 32 lines for the GUI-buttons

MAIN_WINDOW_SURFACE = None
FPS_CLOCK = pygame.time.Clock()


def NXT_get_display_data(b):
    # each "module" has it's own memory region, id, ...
    #    for t in b.find_modules():
    #        print(t, hex(t[1]))
    mod_display = 0xA0001

    # display is WxH = 100x64 pixels
    # their memory layout is in eight lines of 100 bytes, with each byte encoding
    # a strip of eight vertical pixels
    data = b""
    pixels = [""] * 64
    DisplayOffsetNormal = 119
    for i in range(20):
        data += b.read_io_map(mod_display, DisplayOffsetNormal + i * 40, 40)[1]
    for line in range(8):
        for x in range(100):
            b = data[line * 100 + x]
            for y in range(8):
                bitsels = format(
                    b, "08b"
                )  # abuse the stringification to get 8 1's and 0's
                pixels[line * 8 + y] += bitsels[7 - y]
    return pixels


def initialize_pygame():
    pygame.init()
    main_window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    global MAIN_WINDOW_SURFACE
    MAIN_WINDOW_SURFACE = pygame.display.set_mode(main_window_size)
    pygame.display.set_caption("NXT Screen")
    # paint the buttons...
    rect_return = pygame.Rect(
        (50 - 13) * PIXEL_SIZE, (64 + 2) * PIXEL_SIZE, 26 * PIXEL_SIZE, 16 * PIXEL_SIZE
    )
    pygame.draw.rect(MAIN_WINDOW_SURFACE, pygame.Color("orange"), rect_return)
    pygame.draw.polygon(
        MAIN_WINDOW_SURFACE,
        pygame.Color("antiquewhite3"),
        (
            ((50 - 13 - 30) * PIXEL_SIZE, (64 + 2 + 8) * PIXEL_SIZE),
            ((50 - 13 - 30 + 26) * PIXEL_SIZE, (64 + 2) * PIXEL_SIZE),
            ((50 - 13 - 30 + 26) * PIXEL_SIZE, (64 + 2 + 16) * PIXEL_SIZE),
        ),
    )
    pygame.draw.polygon(
        MAIN_WINDOW_SURFACE,
        pygame.Color("antiquewhite3"),
        (
            ((50 + 13 + 30) * PIXEL_SIZE - 1, (64 + 2 + 8) * PIXEL_SIZE),
            ((50 + 13 + 30 - 26) * PIXEL_SIZE - 1, (64 + 2) * PIXEL_SIZE),
            ((50 + 13 + 30 - 26) * PIXEL_SIZE - 1, (64 + 2 + 16) * PIXEL_SIZE),
        ),
    )
    rect_exit = pygame.Rect(
        (50 - 13) * PIXEL_SIZE, (64 + 20) * PIXEL_SIZE, 26 * PIXEL_SIZE, 10 * PIXEL_SIZE
    )
    pygame.draw.rect(MAIN_WINDOW_SURFACE, pygame.Color("antiquewhite4"), rect_exit)


def draw(pixels):
    for y in range(64):
        for x in range(100):
            p = pixels[y][x]
            if p == "0":
                color = pygame.Color("grey66")
            else:
                color = pygame.Color("black")

            rect = pygame.Rect(x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            pygame.draw.rect(MAIN_WINDOW_SURFACE, color, rect)


def main_loop():
    b = nxt.locator.find()
    print("Found brick:", b.get_device_info()[0])
    # And play a recognizable note.
    b.play_tone(440, 250)

    while True:
        for event in pygame.event.get():
            # react to titlebar 'X' beeing clicked
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # or the press of the 'Esc' key
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
            ):  # interpret mouse-button clicks on the GUI buttons
                if (50 - 13) * PIXEL_SIZE <= event.pos[0] <= (
                    50 - 13 + 26
                ) * PIXEL_SIZE and (64 + 2) * PIXEL_SIZE <= event.pos[1] <= (
                    64 + 2 + 16
                ) * PIXEL_SIZE:
                    b.write_io_map(0x40001, 35, bytearray([0x80]))
                    b.write_io_map(0x40001, 35, bytearray([0x80]))
                if (50 - 13 - 30) * PIXEL_SIZE <= event.pos[0] <= (
                    50 - 13 - 30 + 26
                ) * PIXEL_SIZE and (64 + 2) * PIXEL_SIZE <= event.pos[1] <= (
                    64 + 2 + 16
                ) * PIXEL_SIZE:
                    b.write_io_map(0x40001, 34, bytearray([0x80]))
                    b.write_io_map(0x40001, 34, bytearray([0x80]))
                if (50 + 13 + 30 - 26) * PIXEL_SIZE <= event.pos[0] <= (
                    50 + 13 + 30
                ) * PIXEL_SIZE and (64 + 2) * PIXEL_SIZE <= event.pos[1] <= (
                    64 + 2 + 16
                ) * PIXEL_SIZE:
                    b.write_io_map(0x40001, 33, bytearray([0x80]))
                    b.write_io_map(0x40001, 33, bytearray([0x80]))
                if (50 - 13) * PIXEL_SIZE <= event.pos[0] <= (
                    50 - 13 + 26
                ) * PIXEL_SIZE and (64 + 20) * PIXEL_SIZE <= event.pos[1] <= (
                    64 + 20 + 10
                ) * PIXEL_SIZE:
                    try:
                        b.stop_program()
                    except DirectProtocolError:
                        b.write_io_map(0x40001, 32, bytearray([0x80]))
                        b.write_io_map(0x40001, 32, bytearray([0x80]))

        # beep to let the user know that a screen refresh happended
        # removed beep as it annoyed me :-)
        # b.play_tone(440, 25)

        p = NXT_get_display_data(b)
        draw(p)

        pygame.display.update()

        # keep the refresh rate low, to not interfere with the NXP too much
        # since usb-commands keep the command processor busy, which might tripp
        # up the more timing critical bluetooth handling parts
        # in my case 10 fps is still OK when connecting via USB:
        FPS_CLOCK.tick(10)


if __name__ == "__main__":
    initialize_pygame()
    main_loop()
