Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-display_text/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/display_text/en/latest/
    :alt: Documentation Status

.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_Display_Text/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_Display_Text/actions/
    :alt: Build Status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

Displays text using CircuitPython's displayio.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Usage Example
=============

For a board with a built-in display.

.. code:: python

    import board
    import terminalio
    from adafruit_display_text import label


    text = "Hello world"
    text_area = label.Label(terminalio.FONT, text=text)
    text_area.x = 10
    text_area.y = 10
    board.DISPLAY.root_group = text_area
    while True:
        pass


Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/display_text/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_Display_Text/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
