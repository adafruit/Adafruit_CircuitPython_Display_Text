# SPDX-FileCopyrightText: 2020 Kevin Matocha
# SPDX-FileCopyrightText: 2025 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_display_text.bitmap_label`
================================================================================

Text graphics handling for CircuitPython, including text boxes


* Author(s): Kevin Matocha, Tim Cocks

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Text.git"

import adafruit_ticks
import displayio
from micropython import const

from adafruit_display_text import LabelBase

try:
    import bitmaptools
except ImportError:
    # We have a slower fallback for bitmaptools
    pass

try:
    from typing import Optional, Tuple

    from fontio import FontProtocol
except ImportError:
    pass

# constant indexes for accent_ranges
ACCENT_START = const(0)
ACCENT_END = const(1)
ACCENT_FG = const(2)
ACCENT_BG = const(3)
ACCENT_TYPE = const(4)


class Label(LabelBase):
    """A label displaying a string of text that is stored in a bitmap.
    Note: This ``bitmap_label.py`` library utilizes a :py:class:`~displayio.Bitmap`
    to display the text. This method is memory-conserving relative to ``label.py``.

    For further reduction in memory usage, set ``save_text=False`` (text string will not
    be stored and ``line_spacing`` and ``font`` are immutable with ``save_text``
    set to ``False``).

    The origin point set by ``x`` and ``y``
    properties will be the left edge of the bounding box, and in the center of a M
    glyph (if its one line), or the (number of lines * linespacing + M)/2. That is,
    it will try to have it be center-left as close as possible.

    Optionally supports:
      - Accented ranges of text with different colors
      - Outline stroke around the text
      - Fixed-width scrolling "marquee"

    :param font: A font class that has ``get_bounding_box`` and ``get_glyph``.
      Must include a capital M for measuring character size.
    :type font: ~fontio.FontProtocol
    :param str text: The full text to show in the label. If this is longer than
     ``max_characters`` then the label will scroll to show everything.
    :param int|Tuple(int, int, int) color: Color of all text in HEX or RGB
    :param int|Tuple(int, int, int)|None background_color: Color of the background, use `None`
     for transparent
    :param float line_spacing: Line spacing of text to display
    :param bool background_tight: Set `True` only if you want background box to tightly
     surround text. When set to 'True' Padding parameters will be ignored.
    :param int padding_top: Additional pixels added to background bounding box at top
    :param int padding_bottom: Additional pixels added to background bounding box at bottom
    :param int padding_left: Additional pixels added to background bounding box at left
    :param int padding_right: Additional pixels added to background bounding box at right
    :param Tuple(float, float) anchor_point: Point that anchored_position moves relative to.
     Tuple with decimal percentage of width and height.
     (E.g. (0,0) is top left, (1.0, 0.5): is middle right.)
    :param Tuple(int, int) anchored_position: Position relative to the anchor_point. Tuple
     containing x,y pixel coordinates.
    :param int scale: Integer value of the pixel scaling
    :param bool save_text: Set True to save the text string as a constant in the
     label structure.  Set False to reduce memory use.
    :param bool base_alignment: when True allows to align text label to the baseline.
     This is helpful when two or more labels need to be aligned to the same baseline
    :param Tuple(int, str) tab_replacement: tuple with tab character replace information. When
     (4, " ") will indicate a tab replacement of 4 spaces, defaults to 4 spaces by
     tab character
    :param str label_direction: string defining the label text orientation. There are 5
     configurations possibles ``LTR``-Left-To-Right ``RTL``-Right-To-Left
     ``UPD``-Upside Down ``UPR``-Upwards ``DWR``-Downwards. It defaults to ``LTR``
    :param bool verbose: print debugging information in some internal functions. Default to False
    :param Optional[Union[Tuple, int]] outline_color: The color of the outline stroke
      as RGB tuple, or hex.
    :param int outline_size: The size in pixels of the outline stroke.
      Defaults to 1 pixel.
    :param Optional[displayio.Palette] color_palette: The palette to use for the Label.
      Indexes 0, 1, and 2 will be filled with background, foreground, and outline colors
      automatically. Indexes 3 and above can be used for accent colors.
    :param Optional[int] max_characters: The number of characters that sets the fixed-width.
      Default is None for unlimited width and no scrolling

    :param float animate_time: The number of seconds in between scrolling animation
     frames. Default is 0.3 seconds.
    :param int current_index: The index of the first visible character in the label.
     Default is 0, the first character. Will increase while scrolling.

    """

    # This maps label_direction to TileGrid's transpose_xy, flip_x, flip_y
    _DIR_MAP = {
        "UPR": (True, True, False),
        "DWR": (True, False, True),
        "UPD": (False, True, True),
        "LTR": (False, False, False),
        "RTL": (False, False, False),
    }

    def __init__(
        self,
        font: FontProtocol,
        save_text: bool = True,
        color_palette: Optional[displayio.Palette] = None,
        outline_color: Optional[int] = None,
        outline_size: int = 1,
        max_characters: Optional[int] = None,
        animate_time: float = 0.3,
        current_index: int = 0,
        **kwargs,
    ) -> None:
        self._bitmap = None
        self._tilegrid = None
        self._prev_label_direction = None

        if outline_color is not None:
            if "padding_top" not in kwargs:
                kwargs["padding_top"] = outline_size
            if "padding_bottom" not in kwargs:
                kwargs["padding_bottom"] = outline_size
            if "padding_left" not in kwargs:
                kwargs["padding_left"] = outline_size
            if "padding_right" not in kwargs:
                kwargs["padding_right"] = outline_size

        super().__init__(font, **kwargs)

        self.animate_time = animate_time
        self._current_index = current_index
        self._last_animate_time = -1
        self._max_characters = max_characters

        if color_palette is not None:
            if len(color_palette) <= 3:
                raise ValueError(
                    "color_palette should be at least 4 colors to "
                    "provide enough for normal, accented, and outlined text. "
                    "color_palette argument can be omitted if not "
                    "using accents."
                )
            self._palette = color_palette
            self.color = self._color
            self.background_color = self._background_color
        else:
            _background_color = self._palette[0]
            _foreground_color = self._palette[1]
            _background_is_transparent = self._palette.is_transparent(0)
            self._palette = displayio.Palette(3)
            self._palette[0] = _background_color
            self._palette[1] = _foreground_color
            self._palette[2] = outline_color if outline_color is not None else 0x999999
            if _background_is_transparent:
                self._palette.make_transparent(0)

        # accent handling vars
        self._accent_ranges = []
        self._tmp_glyph_bitmap = None

        # outline handling vars
        self._outline_size = outline_size
        self._outline_color = outline_color
        self._init_outline_stamp(outline_size)

        self._save_text = save_text
        self._text = self._replace_tabs(self._text)

        if "text" in kwargs:
            text = kwargs["text"]
        else:
            text = ""
        if self._max_characters is not None:
            if text and text[-1] != " " and len(text) > max_characters:
                text = f"{text} "
        self._full_text = text

        self.update(True)

    def _init_outline_stamp(self, outline_size):
        self._outline_size = outline_size
        self._stamp_source = displayio.Bitmap((outline_size * 2) + 1, (outline_size * 2) + 1, 3)
        self._stamp_source.fill(2)

    def _reset_text(
        self,
        font: Optional[FontProtocol] = None,
        text: Optional[str] = None,
        line_spacing: Optional[float] = None,
        scale: Optional[int] = None,
    ) -> None:
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
        else:
            self._text = None  # save a None value since text string is not saved

        # Check for empty string
        if (not text) or (
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

            # Free the bitmap and tilegrid since they are removed
            self._bitmap = None
            self._tilegrid = None

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
                text,
                self._font,
            )  # calculate the box size for a tight and loose backgrounds

            if self._background_tight:
                box_y = tight_box_y
                y_offset = tight_y_offset
                self._padding_left = 0
                self._padding_right = 0
                self._padding_top = 0
                self._padding_bottom = 0

            else:  # calculate the box size for a loose background
                box_y = loose_box_y
                y_offset = loose_y_offset

            # Calculate the background size including padding
            tight_box_x = box_x
            box_x = box_x + self._padding_left + self._padding_right
            box_y = box_y + self._padding_top + self._padding_bottom

            if self._outline_color is not None:
                box_x += self._outline_size * 2
                box_y += self._outline_size * 2

            # Create the Bitmap unless it can be reused
            new_bitmap = None
            if self._bitmap is None or self._bitmap.width != box_x or self._bitmap.height != box_y:
                new_bitmap = displayio.Bitmap(box_x, box_y, len(self._palette))
                self._bitmap = new_bitmap
            else:
                self._bitmap.fill(0)

            # Place the text into the Bitmap
            self._place_text(
                self._bitmap,
                text if self._label_direction != "RTL" else "".join(reversed(text)),
                self._font,
                self._padding_left - x_offset,
                self._padding_top + y_offset,
            )

            if self._base_alignment:
                label_position_yoffset = 0
            else:
                label_position_yoffset = self._ascent // 2

            # Create the TileGrid if not created bitmap unchanged
            if self._tilegrid is None or new_bitmap:
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
                # Clear out any items in the local_group Group, in case this is an update to
                # the bitmap_label
                for _ in self._local_group:
                    self._local_group.pop(0)
                self._local_group.append(self._tilegrid)  # add the bitmap's tilegrid to the group

            # Set TileGrid properties based on label_direction
            if self._label_direction != self._prev_label_direction:
                tg1 = self._tilegrid
                tg1.transpose_xy, tg1.flip_x, tg1.flip_y = self._DIR_MAP[self._label_direction]

            # Update bounding_box values.  Note: To be consistent with label.py,
            # this is the bounding box for the text only, not including the background.
            if self._label_direction in {"UPR", "DWR"}:
                if self._label_direction == "UPR":
                    top = self._padding_right
                    left = self._padding_top
                if self._label_direction == "DWR":
                    top = self._padding_left
                    left = self._padding_bottom
                self._bounding_box = (
                    self._tilegrid.x + left,
                    self._tilegrid.y + top,
                    tight_box_y,
                    tight_box_x,
                )
            else:
                self._bounding_box = (
                    self._tilegrid.x + self._padding_left,
                    self._tilegrid.y + self._padding_top,
                    tight_box_x,
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
    def _line_spacing_ypixels(font: FontProtocol, line_spacing: float) -> int:
        # Note: Scaling is provided at the Group level
        return_value = int(line_spacing * font.get_bounding_box()[1])
        return return_value

    def _text_bounding_box(
        self, text: str, font: FontProtocol
    ) -> Tuple[int, int, int, int, int, int]:
        bbox = font.get_bounding_box()
        if len(bbox) == 4:
            ascender_max, descender_max = bbox[1], -bbox[3]
        else:
            ascender_max, descender_max = self._ascent, self._descent

        lines = 1

        # starting x and y position (left margin)
        xposition = x_start = yposition = y_start = 0

        left = None
        right = x_start
        top = bottom = y_start

        y_offset_tight = self._ascent // 2

        newlines = 0
        line_spacing = self._line_spacing

        for char_index in range(len(text)):
            char = text[char_index]
            if char == "\n":  # newline
                newlines += 1

            else:
                my_glyph = font.get_glyph(ord(char))

                if my_glyph is None:  # Error checking: no glyph found
                    print(f"Glyph not found: {repr(char)}")
                else:
                    if newlines:
                        xposition = x_start  # reset to left column
                        yposition += (
                            self._line_spacing_ypixels(font, line_spacing) * newlines
                        )  # Add the newline(s)
                        lines += newlines
                        newlines = 0
                    if xposition == x_start:
                        if left is None:
                            left = 0
                        else:
                            left = min(left, my_glyph.dx)
                    xright = xposition + my_glyph.width + my_glyph.dx
                    xposition += my_glyph.shift_x

                    for accent in self.accent_ranges:
                        if accent[ACCENT_TYPE] == "outline":
                            if accent[ACCENT_START] <= char_index < accent[ACCENT_END]:
                                xposition += self.outline_size

                    right = max(right, xposition, xright)

                    if yposition == y_start:  # first line, find the Ascender height
                        top = min(top, -my_glyph.height - my_glyph.dy + y_offset_tight)
                    bottom = max(bottom, yposition - my_glyph.dy + y_offset_tight)

        if left is None:
            left = 0

        final_box_width = right - left

        final_box_height_tight = bottom - top
        final_y_offset_tight = -top + y_offset_tight

        final_box_height_loose = (lines - 1) * self._line_spacing_ypixels(font, line_spacing) + (
            ascender_max + descender_max
        )
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
        bitmap: displayio.Bitmap,
        text: str,
        font: FontProtocol,
        xposition: int,
        yposition: int,
        skip_index: int = 0,  # set to None to write all pixels, other wise skip this palette index
        # when copying glyph bitmaps (this is important for slanted text
        # where rectangular glyph boxes overlap)
    ) -> Tuple[int, int, int, int]:
        # placeText - Writes text into a bitmap at the specified location.
        #
        # Note: scale is pushed up to Group level

        x_start = xposition  # starting x position (left margin)
        y_start = yposition

        left = None
        right = x_start
        top = bottom = y_start
        line_spacing = self._line_spacing

        for char_idx in range(len(text)):
            char = text[char_idx]
            if char == "\n":  # newline
                xposition = x_start  # reset to left column
                yposition = yposition + self._line_spacing_ypixels(
                    font, line_spacing
                )  # Add a newline

            else:
                my_glyph = font.get_glyph(ord(char))
                if self._tmp_glyph_bitmap is None and len(self._accent_ranges) > 0:
                    self._tmp_glyph_bitmap = displayio.Bitmap(
                        my_glyph.width + self.outline_size * 2,
                        my_glyph.height + self.outline_size * 2,
                        len(self._palette),
                    )

                if my_glyph is None:  # Error checking: no glyph found
                    print(f"Glyph not found: {repr(char)}")
                else:
                    if xposition == x_start:
                        if left is None:
                            left = 0
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
                        if self._verbose:
                            print(f'Warning: Glyph clipped, exceeds Ascent property: "{char}"')

                    if (y_blit_target + my_glyph.height) > bitmap.height:
                        if self._verbose:
                            print(f'Warning: Glyph clipped, exceeds descent property: "{char}"')

                    accented = False
                    accent_type = "foreground_background"
                    if len(self._accent_ranges) > 0:
                        for accent_range in self._accent_ranges:
                            if (
                                accent_range[ACCENT_START]
                                <= (self.current_index + char_idx) % len(self._full_text)
                                < accent_range[ACCENT_END]
                            ):
                                accent_type = accent_range[ACCENT_TYPE]
                                if accent_range[ACCENT_TYPE] == "foreground_background":
                                    self._tmp_glyph_bitmap.fill(accent_range[ACCENT_BG])

                                    bitmaptools.blit(
                                        self._tmp_glyph_bitmap,
                                        my_glyph.bitmap,
                                        0,
                                        0,
                                        x1=glyph_offset_x,
                                        y1=y_clip,
                                        x2=glyph_offset_x + my_glyph.width,
                                        y2=my_glyph.height,
                                        skip_source_index=0,
                                    )
                                    bitmaptools.replace_color(
                                        self._tmp_glyph_bitmap, 1, accent_range[ACCENT_FG]
                                    )
                                    accented = True
                                elif accent_range[ACCENT_TYPE] == "outline":
                                    self._tmp_glyph_bitmap.fill(0)
                                    bitmaptools.blit(
                                        self._tmp_glyph_bitmap,
                                        my_glyph.bitmap,
                                        self._outline_size,
                                        self._outline_size,
                                        x1=glyph_offset_x,
                                        y1=y_clip,
                                        x2=glyph_offset_x + my_glyph.width,
                                        y2=my_glyph.height,
                                        skip_source_index=0,
                                    )
                                    self._add_outline(self._tmp_glyph_bitmap)
                                    bitmaptools.replace_color(
                                        self._tmp_glyph_bitmap, 1, accent_range[ACCENT_FG]
                                    )
                                    bitmaptools.replace_color(
                                        self._tmp_glyph_bitmap, 2, accent_range[ACCENT_BG]
                                    )
                                    accented = True

                                # only one accent range can effect a given character
                                break

                    if (
                        not accented
                        and self._has_outline_accent()
                        or accented
                        and accent_type == "foreground_background"
                    ):
                        y_blit_target += self._outline_size

                    if accented:
                        try:
                            bitmaptools.blit(
                                bitmap,
                                self._tmp_glyph_bitmap,
                                max(xposition + my_glyph.dx, 0),
                                y_blit_target,
                            )
                        except ValueError:
                            # It's possible to overshoot the width of the bitmap if max_characters
                            # is enabled and outline is used on at least some of the text.
                            # In this case just skip any characters that fall outside the
                            # max_characters box size without accounting for outline size.
                            pass
                    else:
                        try:
                            self._blit(
                                bitmap,
                                max(xposition + my_glyph.dx, 0),
                                y_blit_target,
                                my_glyph.bitmap if not accented else self._tmp_glyph_bitmap,
                                x_1=glyph_offset_x,
                                y_1=y_clip,
                                x_2=glyph_offset_x + my_glyph.width,
                                y_2=my_glyph.height,
                                skip_index=skip_index
                                if not accented
                                else None,  # do not copy any 0 background pixels if not accented
                            )
                        except ValueError:
                            # It's possible to overshoot the width of the bitmap if max_characters
                            # is enabled and outline is used on at least some of the text.
                            # In this case just skip any characters that fall outside the
                            # max_characters box size without accounting for outline size.
                            pass

                    if accented and accent_type == "outline":
                        xposition = xposition + my_glyph.shift_x + self._outline_size
                    else:
                        xposition = xposition + my_glyph.shift_x

        self._add_outline(self.bitmap)
        # bounding_box
        return left, top, right - left, bottom - top

    def _add_outline(self, bitmap):
        """
        Blit the outline into the labels Bitmap. Will blit self._stamp_source for each
        pixel of the foreground color but skip the foreground color when we blit,
        creating an outline.
        :return: None
        """
        if bitmap is not self.bitmap or self._outline_color is not None:
            for y in range(bitmap.height):
                for x in range(bitmap.width):
                    if bitmap[x, y] == 1:
                        try:
                            bitmaptools.blit(
                                bitmap,
                                self._stamp_source,
                                x - self._outline_size,
                                y - self._outline_size,
                                skip_dest_index=1,
                            )
                        except ValueError as value_error:
                            raise ValueError(
                                "Padding must be big enough to fit outline_size "
                                "all the way around the text. "
                                "Try using either larger padding sizes, or smaller outline_size."
                            ) from value_error

    def _has_outline_accent(self):
        for accent in self._accent_ranges:
            if accent[ACCENT_TYPE] == "outline":
                return True
        return False

    def _blit(
        self,
        bitmap: displayio.Bitmap,  # target bitmap
        x: int,  # target x upper left corner
        y: int,  # target y upper left corner
        source_bitmap: displayio.Bitmap,  # source bitmap
        x_1: int = 0,  # source x start
        y_1: int = 0,  # source y start
        x_2: int = None,  # source x end
        y_2: int = None,  # source y end
        skip_index: int = None,  # palette index that will not be copied
        # (for example: the background color of a glyph)
    ) -> None:
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
        elif hasattr(bitmaptools, "blit"):
            bitmaptools.blit(
                bitmap,
                source_bitmap,
                x,
                y,
                x1=x_1,
                y1=y_1,
                x2=x_2,
                y2=y_2,
                skip_source_index=skip_index,
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

    def _set_font(self, new_font: FontProtocol) -> None:
        self._font = new_font
        if self._save_text:
            self._reset_text(font=new_font, scale=self.scale)
        else:
            raise RuntimeError("font is immutable when save_text is False")

    def _set_text(self, new_text: str, scale: int) -> None:
        self._reset_text(text=self._replace_tabs(new_text), scale=self.scale)

    def _set_background_color(self, new_color: Optional[int]):
        self._background_color = new_color
        if new_color is not None:
            self._palette[0] = new_color
            self._palette.make_opaque(0)
        else:
            self._palette[0] = 0
            self._palette.make_transparent(0)

    def _set_label_direction(self, new_label_direction: str) -> None:
        # Only make changes if new direction is different
        # to prevent errors in the _reset_text() direction checks
        if self._label_direction != new_label_direction:
            self._prev_label_direction = self._label_direction
            self._label_direction = new_label_direction
            self._reset_text(text=str(self._text))  # Force a recalculation

    def _get_valid_label_directions(self) -> Tuple[str, ...]:
        return "LTR", "RTL", "UPD", "UPR", "DWR"

    @property
    def bitmap(self) -> displayio.Bitmap:
        """
        The Bitmap object that the text and background are drawn into.

        :rtype: displayio.Bitmap
        """
        return self._bitmap

    def update(self, force: bool = False) -> bool:
        """Attempt to update the display. If ``animate_time`` has elapsed since
        previews animation frame then move the characters over by 1 index.
        Must be called in the main loop of user code.

        :param bool force: whether to ignore ``animation_time`` and force the update.
         Default is False.
        :return: bool updated: whether anything changed and the display needs to be refreshed.
        """
        _now = adafruit_ticks.ticks_ms()
        if force or adafruit_ticks.ticks_less(
            self._last_animate_time + int(self.animate_time * 1000), _now
        ):
            if self._max_characters is None:
                self._set_text(self._full_text, self.scale)
                self._last_animate_time = _now
                return

            if len(self.full_text) <= self.max_characters:
                if self._text != self.full_text:
                    self._set_text(self.full_text, self.scale)
                self._last_animate_time = _now
                return

            if self.current_index + self.max_characters <= len(self.full_text):
                _showing_string = self.full_text[
                    self.current_index : self.current_index + self.max_characters
                ]
            else:
                _showing_string_start = self.full_text[self.current_index :]
                _showing_string_end = "{}".format(
                    self.full_text[
                        : (self.current_index + self.max_characters) % len(self.full_text)
                    ]
                )

                _showing_string = f"{_showing_string_start}{_showing_string_end}"
            self._set_text(_showing_string, self.scale)
            if not force:
                self.current_index += 1
            self._last_animate_time = _now

            return True

        return False

    @property
    def current_index(self) -> int:
        """Index of the first visible character.

        :return int: The current index
        """
        return self._current_index

    @current_index.setter
    def current_index(self, new_index: int) -> None:
        if self.full_text:
            self._current_index = new_index % len(self.full_text)
        else:
            self._current_index = 0

    @property
    def full_text(self) -> str:
        """The full text to be shown. If it's longer than ``max_characters`` then
        scrolling will occur as needed.

        :return str: The full text of this label.
        """
        return self._full_text

    @full_text.setter
    def full_text(self, new_text: str) -> None:
        """
        User code should use the ``text`` property instead of this.
        """
        if self._max_characters is not None:
            if new_text and new_text[-1] != " " and len(new_text) > self.max_characters:
                new_text = f"{new_text} "
            if new_text != self._full_text:
                self._full_text = new_text
                self.current_index = 0
                self.update(True)
        else:
            self._full_text = new_text

    @property
    def max_characters(self):
        """The maximum number of characters to display on screen.

        :return int: The maximum character length of this label.
        """
        return self._max_characters

    @max_characters.setter
    def max_characters(self, new_max_characters):
        """Recalculate the full text based on the new max characters.

        This is necessary to correctly handle the potential space at the end of
        the text.
        """
        if new_max_characters != self._max_characters:
            self._max_characters = new_max_characters
            self.full_text = self.full_text

    @property
    def outline_color(self):
        """Color of the outline to draw around the text. Or None for no outline."""

        return self._palette[2] if self._outline_color is not None else None

    @outline_color.setter
    def outline_color(self, new_outline_color):
        if new_outline_color is not None:
            self._palette[2] = new_outline_color
        else:
            self._outline_color = None

    @property
    def outline_size(self):
        """Stroke size of the outline to draw around the text."""
        return self._outline_size

    @outline_size.setter
    def outline_size(self, new_outline_size):
        self._outline_size = new_outline_size

        self._padding_bottom = max(self._padding_bottom, self.outline_size)
        self._padding_top = max(self._padding_top, self.outline_size)
        self._padding_left = max(self._padding_left, self.outline_size)
        self._padding_right = max(self._padding_right, self.outline_size)

        self._init_outline_stamp(new_outline_size)
        self._reset_text(
            font=self._font,
            text=self._text,
            line_spacing=self._line_spacing,
            scale=self.scale,
        )

    def add_accent_range(
        self, start, end, foreground_color, background_color, accent_type="foreground_background"
    ):
        """
        Set a range of text to get accented with the specified colors.

        :param start: The start index of the range of text to accent, inclusive.
        :param end: The end index of the range of text to accent, exclusive.
        :param foreground_color: The color index within ``color_palette`` to use for
          the accent foreground color.
        :param background_color: The color index within ``color_palette`` to use for
          the accent background color.
        :param accent_type: The type of accent to use, either "foreground_background" or "outline"
        :return: None
        """
        if accent_type not in {"foreground_background", "outline"}:
            raise ValueError("accent_type must be either 'foreground_background' or 'outline'")

        if accent_type == "outline":
            self._padding_bottom = max(self._padding_bottom, self.outline_size)
            self._padding_top = max(self._padding_top, self.outline_size)
            self._padding_left = max(self._padding_left, self.outline_size)
            self._padding_right = max(self._padding_right, self.outline_size)
        self._accent_ranges.append((start, end, foreground_color, background_color, accent_type))
        self._reset_text(text=str(self._text))

    def remove_accent_range(self, start):
        """
        Remove the accent that starts at the specified index within the text.

        :param start: The start index of the range of accented text, inclusive.
        :return: None
        """
        for accent_range in reversed(self._accent_ranges):
            if accent_range[0] == start:
                self._accent_ranges.remove(accent_range)
        self._reset_text(text=str(self._text))

    def add_accent_to_substring(
        self,
        substring,
        foreground_color,
        background_color,
        accent_type="foreground_background",
        start=0,
    ):
        """
        Add accent to the first occurrence of ``substring`` found in the labels text,
        starting from ``start``.

        :param substring: the substring to accent within the text.
        :param foreground_color: The color index within ``color_palette`` to use for
          the accent foreground color.
        :param background_color: The color index within ``color_palette`` to use for
          the accent background color.
        :param accent_type: The type of accent to use, either "foreground_background" or "outline"
        :param start: The index within text to start searching for the substring.
          Defaults is 0 to search the whole text.
        :return: True if the substring was found, False otherwise.
        """
        if accent_type not in {"foreground_background", "outline"}:
            raise ValueError("accent_type must be either 'foreground_background' or 'outline'")
        index = self._full_text.find(substring, start)
        if index != -1:
            self.add_accent_range(
                index, index + len(substring), foreground_color, background_color, accent_type
            )
            return True
        else:
            return False

    def remove_accent_from_substring(self, substring, start=0):
        """
        Remove the accent for the first instance of the specified ``substring``
         starting at ``start``.

        :param substring: the substring to accent within the text.
        :param start: The index within text to start searching for the substring.
          Defaults is 0 to search the whole text.
        :return: True if the substring was found, False otherwise.
        """

        index = self._full_text.find(substring, start)
        if index != -1:
            self.remove_accent_range(index)
            return True
        else:
            return False

    @property
    def accent_ranges(self):
        """
        The list of ranges that are accented.
        :return: List of Tuples containing (start, end, foreground_color, background_color).
        """
        return self._accent_ranges

    def clear_accent_ranges(self):
        """
        Remove all accents from the text. All text will return to default
        foreground and background colors.

        :return: None
        """
        self._accent_ranges = []
        self._reset_text(text=str(self._text))

    @property
    def text(self):
        """The full text to be shown. If it's longer than ``max_characters`` then
        scrolling will occur as needed.

        :return str: The full text of this label.
        """
        return self.full_text

    @text.setter
    def text(self, new_text):
        self.full_text = new_text
        self.update(True)

    @property
    def tilegrid(self) -> displayio.TileGrid:
        """
        The TileGrid that contains the Bitmap for this Label.
        """
        return self._tilegrid
