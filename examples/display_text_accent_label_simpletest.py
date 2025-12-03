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

from adafruit_display_text.accent_label import AccentLabel

display = supervisor.runtime.display

main_group = displayio.Group()

accent_palette = displayio.Palette(4)
accent_palette[2] = 0x000000
accent_palette[3] = 0xDDDD00

quote_lbl = AccentLabel(terminalio.FONT, color_palette=accent_palette, text="", color=0xAAAAAA)
quote_lbl.anchor_point = (0, 0)
quote_lbl.anchored_position = (4, 4)
main_group.append(quote_lbl)
display.root_group = main_group

text = "CircuitPython is amazing!"
start_index = text.find("amazing!")
end_index = start_index + len("amazing!")

quote_lbl.text = text
quote_lbl.add_accent_range(start_index, end_index, 2, 3)

while True:
    time.sleep(1)
