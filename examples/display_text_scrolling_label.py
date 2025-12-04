# SPDX-FileCopyrightText: 2022 Tim Cocks for Adafruit Industries
# SPDX-License-Identifier: MIT

import supervisor
import terminalio

from adafruit_display_text.bitmap_label import Label

display = supervisor.runtime.display
text = "Hello world CircuitPython scrolling label"
my_scrolling_label = Label(terminalio.FONT, text=text, max_characters=20, animate_time=0.3)
my_scrolling_label.x = 10
my_scrolling_label.y = 10
display.root_group = my_scrolling_label
while True:
    my_scrolling_label.update()
