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

.. todo:: Add links to any specific hardware product page(s), or category page(s). Use unordered list & hyperlink rST
   inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

import displayio


def line_spacing_ypixels(font, line_spacing):
    # Note: Scale is not implemented at this time, any scaling is pushed up to the Group level
    return_value = int(line_spacing * font.get_bounding_box()[1])
    return return_value


def text_bounding_box(
    text, font, line_spacing, background_tight=False
):  # **** change default background_tight=False

    label_position_yoffset = int(  # for calibration with label.py positioning
        (font.get_glyph(ord("M")).height - font.get_bounding_box()[1] * line_spacing)
        / 2
    )

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
    font_height = ascender_max + descender_max
    font_yoffset = ascender_max

    base_point = (0, 0)  # entry point for the next glyph

    x1_min = (
        y1_min
    ) = (
        x2_max
    ) = (
        y2_max
    ) = None  # initialize the bounding box corners (1:lower left, 2: upper right)

    y_offset = None  # Provide the baseline y_offset for the bitmap

    box_height = 0
    box_width = 0
    box_height_adder = 0

    firstline = True  # handles special cases for first line

    for char in text:
        if char == "\n":  # newline
            if firstline:  # This the first line
                firstline = False
                if background_tight:
                    if (
                        y1_min is None
                    ):  # A newline was the first character of the first line
                        y_offset = 0 #label_position_yoffset
                        box_height_adder = (
                            line_spacing_ypixels(font, line_spacing - 1) + y_offset
                        )
                        # for a leading newline, this adds to the box_height

                    else:
                        y_offset = (
                            -y1_min
                        )  # The bitmap y-offset is the max y-position of the first line

                else:  # background is "loose"
                    y_offset = font_yoffset
                    if y1_min is None:
                        box_height_adder = line_spacing_ypixels(font, line_spacing)

            base_point = (
                0,
                base_point[1] + line_spacing_ypixels(font, line_spacing),
            )  # baseline point for the next glyph

        else:
            my_glyph = font.get_glyph(ord(char))
            if my_glyph == None:  # Error checking: no glyph found
                print("Glyph not found: {}".format(repr(char)))
            else:
                x1 = base_point[0]  # x1,y1 = upper left of glyph
                x2 = x1 + my_glyph.shift_x  # x2,y2 = lower right of glyph
                if background_tight:
                    y1 = base_point[1] - (
                        my_glyph.height + my_glyph.dy
                    )  # Upper left corner Note: Positive Y is down
                    y2 = y1 + my_glyph.height
                else:  # background is "loose"
                    y1 = base_point[1] - font_yoffset
                    y2 = y1 + font_height
                base_point = (
                    base_point[0] + my_glyph.shift_x,
                    base_point[1] + my_glyph.shift_y,
                )  # update the next baseline point location

                # find the min bounding box size incorporating this glyph's bounding box
                if x1_min is not None:
                    x1_min = min(x1, x1_min)
                else:
                    x1_min = min(0, x1)  # ****
                if y1_min is not None:
                    y1_min = min(y1, y1_min)
                else:
                    y1_min = y1
                if x2_max is not None:
                    x2_max = max(x2, x2_max)
                else:
                    x2_max = x2
                if y2_max is not None:
                    y2_max = max(y2, y2_max)
                else:
                    y2_max = y2

        if x1_min is not None and x2_max is not None:
            box_width = max(0, x2_max - x1_min)
        if y1_min is not None and y2_max is not None:
            box_height = y2_max - y1_min

        if firstline:  # This the first line
            if background_tight:
                y_offset = (
                    -y1_min
                )  # The bitmap y-offset is the max y-position of the first line
            else:  # background is "loose"
                y_offset = font_yoffset

    box_height = max(
        0, box_height + box_height_adder
    )  # to add any additional height for leading newlines

    return (box_width, box_height, -x1_min, y_offset)  # -x1_min is the x_offset


def place_text(
    bitmap,
    text,
    font,
    line_spacing,
    xposition,
    yposition,
    text_palette_index=1,
    background_palette_index=0,
    scale=1,
    print_only_pixels=True,  # print_only_pixels = True: only update the bitmap where the glyph
    # pixel color is > 0.  This is especially useful for script fonts where glyph
    # bounding boxes overlap
    # Set `print_only_pixels=False` to write all pixels
):
    # placeText - Writes text into a bitmap at the specified location.
    #
    # Verify paletteIndex is working properly with * operator, especially if accommodating multicolored fonts
    #
    # Note: Scale is not implemented at this time, is pushed up to Group level

    font_height = font.get_glyph(ord("M")).height

    bitmap_width = bitmap.width
    bitmap_height = bitmap.height

    x_start = xposition  # starting x position (left margin)
    y_start = yposition

    if (
        background_palette_index != 0
    ):  # the textbackground is different from the bitmap background
        # draw a bounding box where the text will go

        (ignore, font_line_height) = bounding_box(
            "M g", font, line_spacing, scale
        )  # check height with ascender and descender.
        (box_x, box_y) = bounding_box(text, font, line_spacing, scale)
        box_y = max(font_line_height, box_y)

        for y in range(box_y):
            for x in range(box_x):
                if (xposition + x < bitmap_width) and (
                    yposition + y < bitmap_height
                ):  # check boundaries
                    bitmap[
                        (yposition + y) * bitmap_width + (xposition + x)
                    ] = background_palette_index

    left = right = x_start
    top = bottom = y_start

    for char in text:

        if char == "\n":  # newline
            xposition = x_start  # reset to left column
            yposition = yposition + line_spacing_ypixels(
                font, line_spacing
            )  # Add a newline

        else:

            my_glyph = font.get_glyph(ord(char))

            if my_glyph == None:  # Error checking: no glyph found
                print("Glyph not found: {}".format(repr(char)))
            else:

                right = max(right, xposition + my_glyph.shift_x)
                if yposition == y_start:  # first line, find the Ascender height
                    top = min(top, -my_glyph.height - my_glyph.dy)
                bottom = max(bottom, yposition - my_glyph.dy)

                width = my_glyph.width
                height = my_glyph.height
                dx = my_glyph.dx
                dy = my_glyph.dy
                shift_x = my_glyph.shift_x
                shift_y = my_glyph.shift_x
                glyph_offset_x = (
                    my_glyph.tile_index * width
                )  # for type BuiltinFont, this creates the x-offset in the glyph bitmap.
                # for BDF loaded fonts, this should equal 0

                y_offset = font_height - height
                for y in range(height):
                    for x in range(width):
                        x_placement = x + xposition + dx
                        y_placement = y + yposition - height - dy

                        if (
                            (x_placement >= 0)
                            and (y_placement >= 0)
                            and (x_placement < bitmap_width)
                            and (y_placement < bitmap_height)
                        ):

                            # Allows for remapping the bitmap indexes using paletteIndex for background and text.
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
                                # write all characters if printOnlyPixels = False, or if thisPixelColor is > 0
                                bitmap[
                                    y_placement * bitmap_width + x_placement
                                ] = this_pixel_color
                        elif y_placement > bitmap_height:
                            break

                xposition = xposition + shift_x

    return (left, top, left + right, bottom - top)  # bounding_box


class Label(displayio.Group):
    # Class variable
    # To save memory, set Label._memory_saver=True and avoid storing the text string in the class.
    # If set to False, the class saves the text string for future reference. *** use getter
    _memory_saver = True

    def __init__(
        self,
        font,
        x=0,
        y=0,
        text="",
        max_glyphs=None,  # This input parameter is ignored, only present for compatibility with label.py
        # width, height,
        color=0xFFFFFF,
        background_color=None,
        line_spacing=1.25,
        background_tight=False,
        padding_top=0,
        padding_bottom=0,
        padding_left=0,
        padding_right=0,
        anchor_point=(0, 0),
        anchored_position=None,
        **kwargs
    ):

        if text == "":
            raise RuntimeError("Please provide text string")

        # Scale will be passed to Group using kwargs.
        if "scale" in kwargs.keys():
            self._scale = kwargs["scale"]
        else:
            self._scale = 1

        self._line_spacing = line_spacing

        if self._memory_saver:  # do not save the text in the instance
            self._text = None
        else:
            self._text = text  # text to be displayed

        # limit padding to >= 0 *** raise an error if negative padding is requested
        padding_top = max(0, padding_top)
        padding_bottom = max(0, padding_bottom)
        padding_left = max(0, padding_left)
        padding_right = max(0, padding_right)

        # Calculate the text bounding box

        # Calculate tight box to provide bounding box dimensions to match label for anchor_position calculations
        (tight_box_x, tight_box_y, dummy_x_offset, tight_y_offset) = text_bounding_box(
            text, font, self._line_spacing, background_tight=True,
        )

        if background_tight:
            box_x = tight_box_x
            box_y = tight_box_y
            x_offset = dummy_x_offset
            y_offset = tight_y_offset
        else:
            (box_x, box_y, x_offset, y_offset) = text_bounding_box(
                text, font, self._line_spacing, background_tight=background_tight,
            )
        # Calculate the background size including padding
        box_x = box_x + padding_left + padding_right
        box_y = box_y + padding_top + padding_bottom

        # Create the two-color palette
        self.palette = displayio.Palette(2)
        if background_color is not None:
            self.palette[0] = background_color
        else:
            self.palette[0] = 0
            self.palette.make_transparent(0)
        self.palette[1] = color

        # Create the bitmap and TileGrid
        self.bitmap = displayio.Bitmap(box_x, box_y, len(self.palette))

        # Place the text into the Bitmap
        text_size = place_text(
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
                - font.get_bounding_box()[1] * self._line_spacing
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
            #y=label_position_yoffset - y_offset - padding_left,
            y= - y_offset - padding_left,
        )

        # instance the Group with super...    super().__init__(
        # this Group will contain just one TileGrid with one contained bitmap
        super().__init__(
            max_size=1, x=x, y=y, **kwargs
        )  # this will include any arguments, including scale
        self.append(self.tilegrid)  # add the bitmap's tilegrid to the group

        #######  *******
        # Set the tileGrid position in the parent based upon anchor_point and anchor_position
        # **** Should scale affect the placement of anchor_position?

        self.bounding_box = (
            self.tilegrid.x,
            self.tilegrid.y + (y_offset - tight_y_offset),
            tight_box_x,
            tight_box_y,
        )
        # Update bounding_box values.  Note: To be consistent with label.py,
        # this is the bounding box for the text only, not including the background.
        # ******** Need repair
        # Create the TileGrid to hold the single Bitmap (self.bitmap)

        self._anchored_position = anchored_position
        self.anchor_point = anchor_point
        self.anchored_position = (
            self._anchored_position
        )  # sets anchored_position with setter after bitmap is created

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
        return self._anchored_position

    @anchored_position.setter
    def anchored_position(self, new_position):

        self._anchored_position = new_position

        # Set anchored_position
        if (self._anchor_point is not None) and (self._anchored_position is not None):
            new_x = int(
                new_position[0]
                - self._anchor_point[0] * (self.bounding_box[2] * self._scale)
            )
            new_y = int(
                new_position[1]
                - (self._anchor_point[1] * self.bounding_box[3] * self.scale)
                + round((self.bounding_box[3] * self.scale) / 2.0)
            )
            self.x = new_x
            self.y = new_y
