# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This examples shows the use of base_alignment parameter.
"""

import time
import board
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label


display = board.DISPLAY

# Font definition. You can choose any two fonts available in your system
MEDIUM_FONT = bitmap_font.load_font("Helvetica-Bold-16.bdf")
BIG_FONT = bitmap_font.load_font("LeagueSpartan-Bold-16.bdf")

# Test parameters
TEXT_BACKGROUND_COLOR = 0x990099
TEXT_COLOR = 0x00FF00
X_COL_POS = [10, 90]  # X position of the Label boxes
TEST_TEXT = [
    "aApPqQ.",
    "ppppppp",
    "llllll",
    "oooooo",
    "ñúÇèüß",
]  # Iteration text for testing
LOCALISATION_Y = [40, 80, 120, 160, 200]  # Y coordinate of the text labels
NUMBER_TEXT_LABELS = len(LOCALISATION_Y) * len(
    X_COL_POS
)  # Calculation for Display.Group function
TIME_BETWEEN_TEXTS = 5  # Seconds
BASE_ALIGNMENT_OPTIONS = [False, True]

# Test
for behaviour in BASE_ALIGNMENT_OPTIONS:
    for text_test in TEST_TEXT:
        main_group = displayio.Group(max_size=NUMBER_TEXT_LABELS + 1)
        for position in LOCALISATION_Y:
            text = label.Label(
                font=MEDIUM_FONT,
                text=text_test,
                color=TEXT_COLOR,
                background_tight=True,
                background_color=TEXT_BACKGROUND_COLOR,
                x=X_COL_POS[0],
                y=position,
                base_alignment=behaviour,
            )
            main_group.append(text)
            text = label.Label(
                font=BIG_FONT,
                text=text_test,
                color=TEXT_COLOR,
                background_tight=False,
                background_color=TEXT_BACKGROUND_COLOR,
                x=X_COL_POS[1],
                y=position,
                base_alignment=behaviour,
            )
            main_group.append(text)
            display.show(main_group)
            display.refresh()
        time.sleep(TIME_BETWEEN_TEXTS)


bitmap = displayio.Bitmap(280, 5, 2)
palette = displayio.Palette(2)
palette[0] = 0x004400
palette[1] = 0x00FFFF
tile_grid2 = displayio.TileGrid(bitmap, pixel_shader=palette, x=10, y=160)
main_group.append(tile_grid2)

while True:
    pass
