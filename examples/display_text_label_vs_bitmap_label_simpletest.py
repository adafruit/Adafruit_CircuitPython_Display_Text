# Sample code using the textMap library and the "textBox" wrapper class
# Creates four textBox instances
# Inserts each textBox into a tileGrid group
# Writes text into the box one character at a time
# Moves the position of the textBox around the display
# Clears each textBox after the full string is written (even if the text is outside of the box)

# import textmap
# from textmap import textBox

import board
import displayio
import terminalio
import gc
import time

##########
# Use these Boolean variables to select the text display library and which font style to use
##########
use_bitmap_label = True  # Set True if to use 'bitmap_label.py'
# Set False to use 'label.py' library
##########
use_builtin_font = True  # Set True to use the terminalio.FONT BuiltinFont,
# Set False to use a BDF loaded font, see "fontFiles" below
##########


my_scale = 1

if use_bitmap_label:  # use bitmap_label.py library (Bitmap)
    from adafruit_display_text import bitmap_label as label

    version = "bitmap_label.py"

else:  # use label.py library (TileGrid)
    from adafruit_display_text import label as label

    version = "label.py"

#  Setup the SPI display

if "DISPLAY" not in dir(board):
    # Setup the LCD display with driver
    # You may need to change this to match the display driver for the chipset
    # used on your display
    from adafruit_ili9341 import ILI9341

    displayio.release_displays()

    # setup the SPI bus
    spi = board.SPI()
    tft_cs = board.D9  # arbitrary, pin not used
    tft_dc = board.D10
    tft_backlight = board.D12
    tft_reset = board.D11

    while not spi.try_lock():
        spi.configure(baudrate=32000000)
    spi.unlock()

    display_bus = displayio.FourWire(
        spi,
        command=tft_dc,
        chip_select=tft_cs,
        reset=tft_reset,
        baudrate=32000000,
        polarity=1,
        phase=1,
    )

    # Number of pixels in the display
    DISPLAY_WIDTH = 320
    DISPLAY_HEIGHT = 240

    # create the display
    display = ILI9341(
        display_bus,
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        rotation=180,  # The rotation can be adjusted to match your configuration.
        auto_refresh=True,
        native_frames_per_second=90,
    )

    # reset the display to show nothing.
    display.show(None)
else:
    # built-in display
    display = board.DISPLAY

print("Display is started")

# load all the fonts
print("loading fonts...")


# Setup file locations for BDF font files
font_files = [
    "fonts/Helvetica-Bold-16.bdf",
    #            'fonts/BitstreamVeraSans-Roman-24.bdf',
    #            'fonts/BitstreamVeraSans-Roman-16.bdf',
    #            'fonts/Fayette-HandwrittenScript-64.bdf',
]

font_list = []

for i, font_file in enumerate(font_files):

    if use_builtin_font:
        this_font = (
            terminalio.FONT
        )  # comment this out to switch back to BDF loaded fonts
    else:
        from adafruit_bitmap_font import bitmap_font

        this_font = bitmap_font.load_font(font_file)

    font_list.append(this_font)


preload_the_glyphs = (
    True  # set this to True if you want to preload the font glyphs into memory
)
# preloading the glyphs will help speed up the rendering of text but will use more RAM

if preload_the_glyphs:

    # identify the glyphs to load into memory -> increases rendering speed
    glyphs = b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.:?! "

    print("loading glyphs...")
    for font in font_list:
        if font is not terminalio.FONT:
            font.load_glyphs(glyphs)

    print("Glyphs are loaded.")

print("Fonts completed loading.")

# create group
import gc

gc.collect()
print("After creating Group,  Memory free: {}".format(gc.mem_free()))


my_string = "Welcome to using displayio on CircuitPython!"

gc.collect()
label_start_memory = gc.mem_free()
start_time = time.monotonic()

bmap_label = label.Label(
    font=font_list[0],
    text=my_string,
    color=0xFFFFFF,
    max_glyphs=len(my_string),
    background_color=0xFF0000,
    padding_bottom=0,
    padding_left=0,
    padding_right=0,
    padding_top=0,
    background_tight=False,
    x=10,
    y=30,
    line_spacing=1.25,
    scale=my_scale,
)
end_time = time.monotonic()

gc.collect()
label_end_memory = gc.mem_free()

bmap_group = displayio.Group(max_size=1)  # Create a group for displaying
bmap_group.append(bmap_label)


print("***")
print("{} memory used: {}".format(version, label_start_memory - label_end_memory))
print("{} time to process: {} seconds".format(version, end_time - start_time))
display.auto_refresh = True

display.show(bmap_group)

while True:
    pass
