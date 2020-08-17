# The MIT License (MIT)
#
# Copyright (c) 2020 Kevin Matocha
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
`bitmap_label`
================================================================================

Text graphics handling for CircuitPython, including text boxes


* Author(s): Kevin Matocha

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


class Label(displayio.Group):
    """A label displaying a string of text that is stored in a bitmap.
       Note: This ``bitmap_label.py`` library utilizes a bitmap to display the text.
       This method is memory-conserving relative to ``label.py``.
       For the bitmap_label library, the font, text, and line_spacing must be set at
       instancing and are immutable.  The ``max_glyphs`` parameter is ignored and is present
       only for direct compatability with label.py.
       For use cases where text changes are required after the initial instancing, please
       use the `label.py` library.
       For further reduction in memory usage, set save_text to False (text string will not
       be stored).

       The origin point set by ``x`` and ``y``
       properties will be the left edge of the bounding box, and in the center of a M
       glyph (if its one line), or the (number of lines * linespacing + M)/2. That is,
       it will try to have it be center-left as close as possible.

       :param Font font: A font class that has ``get_bounding_box`` and ``get_glyph``.
         Must include a capital M for measuring character size.
       :param str text: Text to display
       :param int max_glyphs: Unnecessary parameter (provided only for direct compability
       with label.py)
       :param int color: Color of all text in RGB hex
       :param int background_color: Color of the background, use `None` for transparent
       :param double line_spacing: Line spacing of text to display
       :param boolean background_tight: Set `True` only if you want background box to tightly
       surround text
       :param int padding_top: Additional pixels added to background bounding box at top
       :param int padding_bottom: Additional pixels added to background bounding box at bottom
       :param int padding_left: Additional pixels added to background bounding box at left
       :param int padding_right: Additional pixels added to background bounding box at right
       :param (double,double) anchor_point: Point that anchored_position moves relative to.
        Tuple with decimal percentage of width and height.
        (E.g. (0,0) is top left, (1.0, 0.5): is middle right.)
       :param (int,int) anchored_position: Position relative to the anchor_point. Tuple
       containing x,y pixel coordinates.
       :param int scale: Integer value of the pixel scaling
       :param bool save_text: Set True to save the text string as a constant in the
        label structure.  Set False to reduce memory use.
       """

    # pylint: disable=unused-argument, too-many-instance-attributes, too-many-locals, too-many-arguments
    # Note: max_glyphs parameter is unnecessary, this is used for direct
    # compatibility with label.py

    def __init__(
        self,
        font,
        x=0,
        y=0,
        text="",
        max_glyphs=None,  # This input parameter is ignored, only present for compatibility
        # with label.py
        color=0xFFFFFF,
        background_color=None,
        line_spacing=1.25,
        background_tight=False,
        padding_top=0,
        padding_bottom=0,
        padding_left=0,
        padding_right=0,
        anchor_point=None,
        anchored_position=None,
        save_text=True,  # can reduce memory use if save_text = False
        **kwargs
    ):

        if text == "":
            raise RuntimeError(
                "Please provide text string, or use label.py for mutable text"
            )

        self._font = font

        # Scale will be passed to Group using kwargs.
        if "scale" in kwargs.keys():
            self._scale = kwargs["scale"]
        else:
            self._scale = 1

        self._line_spacing = line_spacing
        self._save_text = save_text

        if self._save_text:  # text string will be saved
            self._text = text
        else:
            self._text = None  # save a None value since text string is not saved

        # limit padding to >= 0
        padding_top = max(0, padding_top)
        padding_bottom = max(0, padding_bottom)
        padding_left = max(0, padding_left)
        padding_right = max(0, padding_right)

        # Calculate the text bounding box

        # Calculate tight box to provide bounding box dimensions to match label for
        # anchor_position calculations
        (tight_box_x, tight_box_y, x_offset, tight_y_offset) = self._text_bounding_box(
            text, font, self._line_spacing, background_tight=True,
        )

        if background_tight:
            box_x = tight_box_x
            box_y = tight_box_y
            y_offset = tight_y_offset

        else:
            (box_x, box_y, x_offset, y_offset) = self._text_bounding_box(
                text, font, self._line_spacing, background_tight=background_tight,
            )
        # Calculate the background size including padding
        box_x = box_x + padding_left + padding_right
        box_y = box_y + padding_top + padding_bottom

        # Create the two-color palette
        self.palette = displayio.Palette(2)

        self.background_color = background_color
        self.color = color

        # Create the bitmap and TileGrid
        self.bitmap = displayio.Bitmap(box_x, box_y, len(self.palette))

        # Place the text into the Bitmap
        self._place_text(
            self.bitmap,
            text,
            font,
            self._line_spacing,
            padding_left + x_offset,
            padding_top + y_offset,
        )

        label_position_yoffset = int(  # To calibrate with label.py positioning
            (
                font.get_glyph(ord("M")).height
                - text.count("\n") * font.get_bounding_box()[1] * self._line_spacing
            )
            / 2
        )

        self.tilegrid = displayio.TileGrid(
            self.bitmap,
            pixel_shader=self.palette,
            width=1,
            height=1,
            tile_width=box_x,
            tile_height=box_y,
            default_tile=0,
            x=-padding_left,
            y=label_position_yoffset - y_offset - padding_top,
        )

        # instance the Group
        # this Group will contain just one TileGrid with one contained bitmap
        super().__init__(
            max_size=1, x=x, y=y, **kwargs
        )  # this will include any arguments, including scale
        self.append(self.tilegrid)  # add the bitmap's tilegrid to the group

        # Update bounding_box values.  Note: To be consistent with label.py,
        # this is the bounding box for the text only, not including the background.

        self._bounding_box = (
            self.tilegrid.x,
            self.tilegrid.y,
            tight_box_x,
            tight_box_y,
        )

        self._anchored_position = anchored_position
        self.anchor_point = anchor_point
        self.anchored_position = (
            self._anchored_position
        )  # sets anchored_position with setter after bitmap is created

    @staticmethod
    def _line_spacing_ypixels(font, line_spacing):
        # Note: Scale is not implemented at this time, any scaling is pushed up to the Group level
        return_value = int(line_spacing * font.get_bounding_box()[1])
        return return_value

    def _text_bounding_box(
        self, text, font, line_spacing, background_tight=False
    ):  # **** change default background_tight=False

        # This empirical approach checks several glyphs for maximum ascender and descender height
        # (consistent with label.py)
        glyphs = "M j'"  # choose glyphs with highest ascender and lowest
        # descender, will depend upon font used
        ascender_max = descender_max = 0
        for char in glyphs:
            this_glyph = font.get_glyph(ord(char))
            if this_glyph:
                ascender_max = max(ascender_max, this_glyph.height + this_glyph.dy)
                descender_max = max(descender_max, -this_glyph.dy)

        lines = 1

        xposition = x_start = 0  # starting x position (left margin)
        yposition = y_start = 0

        left = right = x_start
        top = bottom = y_start

        y_offset_tight = int(
            (
                font.get_glyph(ord("M")).height
                - text.count("\n") * self._line_spacing_ypixels(font, line_spacing)
            )
            / 2
        )
        # this needs to be reviewed (also in label.py), since it doesn't respond
        # properly to the number of newlines.

        newline = False

        for char in text:

            if char == "\n":  # newline
                newline = True

            else:

                my_glyph = font.get_glyph(ord(char))

                if my_glyph is None:  # Error checking: no glyph found
                    print("Glyph not found: {}".format(repr(char)))
                else:
                    if newline:
                        newline = False
                        xposition = x_start  # reset to left column
                        yposition = yposition + self._line_spacing_ypixels(
                            font, line_spacing
                        )  # Add a newline
                        lines += 1
                    xposition += my_glyph.shift_x
                    right = max(right, xposition)

                    if yposition == y_start:  # first line, find the Ascender height
                        top = min(top, -my_glyph.height - my_glyph.dy + y_offset_tight)
                    bottom = max(bottom, yposition - my_glyph.dy + y_offset_tight)

        loose_height = (lines - 1) * self._line_spacing_ypixels(font, line_spacing) + (
            ascender_max + descender_max
        )

        label_calibration_offset = int(
            (
                font.get_glyph(ord("M")).height
                - text.count("\n") * self._line_spacing_ypixels(font, line_spacing)
            )
            / 2
        )

        y_offset_tight = -top + label_calibration_offset

        final_box_width = right - left
        if background_tight:
            final_box_height = bottom - top
            final_y_offset = y_offset_tight

        else:
            final_box_height = loose_height
            final_y_offset = ascender_max

        return (final_box_width, final_box_height, 0, final_y_offset)

    # pylint: disable=too-many-nested-blocks
    def _place_text(
        self,
        bitmap,
        text,
        font,
        line_spacing,
        xposition,
        yposition,
        text_palette_index=1,
        background_palette_index=0,
        print_only_pixels=True,  # print_only_pixels = True: only update the bitmap where the glyph
        # pixel color is > 0.  This is especially useful for script fonts where glyph
        # bounding boxes overlap
        # Set `print_only_pixels=False` to write all pixels
    ):
        # placeText - Writes text into a bitmap at the specified location.
        #
        # Verify paletteIndex is working properly with * operator, especially
        # if accommodating multicolored fonts
        #
        # Note: Scale is not implemented at this time, is pushed up to Group level

        bitmap_width = bitmap.width
        bitmap_height = bitmap.height

        x_start = xposition  # starting x position (left margin)
        y_start = yposition

        left = right = x_start
        top = bottom = y_start

        for char in text:

            if char == "\n":  # newline
                xposition = x_start  # reset to left column
                yposition = yposition + self._line_spacing_ypixels(
                    font, line_spacing
                )  # Add a newline

            else:

                my_glyph = font.get_glyph(ord(char))

                if my_glyph is None:  # Error checking: no glyph found
                    print("Glyph not found: {}".format(repr(char)))
                else:

                    right = max(right, xposition + my_glyph.shift_x)
                    if yposition == y_start:  # first line, find the Ascender height
                        top = min(top, -my_glyph.height - my_glyph.dy)
                    bottom = max(bottom, yposition - my_glyph.dy)

                    glyph_offset_x = (
                        my_glyph.tile_index * my_glyph.width
                    )  # for type BuiltinFont, this creates the x-offset in the glyph bitmap.
                    # for BDF loaded fonts, this should equal 0

                    for y in range(my_glyph.height):
                        for x in range(my_glyph.width):
                            x_placement = x + xposition + my_glyph.dx
                            y_placement = y + yposition - my_glyph.height - my_glyph.dy

                            if (bitmap_width > x_placement >= 0) and (
                                bitmap_height > y_placement >= 0
                            ):

                                # Allows for remapping the bitmap indexes using paletteIndex
                                # for background and text.
                                palette_indexes = (
                                    background_palette_index,
                                    text_palette_index,
                                )

                                this_pixel_color = palette_indexes[
                                    my_glyph.bitmap[
                                        y * my_glyph.bitmap.width + x + glyph_offset_x
                                    ]
                                ]

                                if not print_only_pixels or this_pixel_color > 0:
                                    # write all characters if printOnlyPixels = False,
                                    # or if thisPixelColor is > 0
                                    bitmap[
                                        y_placement * bitmap_width + x_placement
                                    ] = this_pixel_color
                            elif y_placement > bitmap_height:
                                break

                    xposition = xposition + my_glyph.shift_x

        return (left, top, right - left, bottom - top)  # bounding_box

    @property
    def bounding_box(self):
        """An (x, y, w, h) tuple that completely covers all glyphs. The
        first two numbers are offset from the x, y origin of this group"""
        return self._bounding_box

    @property
    def line_spacing(self):
        """The amount of space between lines of text, in multiples of the font's
        bounding-box height. (E.g. 1.0 is the bounding-box height)"""
        return self._line_spacing

    # pylint: disable=no-self-use
    @line_spacing.setter
    def line_spacing(self, new_line_spacing):
        raise RuntimeError(
            "line_spacing is immutable for bitmap_label.py; use label.py for mutable line_spacing"
        )

    @property
    def color(self):
        """Color of the text as an RGB hex number."""
        return self._color

    @color.setter
    def color(self, new_color):
        self._color = new_color
        if new_color is not None:
            self.palette[1] = new_color
            self.palette.make_opaque(1)
        else:
            self.palette[1] = 0
            self.palette.make_transparent(1)

    @property
    def background_color(self):
        """Color of the background as an RGB hex number."""
        return self._background_color

    @background_color.setter
    def background_color(self, new_color):
        self._background_color = new_color
        if new_color is not None:
            self.palette[0] = new_color
            self.palette.make_opaque(0)
        else:
            self.palette[0] = 0
            self.palette.make_transparent(0)

    @property
    def text(self):
        """Text to displayed."""
        return self._text

    # pylint: disable=no-self-use
    @text.setter
    def text(self, new_text):
        raise RuntimeError(
            "text is immutable for bitmap_label.py; use label.py library for mutable text"
        )

    @property
    def font(self):
        """Font to use for text display."""
        return self.font

    # pylint: disable=no-self-use
    @font.setter
    def font(self, new_font):
        raise RuntimeError(
            "font is immutable for bitmap_label.py; use label.py library for mutable font"
        )

    @property
    def anchor_point(self):
        """Point that anchored_position moves relative to.
           Tuple with decimal percentage of width and height.
           (E.g. (0,0) is top left, (1.0, 0.5): is middle right.)"""
        return self._anchor_point

    @anchor_point.setter
    def anchor_point(self, new_anchor_point):
        self._anchor_point = new_anchor_point
        self.anchored_position = (
            self._anchored_position
        )  # update the anchored_position using setter

    @property
    def anchored_position(self):
        """Position relative to the anchor_point. Tuple containing x,y
           pixel coordinates."""
        return self._anchored_position

    @anchored_position.setter
    def anchored_position(self, new_position):
        self._anchored_position = new_position

        # Set anchored_position
        if (self._anchor_point is not None) and (self._anchored_position is not None):
            new_x = int(
                new_position[0]
                - self._anchor_point[0] * (self._bounding_box[2] * self._scale)
            )
            new_y = int(
                new_position[1]
                - (self._anchor_point[1] * self._bounding_box[3] * self.scale)
                + round((self._bounding_box[3] * self.scale) / 2.0)
            )
            self.x = new_x
            self.y = new_y
