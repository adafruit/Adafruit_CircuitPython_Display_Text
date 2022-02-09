# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_display_text.scrolling_label`
====================================================

Displays text into a fixed-width label that scrolls leftward
if the full_text is large enough to need it.

* Author(s): Tim Cocks

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Text.git"

import time
from adafruit_display_text import bitmap_label


class ScrollingLabel(bitmap_label.Label):

    """
    ScrollingLabel - A fixed-width label that will scroll to the left
    in order to show the full text if it's larger than the fixed-width.

    :param font: The font to use for the label.
    :param max_characters: The number of characters that sets the  fixed-width. Default is 10.
    :param text: The full text to show in the label. If this is longer than
     `max_characters` then the label will scroll to show everything.
    :param animate_time: The number of seconds in between scrolling animation
     frames. Default is 0.3 seconds.
    :param current_index: The index of the first visible character in the label.
     Default is 0, the first character. Will increase while scrolling.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        font,
        max_characters=10,
        text="",
        animate_time=0.3,
        current_index=0,
        **kwargs
    ):

        super().__init__(font, **kwargs)
        self.animate_time = animate_time
        self._current_index = current_index
        self._last_animate_time = -1
        self.max_characters = max_characters

        if text[-1] != " ":
            text = "{} ".format(text)
        self._full_text = text

        self.update()

    def update(self, force=False):
        """
        Attempt to update the display. If `animate_time` has elapsed since
        previews animation frame then move the characters over by 1 index.
        Must be called in the main loop of user code.

        :param force: whether to ignore `animation_time` and force the update. Default is False.
        :return: None
        """
        _now = time.monotonic()
        if force or self._last_animate_time + self.animate_time <= _now:

            if len(self.full_text) <= self.max_characters:
                self.text = self.full_text
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
                        : (self.current_index + self.max_characters)
                        % len(self.full_text)
                    ]
                )

                _showing_string = "{}{}".format(
                    _showing_string_start, _showing_string_end
                )
            self.text = _showing_string

            self.current_index += 1
            self._last_animate_time = _now

            return

    @property
    def current_index(self):
        """
        Index of the first visible character.

        :return int: the current index
        """
        return self._current_index

    @current_index.setter
    def current_index(self, new_index):
        if new_index < len(self.full_text):
            self._current_index = new_index
        else:
            self._current_index = new_index % len(self.full_text)

    @property
    def full_text(self):
        """
        The full text to be shown. If it's longer than `max_characters` then
        scrolling will occur as needed.

        :return string: The full text of this label.
        """
        return self._full_text

    @full_text.setter
    def full_text(self, new_text):
        if new_text[-1] != " ":
            new_text = "{} ".format(new_text)
        self._full_text = new_text
        self.current_index = 0
        self.update()
