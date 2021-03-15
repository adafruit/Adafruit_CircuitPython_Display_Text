# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_display_text.label`
====================================================

Displays text labels using CircuitPython's displayio.

* Author(s): Scott Shawcroft

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

from adafruit_display_text import LabelBase


class Label(LabelBase):
    """A label displaying a string of text. The origin point set by ``x`` and ``y``
    properties will be the left edge of the bounding box, and in the center of a M
    glyph (if its one line), or the (number of lines * linespacing + M)/2. That is,
    it will try to have it be center-left as close as possible.

    :param Font font: A font class that has ``get_bounding_box`` and ``get_glyph``.
      Must include a capital M for measuring character size.
    :param str text: Text to display
    :param int max_glyphs: The largest quantity of glyphs we will display
    :param int color: Color of all text in RGB hex
    :param float line_spacing: Line spacing of text to display
    :param bool background_tight: Set `True` only if you want background box to tightly
     surround text. When set to 'True' Padding parameters will be ignored.
    :param int padding_top: Additional pixels added to background bounding box at top.
     This parameter could be negative indicating additional pixels subtracted to background
     bounding box.
    :param int padding_bottom: Additional pixels added to background bounding box at bottom.
     This parameter could be negative indicating additional pixels subtracted to background
     bounding box.
    :param int padding_left: Additional pixels added to background bounding box at left.
     This parameter could be negative indicating additional pixels subtracted to background
     bounding box.
    :param int padding_right: Additional pixels added to background bounding box at right.
     This parameter could be negative indicating additional pixels subtracted to background
     bounding box.
    :param (float,float) anchor_point: Point that anchored_position moves relative to.
     Tuple with decimal percentage of width and height.
     (E.g. (0,0) is top left, (1.0, 0.5): is middle right.)
    :param (int,int) anchored_position: Position relative to the anchor_point. Tuple
     containing x,y pixel coordinates.
    :param int scale: Integer value of the pixel scaling
    :param bool base_alignment: when True allows to align text label to the baseline.
     This is helpful when two or more labels need to be aligned to the same baseline
    :param (int,str) tab_replacement: tuple with tab character replace information. When
     (4, " ") will indicate a tab replacement of 4 spaces, defaults to 4 spaces by
     tab character
    :param str label_direction: string defining the label text orientation. There are 5
     configurations possibles ``LTR``-Left-To-Right ``RTL``-Right-To-Left
     ``TTB``-Top-To-Bottom ``UPR``-Upwards ``DWR``-Downwards. It defaults to ``LTR``"""

    # pylint: disable=too-many-instance-attributes, too-many-locals
    # This has a lot of getters/setters, maybe it needs cleanup.

    def __init__(self, font, **kwargs) -> None:
        super().__init__(font, **kwargs)

        max_glyphs = kwargs.get("max_glyphs", None)
        text = kwargs.get("text", "")

        if not max_glyphs and not text:
            raise RuntimeError("Please provide a max size, or initial text")
        self._tab_replacement = kwargs.get("tab_replacement", (4, " "))
        self._tab_text = self._tab_replacement[1] * self._tab_replacement[0]
        text = self._tab_text.join(text.split("\t"))
        if not max_glyphs:
            max_glyphs = len(text)
        # add one to max_size for the background bitmap tileGrid

        # local_group will set the scale
        self.local_group = displayio.Group(
            max_size=max_glyphs + 1, scale=kwargs.get("scale", 1)
        )
        self.append(self.local_group)

        self.width = max_glyphs
        self._font = font
        self._text = None
        self._anchor_point = kwargs.get("anchor_point", None)
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)

        self.height = self._font.get_bounding_box()[1]
        self._line_spacing = kwargs.get("line_spacing", 1.25)
        self._bounding_box = None

        self._background_tight = kwargs.get(
            "background_tight", False
        )  # sets padding status for text background box

        # Create the two-color text palette
        self.palette = displayio.Palette(2)
        self.palette[0] = 0
        self.palette.make_transparent(0)
        self.color = kwargs.get("color", 0xFFFFFF)

        self._background_color = kwargs.get("background_color", None)
        self._background_palette = displayio.Palette(1)
        self._added_background_tilegrid = False

        self._padding_top = kwargs.get("padding_top", 0)
        self._padding_bottom = kwargs.get("padding_bottom", 0)
        self._padding_left = kwargs.get("padding_left", 0)
        self._padding_right = kwargs.get("padding_right", 0)
        self.base_alignment = kwargs.get("base_alignment", False)
        self._label_direction = kwargs.get("label_direction", "LTR")
        self._label_style = kwargs.get("label_style", "Default")

        if self.label_style != "Default":
            self._update_text(str(text))

        if text is not None:
            if self.label_style != "Default":
                self._set_label_style(self._label_style)
            else:
                self._update_text(str(text))
        if (kwargs.get("anchored_position", None) is not None) and (
            kwargs.get("anchor_point", None) is not None
        ):
            self.anchored_position = kwargs.get("anchored_position", None)

    def _create_background_box(self, lines: int, y_offset: int) -> None:
        """Private Class function to create a background_box
        :param lines: int number of lines
        :param y_offset: int y pixel bottom coordinate for the background_box"""

        left = self._bounding_box[0]
        if self._background_tight:  # draw a tight bounding box
            box_width = self._bounding_box[2]
            box_height = self._bounding_box[3]
            x_box_offset = 0
            y_box_offset = self._bounding_box[1]

        else:  # draw a "loose" bounding box to include any ascenders/descenders.
            ascent, descent = self._get_ascent_descent()

            if (
                self._label_direction == "UPR"
                or self._label_direction == "DWR"
                or self._label_direction == "TTB"
            ):
                box_height = (
                    self._bounding_box[3] + self._padding_top + self._padding_bottom
                )
                x_box_offset = -self._padding_bottom
                box_width = (
                    (ascent + descent)
                    + int((lines - 1) * self.width * self._line_spacing)
                    + self._padding_left
                    + self._padding_right
                )
            else:
                box_width = (
                    self._bounding_box[2] + self._padding_left + self._padding_right
                )
                x_box_offset = -self._padding_left
                box_height = (
                    (ascent + descent)
                    + int((lines - 1) * self.height * self._line_spacing)
                    + self._padding_top
                    + self._padding_bottom
                )

            if self.base_alignment:
                y_box_offset = -ascent - self._padding_top
            else:
                y_box_offset = -ascent + y_offset - self._padding_top

        box_width = max(0, box_width)  # remove any negative values
        box_height = max(0, box_height)  # remove any negative values

        if self._label_direction == "UPR":
            movx = left + x_box_offset
            movy = -box_height - x_box_offset
        elif self._label_direction == "DWR":
            movx = left + x_box_offset
            movy = x_box_offset
        elif self._label_direction == "TTB":
            movx = left + x_box_offset
            movy = x_box_offset
        else:
            movx = left + x_box_offset
            movy = y_box_offset

        background_bitmap = displayio.Bitmap(box_width, box_height, 1)
        tile_grid = displayio.TileGrid(
            background_bitmap,
            pixel_shader=self._background_palette,
            x=movx,
            y=movy,
        )

        return tile_grid

    def _update_background_color(self, new_color: int) -> None:
        """Private class function that allows updating the font box background color
        :param new_color: int color as an RGB hex number."""

        if new_color is None:
            self._background_palette.make_transparent(0)
            if self._added_background_tilegrid:
                self.local_group.pop(0)
                self._added_background_tilegrid = False
        else:
            self._background_palette.make_opaque(0)
            self._background_palette[0] = new_color
        self._background_color = new_color

        lines = self._text.rstrip("\n").count("\n") + 1
        y_offset = self._get_ascent() // 2

        if not self._added_background_tilegrid:  # no bitmap is in the self Group
            # add bitmap if text is present and bitmap sizes > 0 pixels
            if (
                (len(self._text) > 0)
                and (
                    self._bounding_box[2] + self._padding_left + self._padding_right > 0
                )
                and (
                    self._bounding_box[3] + self._padding_top + self._padding_bottom > 0
                )
            ):
                # This can be simplified in CP v6.0, when group.append(0) bug is corrected
                if len(self.local_group) > 0:
                    self.local_group.insert(
                        0, self._create_background_box(lines, y_offset)
                    )
                else:
                    self.local_group.append(
                        self._create_background_box(lines, y_offset)
                    )
                self._added_background_tilegrid = True

        else:  # a bitmap is present in the self Group
            # update bitmap if text is present and bitmap sizes > 0 pixels
            if (
                (len(self._text) > 0)
                and (
                    self._bounding_box[2] + self._padding_left + self._padding_right > 0
                )
                and (
                    self._bounding_box[3] + self._padding_top + self._padding_bottom > 0
                )
            ):
                self.local_group[0] = self._create_background_box(lines, self._y_offset)
            else:  # delete the existing bitmap
                self.local_group.pop(0)
                self._added_background_tilegrid = False

    # pylint: disable = too-many-branches, too-many-statements
    def _update_text(
        self, new_text: str
    ) -> None:  # pylint: disable=too-many-locals ,too-many-branches, too-many-statements
        x = 0
        y = 0
        if self._added_background_tilegrid:
            i = 1
        else:
            i = 0
        tilegrid_count = i
        if self.base_alignment:
            self._y_offset = 0
        else:
            self._y_offset = self._get_ascent() // 2

        if self._label_direction == "RTL":
            left = top = bottom = 0
            right = None
        elif self._label_direction == "LTR":
            right = top = bottom = 0
            left = None
        else:
            top = right = left = 0
            bottom = 0

        for character in new_text:
            if character == "\n":
                y += int(self.height * self._line_spacing)
                x = 0
                continue
            glyph = self._font.get_glyph(ord(character))
            if not glyph:
                continue

            if self._label_direction == "LTR" or self._label_direction == "RTL":
                bottom = max(bottom, y - glyph.dy + self._y_offset)
                if y == 0:  # first line, find the Ascender height
                    top = min(top, -glyph.height - glyph.dy + self._y_offset)
                position_y = y - glyph.height - glyph.dy + self._y_offset

                if self._label_direction == "LTR":
                    right = max(right, x + glyph.shift_x, x + glyph.width + glyph.dx)
                    if x == 0:
                        if left is None:
                            left = glyph.dx
                        else:
                            left = min(left, glyph.dx)
                    position_x = x + glyph.dx
                else:
                    left = max(
                        left, abs(x) + glyph.shift_x, abs(x) + glyph.width + glyph.dx
                    )
                    if x == 0:
                        if right is None:
                            right = glyph.dx
                        else:
                            right = max(right, glyph.dx)
                    position_x = x - glyph.width

            if self._label_direction == "TTB":
                if x == 0:
                    if left is None:
                        left = glyph.dx
                    else:
                        left = min(left, glyph.dx)
                if y == 0:
                    top = min(top, -glyph.dy)

                bottom = max(bottom, y + glyph.height, y + glyph.height + glyph.dy)
                right = max(
                    right, x + glyph.width + glyph.dx, x + glyph.shift_x + glyph.dx
                )
                position_y = y + glyph.dy
                position_x = x - glyph.width // 2 + self._y_offset

            if self._label_direction == "UPR":
                if x == 0:
                    if bottom is None:
                        bottom = -glyph.dx

                if y == 0:  # first line, find the Ascender height
                    bottom = min(bottom, -glyph.dy)
                left = min(left, x - glyph.height + self._y_offset)
                top = min(top, y - glyph.width - glyph.dx, y - glyph.shift_x)
                right = max(right, x + glyph.height, x + glyph.height - glyph.dy)
                position_y = y - glyph.width - glyph.dx
                position_x = x - glyph.height - glyph.dy + self._y_offset

            if self._label_direction == "DWR":
                if y == 0:
                    if top is None:
                        top = -glyph.dx
                top = min(top, -glyph.dx)
                if x == 0:
                    left = min(left, -glyph.dy)
                left = min(left, x, x - glyph.dy - self._y_offset)
                bottom = max(bottom, y + glyph.width + glyph.dx, y + glyph.shift_x)
                right = max(right, x + glyph.height)
                position_y = y + glyph.dx
                position_x = x + glyph.dy - self._y_offset

            if glyph.width > 0 and glyph.height > 0:
                try:
                    # pylint: disable=unexpected-keyword-arg
                    face = displayio.TileGrid(
                        glyph.bitmap,
                        pixel_shader=self.palette,
                        default_tile=glyph.tile_index,
                        tile_width=glyph.width,
                        tile_height=glyph.height,
                        position=(position_x, position_y),
                    )
                except TypeError:
                    face = displayio.TileGrid(
                        glyph.bitmap,
                        pixel_shader=self.palette,
                        default_tile=glyph.tile_index,
                        tile_width=glyph.width,
                        tile_height=glyph.height,
                        x=position_x,
                        y=position_y,
                    )

                if self._label_direction == "UPR":
                    face.transpose_xy = True
                    face.flip_x = True
                if self._label_direction == "DWR":
                    face.transpose_xy = True
                    face.flip_y = True

                if tilegrid_count < len(self.local_group):
                    self.local_group[tilegrid_count] = face
                else:
                    self.local_group.append(face)
                tilegrid_count += 1

            if self._label_direction == "RTL":
                x = x - glyph.shift_x
            if self._label_direction == "TTB":
                if glyph.height < 2:
                    y = y + glyph.shift_x
                else:
                    y = y + glyph.height + 1
            if self._label_direction == "UPR":
                y = y - glyph.shift_x
            if self._label_direction == "DWR":
                y = y + glyph.shift_x
            if self._label_direction == "LTR":
                x = x + glyph.shift_x

            i += 1

        if self._label_direction == "LTR" and left is None:
            left = 0
        if self._label_direction == "RTL" and right is None:
            right = 0
        if self._label_direction == "TTB" and top is None:
            top = 0

        while len(self.local_group) > tilegrid_count:  # i:
            self.local_group.pop()
        # pylint: disable=invalid-unary-operand-type
        if self._label_direction == "RTL":
            self._bounding_box = (-left, top, left - right, bottom - top)
        if self._label_direction == "TTB":
            self._bounding_box = (left, top, right - left, bottom - top)
        if self._label_direction == "UPR":
            self._bounding_box = (left, top, right, bottom - top)
        if self._label_direction == "DWR":
            self._bounding_box = (left, top, right, bottom - top)
        if self._label_direction == "LTR":
            self._bounding_box = (left, top, right - left, bottom - top)

        self._text = new_text

        if self.background_color is not None:
            self._update_background_color(self._background_color)

    def _reset_text(self, new_text: str) -> None:
        new_text = self._tab_text.join(new_text.split("\t"))
        try:
            current_anchored_position = self.anchored_position
            self._update_text(str(new_text))
            self.anchored_position = current_anchored_position
        except RuntimeError as run_error:
            raise RuntimeError("Text length exceeds max_glyphs") from run_error

    def _set_font(self, new_font) -> None:
        old_text = self._text
        current_anchored_position = self.anchored_position
        self._text = ""
        self._font = new_font
        self.height = self._font.get_bounding_box()[1]
        self._update_text(str(old_text))
        self.anchored_position = current_anchored_position

    def _set_line_spacing(self, new_line_spacing: float) -> None:
        self._line_spacing = new_line_spacing
        self.text = self._text  # redraw the box

    def _set_text(self, new_text: str, scale: int) -> None:
        self._reset_text(new_text)

    def _set_background_color(self, new_color: int) -> None:
        self._update_background_color(new_color)

    def _set_label_direction(self, new_label_direction: str) -> None:
        self._label_direction = new_label_direction
        old_text = self._text
        self._update_text(str(old_text))

    def _set_label_style(self, new_label_style: str) -> None:
        # import would change after library packaging
        # pylint: disable=import-outside-toplevel
        from adafruit_colorsys import get_hex
        from adafruit_colorsys import styles

        self._label_style = new_label_style
        colorset = styles.THEME
        self.color = get_hex(colorset[self._label_style]["TEXT"])
        self._background_color = get_hex(colorset[self._label_style]["BACKGROUND"])

        old_text = self._text
        self._update_text(str(old_text))
