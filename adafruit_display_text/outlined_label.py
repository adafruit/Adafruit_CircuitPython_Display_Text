# SPDX-FileCopyrightText: 2025 Tim C for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import warnings

from .bitmap_label import Label as BitmapLabel

warnings.warn(
    "outlined_label.OutlinedLabel is deprecated, adafruit_display_text.bitmap_label.Label"
    " now supports outline functionality with the same API, it should be used instead."
)
OutlinedLabel = BitmapLabel
