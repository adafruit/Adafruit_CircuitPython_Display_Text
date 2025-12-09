# SPDX-FileCopyrightText: 2025 Tim Cocks for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
Demonstrates how to use the AccentLabel to highlight part of the text
with different foreground and background color.
"""

import time

import displayio
import supervisor
import terminalio

from adafruit_display_text.bitmap_label import Label

display = supervisor.runtime.display

main_group = displayio.Group()

accent_palette = displayio.Palette(6)
accent_palette[2] = 0x000000
accent_palette[3] = 0xDDDD00
accent_palette[4] = 0xFFFFFF
accent_palette[5] = 0x652F8F

accent_lbl = Label(terminalio.FONT, color_palette=accent_palette, text="", color=0xAAAAAA)
accent_lbl.anchor_point = (0, 0)
accent_lbl.anchored_position = (4, 4)
main_group.append(accent_lbl)
display.root_group = main_group

text = "CircuitPython is amazing!"
accent_lbl.text = text

time.sleep(1)
accent_lbl.add_accent_to_substring("CircuitPython", 4, 5)
time.sleep(2)
accent_lbl.remove_accent_from_substring("CircuitPython")
accent_lbl.add_accent_to_substring("amazing!", 2, 3)

while True:
    time.sleep(1)
