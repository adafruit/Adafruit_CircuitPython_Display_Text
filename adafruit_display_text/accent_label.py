# SPDX-FileCopyrightText: 2025 Tim Cocks for Adafruit Industries
# SPDX-License-Identifier: MIT
import bitmaptools
from displayio import Bitmap, Palette
from micropython import const

from adafruit_display_text.bitmap_label import Label as BitmapLabel

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


class AccentLabel(BitmapLabel):
    """
    Subclass of BitmapLabel that allows accenting ranges of text with different
    foreground and background colors.

    :param font: A font class that has ``get_bounding_box`` and ``get_glyph``.
      Must include a capital M for measuring character size.
    :type font: ~fontio.FontProtocol
    :param displayio.Palette color_palette: The palette to use for the Label.
      Indexes 0 and 1 will be filled with background and foreground colors automatically.
      Indexes 2 and above can be used for accent colors.
    """

    def __init__(
        self, font: FontProtocol, color_palette: Palette, save_text: bool = True, **kwargs
    ) -> None:
        super().__init__(font, save_text, **kwargs)

        if len(color_palette) <= 2:
            raise ValueError(
                "color_palette should be at least 3 colors to "
                "provide enough for normal and accented text"
            )

        self._palette = color_palette
        self.color = self._color
        self.background_color = self._background_color

        self._accent_ranges = []

        self._tmp_glyph_bitmap = None

    def add_accent_range(self, start, end, foreground_color, background_color):
        """
        Set a range of text to get accented with the specified colors.

        :param start: The start index of the range of text to accent, inclusive.
        :param end: The end index of the range of text to accent, exclusive.
        :param foreground_color: The color index within ``color_palette`` to use for
          the accent foreground color.
        :param background_color: The color index within ``color_palette`` to use for
          the accent background color.
        :return: None
        """
        self._accent_ranges.append((start, end, foreground_color, background_color))
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

    def add_accent_to_substring(self, substring, foreground_color, background_color, start=0):
        """
        Add accent to the first occurrence of ``substring`` found in the labels text,
        starting from ``start``.

        :param substring: the substring to accent within the text.
        :param foreground_color: The color index within ``color_palette`` to use for
          the accent foreground color.
        :param background_color: The color index within ``color_palette`` to use for
          the accent background color.
        :param start: The index within text to start searching for the substring.
          Defaults is 0 to search the whole text.
        :return: True if the substring was found, False otherwise.
        """

        index = self._text.find(substring, start)
        if index != -1:
            self.add_accent_range(index, index + len(substring), foreground_color, background_color)
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

        index = self._text.find(substring, start)
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
        """
        Overridden from parent class BitmapLabel with accent color
        functionality added.
        """
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
                if self._tmp_glyph_bitmap is None:
                    self._tmp_glyph_bitmap = Bitmap(
                        my_glyph.bitmap.width, my_glyph.bitmap.height, len(self._palette)
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
                    if len(self._accent_ranges) > 0:
                        for accent_range in self._accent_ranges:
                            if (
                                char_idx >= accent_range[ACCENT_START]
                                and char_idx < accent_range[ACCENT_END]
                            ):
                                self._tmp_glyph_bitmap.fill(accent_range[ACCENT_BG])

                                bitmaptools.blit(
                                    self._tmp_glyph_bitmap,
                                    my_glyph.bitmap,
                                    0,
                                    0,
                                    skip_source_index=0,
                                )
                                bitmaptools.replace_color(
                                    self._tmp_glyph_bitmap, 1, accent_range[ACCENT_FG]
                                )
                                accented = True
                                break

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
                        else None,  # do not copy over any 0 background pixels
                    )

                    xposition = xposition + my_glyph.shift_x

        # bounding_box
        return left, top, right - left, bottom - top
