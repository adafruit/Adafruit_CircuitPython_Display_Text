# SPDX-FileCopyrightText: 2020 Kevin Matocha
#
# SPDX-License-Identifier: MIT

"""
`adafruit_display_text.bitmap_label`
================================================================================

Text graphics handling for CircuitPython, including text boxes


* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Text.git"


try:
    from typing import Tuple
except ImportError:
    pass

import displayio

from adafruit_display_text import LabelBase


class Label(LabelBase):
    """A label displaying a string of text that is stored in a bitmap.
    Note: This ``bitmap_label.py`` library utilizes a bitmap to display the text.
    This method is memory-conserving relative to ``label.py``.

    For further reduction in memory usage, set ``save_text=False`` (text string will not
    be stored and ``line_spacing`` and ``font`` are immutable with ``save_text``
    set to ``False``).

    The origin point set by ``x`` and ``y``
    properties will be the left edge of the bounding box, and in the center of a M
    glyph (if its one line), or the (number of lines * linespacing + M)/2. That is,
    it will try to have it be center-left as close as possible.

    :param Font font: A font class that has ``get_bounding_box`` and ``get_glyph``.
      Must include a capital M for measuring character size.
    :param str text: Text to display
    :param int color: Color of all text in RGB hex
    :param int background_color: Color of the background, use `None` for transparent
    :param float line_spacing: Line spacing of text to display
    :param bool background_tight: Set `True` only if you want background box to tightly
     surround text. When set to 'True' Padding parameters will be ignored.
    :param int padding_top: Additional pixels added to background bounding box at top
    :param int padding_bottom: Additional pixels added to background bounding box at bottom
    :param int padding_left: Additional pixels added to background bounding box at left
    :param int padding_right: Additional pixels added to background bounding box at right
    :param (float,float) anchor_point: Point that anchored_position moves relative to.
     Tuple with decimal percentage of width and height.
     (E.g. (0,0) is top left, (1.0, 0.5): is middle right.)
    :param (int,int) anchored_position: Position relative to the anchor_point. Tuple
     containing x,y pixel coordinates.
    :param int scale: Integer value of the pixel scaling
    :param bool save_text: Set True to save the text string as a constant in the
     label structure.  Set False to reduce memory use.
    :param bool base_alignment: when True allows to align text label to the baseline.
     This is helpful when two or more labels need to be aligned to the same baseline
    :param (int,str) tab_replacement: tuple with tab character replace information. When
     (4, " ") will indicate a tab replacement of 4 spaces, defaults to 4 spaces by
     tab character
    :param str label_direction: string defining the label text orientation. There are 5
     configurations possibles ``LTR``-Left-To-Right ``RTL``-Right-To-Left
     ``UPD``-Upside Down ``UPR``-Upwards ``DWR``-Downwards. It defaults to ``LTR``"""

    def __init__(self, font, save_text=True, **kwargs) -> None:

        self._bitmap = None

        super().__init__(font, **kwargs)

        self._save_text = save_text
        self._text = self._replace_tabs(self._text)

        if self._label_direction == "RTL":
            self._text = "".join(reversed(self._text))

        # call the text updater with all the arguments.
        self._reset_text(
            font=font,
            text=self._text,
            line_spacing=self._line_spacing,
            scale=self.scale,
        )

    def _reset_text(
        self,
        font=None,
        text: str = None,
        line_spacing: float = None,
        scale: int = None,
    ) -> None:
        # pylint: disable=too-many-branches, too-many-statements

        # Store all the instance variables
        if font is not None:
            self._font = font
        if line_spacing is not None:
            self._line_spacing = line_spacing

        # if text is not provided as a parameter (text is None), use the previous value.
        if (text is None) and self._save_text:
            text = self._text

        if self._save_text:  # text string will be saved
            self._text = self._replace_tabs(text)
            if self._label_direction == "RTL":
                self._text = "".join(reversed(self._text))
        else:
            self._text = None  # save a None value since text string is not saved

        # Check for empty string
        if (text == "") or (
            text is None
        ):  # If empty string, just create a zero-sized bounding box and that's it.

            self._bounding_box = (
                0,
                0,
                0,  # zero width with text == ""
                0,  # zero height with text == ""
            )
            # Clear out any items in the self._local_group Group, in case this is an
            # update to the bitmap_label
            for _ in self._local_group:
                self._local_group.pop(0)

        else:  # The text string is not empty, so create the Bitmap and TileGrid and
            # append to the self Group

            # Calculate the text bounding box

            # Calculate both "tight" and "loose" bounding box dimensions to match label for
            # anchor_position calculations
            (
                box_x,
                tight_box_y,
                x_offset,
                tight_y_offset,
                loose_box_y,
                loose_y_offset,
            ) = self._text_bounding_box(
                self._text,
                self._font,
            )  # calculate the box size for a tight and loose backgrounds

            if self._background_tight:
                box_y = tight_box_y
                y_offset = tight_y_offset

            else:  # calculate the box size for a loose background
                box_y = loose_box_y
                y_offset = loose_y_offset

            # Calculate the background size including padding
            box_x = box_x + self._padding_left + self._padding_right
            box_y = box_y + self._padding_top + self._padding_bottom

            # Create the bitmap and TileGrid
            self._bitmap = displayio.Bitmap(box_x, box_y, len(self._palette))

            # Place the text into the Bitmap
            self._place_text(
                self._bitmap,
                self._text,
                self._font,
                self._padding_left - x_offset,
                self._padding_top + y_offset,
            )

            if self._base_alignment:
                label_position_yoffset = 0
            else:
                label_position_yoffset = self._ascent // 2

            self._tilegrid = displayio.TileGrid(
                self._bitmap,
                pixel_shader=self._palette,
                width=1,
                height=1,
                tile_width=box_x,
                tile_height=box_y,
                default_tile=0,
                x=-self._padding_left + x_offset,
                y=label_position_yoffset - y_offset - self._padding_top,
            )

            if self._label_direction == "UPR":
                self._tilegrid.transpose_xy = True
                self._tilegrid.flip_x = True
            if self._label_direction == "DWR":
                self._tilegrid.transpose_xy = True
                self._tilegrid.flip_y = True
            if self._label_direction == "UPD":
                self._tilegrid.flip_x = True
                self._tilegrid.flip_y = True

            # Clear out any items in the local_group Group, in case this is an update to
            # the bitmap_label
            for _ in self._local_group:
                self._local_group.pop(0)
            self._local_group.append(
                self._tilegrid
            )  # add the bitmap's tilegrid to the group

            # Update bounding_box values.  Note: To be consistent with label.py,
            # this is the bounding box for the text only, not including the background.
            if self._label_direction in ("UPR", "DWR"):
                self._bounding_box = (
                    self._tilegrid.x,
                    self._tilegrid.y,
                    tight_box_y,
                    box_x,
                )
            else:
                self._bounding_box = (
                    self._tilegrid.x,
                    self._tilegrid.y,
                    box_x,
                    tight_box_y,
                )

        if (
            scale is not None
        ):  # Scale will be defined in local_group (Note: self should have scale=1)
            self.scale = scale  # call the setter

        # set the anchored_position with setter after bitmap is created, sets the
        # x,y positions of the label
        self.anchored_position = self._anchored_position

    @staticmethod
    def _line_spacing_ypixels(font, line_spacing: float) -> int:
        # Note: Scaling is provided at the Group level
        return_value = int(line_spacing * font.get_bounding_box()[1])
        return return_value

    def _text_bounding_box(
        self, text: str, font
    ) -> Tuple[int, int, int, int, int, int]:
        # pylint: disable=too-many-locals

        ascender_max, descender_max = self._ascent, self._descent

        lines = 1

        xposition = (
            x_start
        ) = yposition = y_start = 0  # starting x and y position (left margin)

        left = None
        right = x_start
        top = bottom = y_start

        y_offset_tight = self._ascent // 2

        newline = False
        line_spacing = self._line_spacing

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
                    if xposition == x_start:
                        if left is None:
                            left = my_glyph.dx
                        else:
                            left = min(left, my_glyph.dx)
                    xright = xposition + my_glyph.width + my_glyph.dx
                    xposition += my_glyph.shift_x

                    right = max(right, xposition, xright)

                    if yposition == y_start:  # first line, find the Ascender height
                        top = min(top, -my_glyph.height - my_glyph.dy + y_offset_tight)
                    bottom = max(bottom, yposition - my_glyph.dy + y_offset_tight)

        if left is None:
            left = 0

        final_box_width = right - left

        final_box_height_tight = bottom - top
        final_y_offset_tight = -top + y_offset_tight

        final_box_height_loose = (lines - 1) * self._line_spacing_ypixels(
            font, line_spacing
        ) + (ascender_max + descender_max)
        final_y_offset_loose = ascender_max

        # return (final_box_width, final_box_height, left, final_y_offset)

        return (
            final_box_width,
            final_box_height_tight,
            left,
            final_y_offset_tight,
            final_box_height_loose,
            final_y_offset_loose,
        )

    def _place_text(
        self,
        bitmap,
        text: str,
        font,
        xposition: int,
        yposition: int,
        skip_index: int = 0,  # set to None to write all pixels, other wise skip this palette index
        # when copying glyph bitmaps (this is important for slanted text
        # where rectangular glyph boxes overlap)
    ) -> Tuple[int, int, int, int]:
        # pylint: disable=too-many-arguments, too-many-locals

        # placeText - Writes text into a bitmap at the specified location.
        #
        # Note: scale is pushed up to Group level

        x_start = xposition  # starting x position (left margin)
        y_start = yposition

        left = None
        right = x_start
        top = bottom = y_start
        line_spacing = self._line_spacing

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
                    if xposition == x_start:
                        if left is None:
                            left = my_glyph.dx
                        else:
                            left = min(left, my_glyph.dx)

                    right = max(
                        right,
                        xposition + my_glyph.shift_x,
                        xposition + my_glyph.width + my_glyph.dx,
                    )
                    if yposition == y_start:  # first line, find the Ascender height
                        top = min(top, -my_glyph.height - my_glyph.dy)
                    bottom = max(bottom, yposition - my_glyph.dy)

                    glyph_offset_x = (
                        my_glyph.tile_index * my_glyph.width
                    )  # for type BuiltinFont, this creates the x-offset in the glyph bitmap.
                    # for BDF loaded fonts, this should equal 0

                    y_blit_target = yposition - my_glyph.height - my_glyph.dy

                    # Clip glyph y-direction if outside the font ascent/descent metrics.
                    # Note: bitmap.blit will automatically clip the bottom of the glyph.
                    y_clip = 0
                    if y_blit_target < 0:
                        y_clip = -y_blit_target  # clip this amount from top of bitmap
                        y_blit_target = 0  # draw the clipped bitmap at y=0

                        print(
                            'Warning: Glyph clipped, exceeds Ascent property: "{}"'.format(
                                char
                            )
                        )

                    if (y_blit_target + my_glyph.height) > bitmap.height:
                        print(
                            'Warning: Glyph clipped, exceeds descent property: "{}"'.format(
                                char
                            )
                        )

                    self._blit(
                        bitmap,
                        xposition + my_glyph.dx,
                        y_blit_target,
                        my_glyph.bitmap,
                        x_1=glyph_offset_x,
                        y_1=y_clip,
                        x_2=glyph_offset_x + my_glyph.width,
                        y_2=my_glyph.height,
                        skip_index=skip_index,  # do not copy over any 0 background pixels
                    )

                    xposition = xposition + my_glyph.shift_x

        # bounding_box
        return left, top, right - left, bottom - top

    def _blit(
        self,
        bitmap,  # target bitmap
        x: int,  # target x upper left corner
        y: int,  # target y upper left corner
        source_bitmap,  # source bitmap
        x_1: int = 0,  # source x start
        y_1: int = 0,  # source y start
        x_2: int = None,  # source x end
        y_2: int = None,  # source y end
        skip_index: int = None,  # palette index that will not be copied
        # (for example: the background color of a glyph)
    ) -> None:
        # pylint: disable=no-self-use, too-many-arguments

        if hasattr(bitmap, "blit"):  # if bitmap has a built-in blit function, call it
            # this function should perform its own input checks
            bitmap.blit(
                x,
                y,
                source_bitmap,
                x1=x_1,
                y1=y_1,
                x2=x_2,
                y2=y_2,
                skip_index=skip_index,
            )

        else:  # perform pixel by pixel copy of the bitmap

            # Perform input checks

            if x_2 is None:
                x_2 = source_bitmap.width
            if y_2 is None:
                y_2 = source_bitmap.height

            # Rearrange so that x_1 < x_2 and y1 < y2
            if x_1 > x_2:
                x_1, x_2 = x_2, x_1
            if y_1 > y_2:
                y_1, y_2 = y_2, y_1

            # Ensure that x2 and y2 are within source bitmap size
            x_2 = min(x_2, source_bitmap.width)
            y_2 = min(y_2, source_bitmap.height)

            for y_count in range(y_2 - y_1):
                for x_count in range(x_2 - x_1):
                    x_placement = x + x_count
                    y_placement = y + y_count

                    if (bitmap.width > x_placement >= 0) and (
                        bitmap.height > y_placement >= 0
                    ):  # ensure placement is within target bitmap

                        # get the palette index from the source bitmap
                        this_pixel_color = source_bitmap[
                            y_1
                            + (
                                y_count * source_bitmap.width
                            )  # Direct index into a bitmap array is speedier than [x,y] tuple
                            + x_1
                            + x_count
                        ]

                        if (skip_index is None) or (this_pixel_color != skip_index):
                            bitmap[  # Direct index into a bitmap array is speedier than [x,y] tuple
                                y_placement * bitmap.width + x_placement
                            ] = this_pixel_color
                    elif y_placement > bitmap.height:
                        break

    def _set_line_spacing(self, new_line_spacing: float) -> None:
        if self._save_text:
            self._reset_text(line_spacing=new_line_spacing, scale=self.scale)
        else:
            raise RuntimeError("line_spacing is immutable when save_text is False")

    def _set_font(self, new_font) -> None:
        self._font = new_font
        if self._save_text:
            self._reset_text(font=new_font, scale=self.scale)
        else:
            raise RuntimeError("font is immutable when save_text is False")

    def _set_text(self, new_text: str, scale: int) -> None:
        self._reset_text(text=self._replace_tabs(new_text), scale=self.scale)

    def _set_background_color(self, new_color):
        self._background_color = new_color
        if new_color is not None:
            self._palette[0] = new_color
            self._palette.make_opaque(0)
        else:
            self._palette[0] = 0
            self._palette.make_transparent(0)

    def _set_label_direction(self, new_label_direction: str) -> None:
        self._label_direction = new_label_direction
        self._reset_text(text=str(self._text))  # Force a recalculation

    def _get_valid_label_directions(self) -> Tuple[str, ...]:
        return "LTR", "RTL", "UPD", "UPR", "DWR"
