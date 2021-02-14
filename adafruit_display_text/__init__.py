# SPDX-FileCopyrightText: 2020 Tim C, 2021 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Display Text module helper functions
"""


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
