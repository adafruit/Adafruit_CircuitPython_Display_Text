# SPDX-FileCopyrightText: 2020 Tim C, 2021 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_display_text`
=======================
"""

try:
    from typing import List, Tuple
except ImportError:
    pass
from displayio import Group, Palette


def wrap_text_to_pixels(
    string: str, max_width: int, font=None, indent0: str = "", indent1: str = ""
) -> List[str]:
    """wrap_text_to_pixels function
    A helper that will return a list of lines with word-break wrapping.
    Leading and trailing whitespace in your string will be removed. If
    you wish to use leading whitespace see ``indent0`` and ``indent1``
    parameters.

    :param str string: The text to be wrapped.
    :param int max_width: The maximum number of pixels on a line before wrapping.
    :param Font font: The font to use for measuring the text.
    :param str indent0: Additional character(s) to add to the first line.
    :param str indent1: Additional character(s) to add to all other lines.

    :return: A list of the lines resulting from wrapping the
        input text at ``max_width`` pixels size
    :rtype: List[str]

    """
    # pylint: disable=too-many-locals, too-many-branches
    if font is None:

        def measure(string):
            return len(string)

    else:
        if hasattr(font, "load_glyphs"):
            font.load_glyphs(string)

        def measure(string):
            return sum(font.get_glyph(ord(c)).shift_x for c in string)

    lines = []
    partial = [indent0]
    width = measure(indent0)
    swidth = measure(" ")
    firstword = True
    for line_in_input in string.split("\n"):
        for index, word in enumerate(line_in_input.split(" ")):
            wwidth = measure(word)
            word_parts = []
            cur_part = ""

            if wwidth > max_width:
                for char in word:
                    if (
                        measure("".join(partial))
                        + measure(cur_part)
                        + measure(char)
                        + measure("-")
                        > max_width
                    ):
                        word_parts.append("".join(partial) + cur_part + "-")
                        cur_part = char
                        partial = [indent1]
                    else:
                        cur_part += char
                if cur_part:
                    word_parts.append(cur_part)
                for line in word_parts[:-1]:
                    lines.append(line)
                partial.append(word_parts[-1])
                width = measure(word_parts[-1])
                if firstword:
                    firstword = False
            else:
                if firstword:
                    partial.append(word)
                    firstword = False
                    width += wwidth
                elif width + swidth + wwidth < max_width:
                    if index > 0:
                        partial.append(" ")
                    partial.append(word)
                    width += wwidth + swidth
                else:
                    lines.append("".join(partial))
                    partial = [indent1, word]
                    width = measure(indent1) + wwidth

        lines.append("".join(partial))
        partial = [indent1]
        width = measure(indent1)

    return lines


def wrap_text_to_lines(string: str, max_chars: int) -> List[str]:
    """wrap_text_to_lines function
    A helper that will return a list of lines with word-break wrapping

    :param str string: The text to be wrapped
    :param int max_chars: The maximum number of characters on a line before wrapping

    :return: A list of lines where each line is separated based on the amount
        of ``max_chars`` provided
    :rtype: List[str]
    """

    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    string = string.replace("\n", "").replace("\r", "")  # Strip confusing newlines
    words = string.split(" ")
    the_lines = []
    the_line = ""
    for w in words:
        if len(w) > max_chars:
            if the_line:  # add what we had stored
                the_lines.append(the_line)
            parts = []
            for part in chunks(w, max_chars - 1):
                parts.append("{}-".format(part))
            the_lines.extend(parts[:-1])
            the_line = parts[-1][:-1]
            continue

        if len(the_line + " " + w) <= max_chars:
            the_line += " " + w
        elif not the_line and len(w) == max_chars:
            the_lines.append(w)
        else:
            the_lines.append(the_line)
            the_line = "" + w
    if the_line:  # Last line remaining
        the_lines.append(the_line)
    # Remove any blank lines
    while not the_lines[0]:
        del the_lines[0]
    # Remove first space from first line:
    if the_lines[0][0] == " ":
        the_lines[0] = the_lines[0][1:]
    return the_lines


class LabelBase(Group):
    """Superclass that all other types of labels will extend. This contains
    all of the properties and functions that work the same way in all labels.

    **Note:** This should be treated as an abstract base class.

    Subclasses should implement ``_set_text``, ``_set_font``, and ``_set_line_spacing`` to
    have the correct behavior for that type of label.

    :param Font font: A font class that has ``get_bounding_box`` and ``get_glyph``.
      Must include a capital M for measuring character size.
    :param str text: Text to display
    :param int max_glyphs: Unnecessary parameter (provided only for direct compability
     with :py:func:`~adafruit_display_text.label.Label`)
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
     tab character"""

    # pylint: disable=unused-argument,  too-many-instance-attributes, too-many-locals, too-many-arguments
    def __init__(
        self,
        font,
        x: int = 0,
        y: int = 0,
        text: str = "",
        max_glyphs: int = None,
        color: int = 0xFFFFFF,
        background_color: int = None,
        line_spacing: float = 1.25,
        background_tight: bool = False,
        padding_top: int = 0,
        padding_bottom: int = 0,
        padding_left: int = 0,
        padding_right: int = 0,
        anchor_point: Tuple[float, float] = None,
        anchored_position: Tuple[int, int] = None,
        save_text: bool = True,  # can reduce memory use if save_text = False
        scale: int = 1,
        base_alignment: bool = False,
        tab_replacement: Tuple[int, str] = (4, " "),
        **kwargs,
    ) -> None:
        super().__init__(max_size=1, x=x, y=y, scale=1)

        self._font = font
        self.palette = Palette(2)
        self._color = color
        self._background_color = background_color

        self._bounding_box = None
        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        # local group will hold background and text
        # the self group scale should always remain at 1, the self.local_group will
        # be used to set the scale of the label
        self.local_group = None

        self._text = text
        self.baseline = -1.0

        self.base_alignment = base_alignment

        if self.base_alignment:
            self._y_offset = 0
        else:
            self._y_offset = self._get_ascent() // 2

    def _get_ascent_descent(self) -> Tuple[int, int]:
        """ Private function to calculate ascent and descent font values """
        if hasattr(self.font, "ascent"):
            return self.font.ascent, self.font.descent

        # check a few glyphs for maximum ascender and descender height
        glyphs = "M j'"  # choose glyphs with highest ascender and lowest
        try:
            self._font.load_glyphs(glyphs)
        except AttributeError:
            # Builtin font doesn't have or need load_glyphs
            pass
        # descender, will depend upon font used
        ascender_max = descender_max = 0
        for char in glyphs:
            this_glyph = self._font.get_glyph(ord(char))
            if this_glyph:
                ascender_max = max(ascender_max, this_glyph.height + this_glyph.dy)
                descender_max = max(descender_max, -this_glyph.dy)
        return ascender_max, descender_max

    def _get_ascent(self) -> int:
        return self._get_ascent_descent()[0]

    @property
    def font(self) -> None:
        """Font to use for text display."""
        return self._font

    def _set_font(self, new_font) -> None:
        # subclasses should override this
        pass

    @font.setter
    def font(self, new_font) -> None:
        self._set_font(new_font)

    @property
    def color(self) -> int:
        """Color of the text as an RGB hex number."""
        return self._color

    @color.setter
    def color(self, new_color: int):
        self._color = new_color
        if new_color is not None:
            self.palette[1] = new_color
            self.palette.make_opaque(1)
        else:
            self.palette[1] = 0
            self.palette.make_transparent(1)

    @property
    def background_color(self) -> int:
        """Color of the background as an RGB hex number."""
        return self._background_color

    def _set_background_color(self, new_color):
        # subclasses should override this
        pass

    @background_color.setter
    def background_color(self, new_color: int) -> None:
        self._set_background_color(new_color)

    @property
    def anchor_point(self) -> Tuple[float, float]:
        """Point that anchored_position moves relative to.
        Tuple with decimal percentage of width and height.
        (E.g. (0,0) is top left, (1.0, 0.5): is middle right.)"""
        return self._anchor_point

    @anchor_point.setter
    def anchor_point(self, new_anchor_point: Tuple[float, float]) -> None:
        if new_anchor_point[1] == self.baseline:
            self._anchor_point = (new_anchor_point[0], -1.0)
        else:
            self._anchor_point = new_anchor_point
        self.anchored_position = (
            self._anchored_position
        )  # update the anchored_position using setter

    @property
    def anchored_position(self) -> Tuple[int, int]:
        """Position relative to the anchor_point. Tuple containing x,y
        pixel coordinates."""
        return self._anchored_position

    @anchored_position.setter
    def anchored_position(self, new_position: Tuple[int, int]) -> None:
        self._anchored_position = new_position
        # Set anchored_position
        if (self._anchor_point is not None) and (self._anchored_position is not None):
            self.x = int(
                new_position[0]
                - (self._bounding_box[0] * self.scale)
                - round(self._anchor_point[0] * (self._bounding_box[2] * self.scale))
            )
            if self._anchor_point[1] == self.baseline:
                self.y = int(new_position[1] - (self._y_offset * self.scale))
            else:
                self.y = int(
                    new_position[1]
                    - (self._bounding_box[1] * self.scale)
                    - round(self._anchor_point[1] * self._bounding_box[3] * self.scale)
                )

    @property
    def scale(self) -> int:
        """Set the scaling of the label, in integer values"""
        return self.local_group.scale

    @scale.setter
    def scale(self, new_scale: int) -> None:
        self.local_group.scale = new_scale
        self.anchored_position = self._anchored_position  # update the anchored_position

    def _set_text(self, new_text: str, scale: int) -> None:
        # subclasses should override this
        pass

    @property
    def text(self) -> str:
        """Text to be displayed."""
        return self._text

    @text.setter  # Cannot set color or background color with text setter, use separate setter
    def text(self, new_text: str) -> None:
        self._set_text(new_text, self.scale)

    @property
    def bounding_box(self) -> Tuple[int, int]:
        """An (x, y, w, h) tuple that completely covers all glyphs. The
        first two numbers are offset from the x, y origin of this group"""
        return tuple(self._bounding_box)

    @property
    def line_spacing(self) -> float:
        """The amount of space between lines of text, in multiples of the font's
        bounding-box height. (E.g. 1.0 is the bounding-box height)"""
        return self._line_spacing

    def _set_line_spacing(self, new_line_spacing: float) -> None:
        # subclass should override this.
        pass

    @line_spacing.setter
    def line_spacing(self, new_line_spacing: float) -> None:
        self._set_line_spacing(new_line_spacing)
