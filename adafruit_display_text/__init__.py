# SPDX-FileCopyrightText: 2020 Tim C, 2021 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Display Text module helper functions
"""
from displayio import Group, Palette


def wrap_text_to_pixels(string, max_width, font=None, indent0="", indent1=""):
    """wrap_text_to_pixels function
    A helper that will return a list of lines with word-break wrapping.
    Leading and trailing whitespace in your string will be removed. If
    you wish to use leading whitespace see `indend0` and `indent1`
    parameters.

    :param str string: The text to be wrapped.
    :param int max_width: The maximum number of pixels on a line before wrapping.
    :param Font font: The font to use for measuring the text.
    :param str indent0: Additional character(s) to add to the first line.
    :param str indent1: Additional character(s) to add to all other lines.


    :return list lines: A list of the lines resulting from wrapping the
      input text at max_width pixels size

    """
    # pylint: disable=too-many-locals too-many-branches
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


def wrap_text_to_lines(string, max_chars):
    """wrap_text_to_lines function
    A helper that will return a list of lines with word-break wrapping

    :param str string: The text to be wrapped
    :param int max_chars: The maximum number of characters on a line before wrapping

    :return list the_lines: A list of lines where each line is separated based on the amount
        of max_chars provided

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
        scale=1,
        base_alignment=False,
        **kwargs,
    ):
        super().__init__(max_size=1, x=x, y=y, scale=1)

        self._font = font
        self.palette = Palette(2)
        self._color = color
        self._background_color = background_color

        self._bounding_box = None
        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        self.local_group = None

        self._text = text

    def _get_ascent_descent(self):
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

    def _get_ascent(self):
        return self._get_ascent_descent()[0]

    @property
    def font(self):
        """Font to use for text display."""
        return self._font

    def _set_font(self, new_font):
        # subclasses should override this
        pass

    @font.setter
    def font(self, new_font):
        self._set_font(new_font)

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
            self.x = int(
                new_position[0]
                - (self._bounding_box[0] * self.scale)
                - round(self._anchor_point[0] * (self._bounding_box[2] * self.scale))
            )
            self.y = int(
                new_position[1]
                - (self._bounding_box[1] * self.scale)
                - round(self._anchor_point[1] * self._bounding_box[3] * self.scale)
            )

    @property
    def scale(self):
        """Set the scaling of the label, in integer values"""
        return self.local_group.scale

    @scale.setter
    def scale(self, new_scale):
        self.local_group.scale = new_scale
        self.anchored_position = self._anchored_position  # update the anchored_position

    def _reset_text(self, text, scale):
        # subclasses should override this
        pass

    @property
    def text(self):
        """Text to be displayed."""
        return self._text

    @text.setter  # Cannot set color or background color with text setter, use separate setter
    def text(self, new_text):
        self._reset_text(text=new_text, scale=self.scale)