# SPDX-FileCopyrightText: 2022 Tim Cocks for Adafruit Industries
# SPDX-License-Identifier: MIT

import supervisor
import terminalio

from adafruit_display_text.bitmap_label import Label

display = supervisor.runtime.display
text = "Hello world CircuitPython scrolling label"
scrolling_label = Label(terminalio.FONT, text=text, max_characters=20, animate_time=0.3)
scrolling_label.x = 10
scrolling_label.y = 10
display.root_group = scrolling_label
display.auto_refresh = False
display.refresh()
while True:
    if scrolling_label.update():
        display.refresh()
