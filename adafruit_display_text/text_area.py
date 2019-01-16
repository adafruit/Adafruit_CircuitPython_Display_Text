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


class TextArea:
    def __init__(self, font, *, text=None, width=None, color=0x0, height=1):
        if not width and not text:
            raise RuntimeError("Please provide a width")
        if not width:
            width = len(text)
        self.width = width
        self.font = font
        self._text = text

        self.p = displayio.Palette(2)
        self.p.make_transparent(0)
        self.p[1] = color

        self.group = displayio.Group(max_size=width * height)

        bounds = self.font.get_bounding_box()
        self.height = bounds[1]

        self.sprites = [None] * (width * height)

        self._x = 0
        self._y = 0

        if text:
            self._update_text()


    def _update_text(self):
        x = 0
        i = 0
        for c in self._text:
            glyph = self.font.get_glyph(ord(c))
            if not glyph:
                continue
            face = displayio.Sprite(glyph["bitmap"], pixel_shader=self.p,
                                    position=(self._x + x, self._y + self.height - glyph["bounds"][1] - glyph["bounds"][3]))
            x += glyph["shift"][0]
            self.group.append(face)
            self.sprites[i] = face

            # TODO skip this for control sequences or non-printables.
            i += 1

            # TODO: support multiple lines by adjusting y

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
        self._text = t
        self._update_text()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        for sprite in self.sprites:
            if not sprite:
                continue
            pos = sprite.position
            sprite.position = (pos[0], (pos[1] - self._y) + new_y)
        self._y = new_y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        for sprite in self.sprites:
            if not sprite:
                continue
            pos = sprite.position
            sprite.position = ((pos[0] - self._x) + new_x, pos[1])
        self._x = new_x
