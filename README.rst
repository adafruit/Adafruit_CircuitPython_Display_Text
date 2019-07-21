Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-display_text/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/display_text/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://discord.gg/nBQh6qu
    :alt: Discord

.. image:: https://travis-ci.com/adafruit/Adafruit_CircuitPython_Display_Text.svg?branch=master
    :target: https://travis-ci.com/adafruit/Adafruit_CircuitPython_Display_Text
    :alt: Build Status

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
    board.DISPLAY.show(text_area)


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_Display_Text/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.


Sphinx documentation
-----------------------

Sphinx is used to build the documentation based on rST files and comments in the code. First,
install dependencies (feel free to reuse the virtual environment from above):

.. code-block:: shell

    python3 -m venv .env
    source .env/bin/activate
    pip install Sphinx sphinx-rtd-theme

Now, once you have the virtual environment activated:

.. code-block:: shell

    cd docs
    sphinx-build -E -W -b html . _build/html

This will output the documentation to ``docs/_build/html``. Open the index.html in your browser to
view them. It will also (due to -W) error out on any warning like Travis will. This is a good way to
locally verify it will pass.
