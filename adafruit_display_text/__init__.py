"""
Display Text module helper functions
"""


# The MIT License (MIT)
#
# Copyright (c) 2020 Tim C for Adafruit Industries LLC
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
            parts = []
            for part in chunks(w, max_chars - 1):
                parts.append("{}-".format(part))
            the_lines.extend(parts[:-1])
            the_line = parts[-1][:-1]
            continue

        if len(the_line + " " + w) <= max_chars:
            the_line += " " + w
        else:
            the_lines.append(the_line)
            the_line = "" + w
    if the_line:  # Last line remaining
        the_lines.append(the_line)
    # Remove first space from first line:
    if the_lines[0][0] == " ":
        the_lines[0] = the_lines[0][1:]
    return the_lines
