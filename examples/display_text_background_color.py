# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This example shows the use color and background_color
"""

import time

import board
import terminalio

from adafruit_display_text import label

text = " Color Background Hello world"
text_area = label.Label(terminalio.FONT, text=text, color=0x0000FF, background_color=0xFFAA00)
text_area.x = 10
text_area.y = 10

print(f"background color is {text_area.background_color:06x}")

board.DISPLAY.root_group = text_area

time.sleep(2)
text_area.background_color = 0xFF0000
print(f"background color is {text_area.background_color:06x}")
time.sleep(2)
text_area.background_color = None
print(f"background color is {text_area.background_color}")
while True:
    pass
