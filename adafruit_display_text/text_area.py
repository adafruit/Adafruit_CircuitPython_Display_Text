# The MIT License (MIT)
#
# Copyright (c) 2019 Scott Shawcroft for Adafruit Industries LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_display_text`
====================================================

Displays text using CircuitPython's displayio.

* Author(s): Scott Shawcroft

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

import displayio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Text.git"


class TextArea(displayio.Group):
    def __init__(self, font, *, text=None, width=None, color=0xffffff, height=1):
        if not width and not text:
            raise RuntimeError("Please provide a width")
        super().__init__(max_size=width * height)
        if not width:
            width = len(text)
        self.width = width
        self.font = font
        self._text = None

        self.p = displayio.Palette(2)
        self.p.make_transparent(0)
        self.p[1] = color

        bounds = self.font.get_bounding_box()
        self.height = bounds[1]

        if text:
            self._update_text(text)


    def _update_text(self, new_text):
        x = 0
        y = 0
        i = 0
        first_different = self._text is not None
        for c in new_text:
            if chr(ord(c)) == '\n':
                y += int(self.height * 1.25)
                x = 0
                continue
            glyph = self.font.get_glyph(ord(c))
            if not glyph:
                continue
            if not self._text or i >= len(self._text) or c != self._text[i]:
                face = displayio.TileGrid(glyph.bitmap, pixel_shader=self.p, default_tile=glyph.tile_index,
                                          tile_width=glyph.width, tile_height=glyph.height,
                                          position=(x, y + self.height - glyph.height - glyph.dy))
                if i < len(self):
                    self[i] = face
                else:
                    self.append(face)
            x += glyph.shift_x

            # TODO skip this for control sequences or non-printables.
            i += 1
        # Remove the rest
        while len(self) > i:
            self.pop()
        self._text = new_text

    @property
    def color(self):
        return self.p[1]

    @color.setter
    def color(self, c):
        self.p[1] = c

    @property
    def text(self, t):
        self._text = t

    @text.setter
    def text(self, t):
        self._update_text(t)
