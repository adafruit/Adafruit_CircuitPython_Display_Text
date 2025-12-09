# SPDX-FileCopyrightText: 2025 Tim Cocks for Adafruit Industries
# SPDX-License-Identifier: MIT

import displayio
import supervisor
import terminalio

from adafruit_display_text.bitmap_label import Label

display = supervisor.runtime.display
text = "Hello world CircuitPython Labels are awesome!"

accent_palette = displayio.Palette(7)
accent_palette[3] = 0x3774A7
accent_palette[4] = 0xFFD748
accent_palette[5] = 0xFFFFFF
accent_palette[6] = 0x652F8F

scrolling_label = Label(
    terminalio.FONT,
    text=text,
    max_characters=20,
    animate_time=0.3,
    color_palette=accent_palette,
    color=0xAAAAAA,
    scale=2,
)

scrolling_label.x = 10
scrolling_label.y = 10
display.root_group = scrolling_label

scrolling_label.add_accent_to_substring("CircuitPython", 5, 6)
scrolling_label.add_accent_to_substring("awesome!", 3, 4, "outline")

display.auto_refresh = False
display.refresh()
while True:
    if scrolling_label.update():
        display.refresh()
