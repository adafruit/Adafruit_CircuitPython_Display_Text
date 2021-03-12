# SPDX-FileCopyrightText: 2021 Jose David M.
# SPDX-License-Identifier: MIT

"""
This example shows the use of label with syles
"""
import board
import displayio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240
TEXT = "Hello"
FONT = bitmap_font.load_font("fonts/LeagueSpartan-Bold-16.bdf")

text_area_top_left = label.LabelT(FONT, "DarkBrown7", text=TEXT)
text_area_top_left.anchor_point = (0.0, 0.0)
text_area_top_left.anchored_position = (0, 0)

text_area_top_right = label.LabelT(FONT, "LightTeal", text=TEXT)
text_area_top_right.anchor_point = (1.0, 0.0)
text_area_top_right.anchored_position = (DISPLAY_WIDTH, 0)

text_area_middle_middle = label.Label(FONT, text=TEXT)
text_area_middle_middle.anchor_point = (0.5, 0.5)
text_area_middle_middle.anchored_position = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2)

text_area_bottom_left = label.LabelT(FONT, "LightBlue1", text=TEXT)
text_area_bottom_left.anchor_point = (0.0, 1.0)
text_area_bottom_left.anchored_position = (0, DISPLAY_HEIGHT)

text_area_bottom_right = label.LabelT(FONT, "BrightColors", text=TEXT)
text_area_bottom_right.anchor_point = (1.0, 1.0)
text_area_bottom_right.anchored_position = (DISPLAY_WIDTH, DISPLAY_HEIGHT)

text_group = displayio.Group(max_size=5)
text_group.append(text_area_top_left)
text_group.append(text_area_top_right)
text_group.append(text_area_middle_middle)
text_group.append(text_area_bottom_left)
text_group.append(text_area_bottom_right)

board.DISPLAY.show(text_group)

while True:
    pass
