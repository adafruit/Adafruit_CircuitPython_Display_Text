# SPDX-FileCopyrightText: 2023 Tim C
# SPDX-License-Identifier: MIT

import board
import terminalio
from adafruit_display_text import outlined_label

text = "Hello world"
text_area = outlined_label.OutlinedLabel(
    terminalio.FONT,
    text=text,
    color=0xFF00FF,
    outline_color=0x00FF00,
    outline_size=1,
    scale=2,
)
text_area.x = 10
text_area.y = 14
board.DISPLAY.show(text_area)
while True:
    pass
