# SPDX-FileCopyrightText: 2023 Tim C
#
# SPDX-License-Identifier: MIT

"""
`adafruit_display_text.outlined_label`
====================================================

Subclass of BitmapLabel that adds outline color and stroke size
functionalities.

* Author(s): Tim Cocks

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""
__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Text.git"

import bitmaptools
import traceback
from adafruit_display_text import bitmap_label
from displayio import Palette, Bitmap

try:
    from typing import Optional, Tuple
    from fontio import FontProtocol
except ImportError:
    pass


class OutlinedLabel(bitmap_label.Label):
    def __init__(self, font, outline_color=0x999999, outline_size=1, **kwargs):
        super().__init__(font, **kwargs)

        _background_color = self._palette[0]
        _foreground_color = self._palette[1]
        _background_is_transparent = self._palette.is_transparent(0)
        self._palette = Palette(3)
        self._palette[0] = _background_color
        self._palette[1] = _foreground_color
        self._palette[2] = outline_color
        if _background_is_transparent:
            self._palette.make_transparent(0)

        self._outline_size = outline_size
        self._stamp_source = Bitmap((outline_size * 2) + 1, (outline_size * 2) + 1, 3)
        self._stamp_source.fill(2)

        self._bitmap = None

        self._reset_text(
            font=font,
            text=self._text,
            line_spacing=self._line_spacing,
            scale=self.scale,
        )

    def _add_outline(self):
        try:
            # before = time.monotonic()

            for y in range(self.bitmap.height):
                for x in range(self.bitmap.width):
                    if self.bitmap[x, y] == 1:
                        # bitmap.blit(x-size,y-size, stamp_source, skip_self_index=target_color_index)
                        bitmaptools.blit(
                            self.bitmap,
                            self._stamp_source,
                            x - self._outline_size,
                            y - self._outline_size,
                            skip_dest_index=1,
                        )
                        # bitmaptools.blit(bitmap, stamp_source, x - size, y - size)
                        # for y_loc in range(-size, size+1):
                        #     for x_loc in range(-size, size+1):
                        #         if bitmap[x+x_loc, y+y_loc] != target_color_index:
                        #             bitmap[x + x_loc, y + y_loc] = outline_color_index
        except ValueError as ve:
            # print(traceback.print_exception(ve))
            pass
        except AttributeError as ae:
            # print(traceback.print_exception(ae))
            pass

    def _place_text(
        self,
        bitmap: Bitmap,
        text: str,
        font: FontProtocol,
        xposition: int,
        yposition: int,
        skip_index: int = 0,  # set to None to write all pixels, other wise skip this palette index
        # when copying glyph bitmaps (this is important for slanted text
        # where rectangular glyph boxes overlap)
    ) -> Tuple[int, int, int, int]:
        parent_result = super()._place_text(
            bitmap, text, font, xposition, yposition, skip_index=skip_index
        )

        self._add_outline()

        return parent_result

    @property
    def outline_color(self):
        return self._palette[2]

    @outline_color.setter
    def outline_color(self, new_outline_color):
        self._palette[2] = new_outline_color

    @property
    def outline_size(self):
        return self._outline_size

    @outline_size.setter
    def outline_size(self, new_outline_size):
        self._outline_size = new_outline_size
        self._stamp_source = Bitmap(
            (new_outline_size * 2) + 1, (new_outline_size * 2) + 1, 3
        )
        self._stamp_source.fill(2)
        self._reset_text(
            font=self._font,
            text=self._text,
            line_spacing=self._line_spacing,
            scale=self.scale,
        )
