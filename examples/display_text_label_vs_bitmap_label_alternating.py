# Sample for comparing label and bitmap_label positioning with Builtin or loaded BDF fonts

# pylint: disable=no-member

import gc
import time
import board
import displayio
import terminalio
from adafruit_bitmap_font import bitmap_font

from adafruit_display_text import bitmap_label

from adafruit_display_text import label

# pylint: disable=no-member

#  Setup the SPI display
##########
# Use this Boolean variables to select which font style to use
##########
use_builtinfont = True  # Set True to use the terminalio.FONT BuiltinFont,
# Set False to use a BDF loaded font, see "fontFiles" below
##########

# Set scaling factor for display text
my_scale = 1

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

fontList = []

# Load some proportional fonts
fontFiles = [
    "fonts/Helvetica-Bold-16.bdf",
    #            'fonts/BitstreamVeraSans-Roman-24.bdf', # Header2
    #            'fonts/BitstreamVeraSans-Roman-16.bdf', # mainText
]


for i, fontFile in enumerate(fontFiles):

    if use_builtinfont:
        thisFont = (
            terminalio.FONT
        )  # comment this out to switch back to BDF loaded fonts
    else:
        thisFont = bitmap_font.load_font(fontFile)

    fontList.append(thisFont)


preload_glyphs = (
    True  # set this to True if you want to preload the font glyphs into memory
)
# preloading the glyphs will help speed up the rendering of text but will use more RAM

if preload_glyphs:

    # identify the glyphs to load into memory -> increases rendering speed
    glyphs = b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.:?! "

    print("loading glyphs...")
    for font in fontList:
        if font is not terminalio.FONT:
            font.load_glyphs(glyphs)

    print("Glyphs are loaded.")


print("Fonts completed loading.")

# create group

my_string1 = "This is a label.py and\nbitmap_label.py comparison."
my_string23 = "none"
my_string_bitmap_label = "bitmap_label"
my_string_label = "label                               bitmap_label"


#####
# Create the "bitmap_label.py" versions of the text labels.

gc.collect()
bitmap_label_start = gc.mem_free()

bmap_label1 = bitmap_label.Label(
    font=fontList[0],
    text=my_string1,
    color=0xFFFFFF,
    max_glyphs=len(my_string1),
    background_color=0xFF0000,
    padding_bottom=0,
    padding_left=0,
    padding_right=0,
    padding_top=0,
    background_tight=True,
    x=10,
    y=60,
    line_spacing=1.25,
    scale=my_scale,
    anchor_point=(0.5, 0),
    anchored_position=(160, 50),
)
label2_padding = 10
bmap_label2 = bitmap_label.Label(
    font=fontList[0],
    text=my_string23,
    color=0x000000,
    max_glyphs=len(my_string23),
    background_color=0xFFFF00,
    padding_bottom=label2_padding,
    padding_left=0,
    padding_right=0,
    padding_top=label2_padding,
    background_tight=False,
    x=10,
    y=100,
    line_spacing=1.25,
    scale=my_scale,
    anchor_point=(0, 0),
    anchored_position=(200, 150),
)

bmap_label3 = bitmap_label.Label(
    font=fontList[0],
    text=my_string23,
    color=0x000000,
    max_glyphs=len(my_string23),
    background_color=0xFFFF00,
    padding_bottom=0,
    padding_left=0,
    padding_right=0,
    padding_top=0,
    background_tight=True,
    x=10,
    y=150,
    line_spacing=1.25,
    scale=my_scale,
)

bmap_label4 = bitmap_label.Label(
    font=fontList[0],
    text=my_string_label,
    color=0x000000,
    max_glyphs=len(my_string_label),
    background_color=0xFFFF00,
    padding_bottom=0,
    padding_left=0,
    padding_right=0,
    padding_top=0,
    background_tight=False,
    x=10,
    y=200,
    line_spacing=1.25,
    scale=my_scale,
)

my_string5 = "bitmap_label -->"
bmap_label5 = bitmap_label.Label(
    font=fontList[0],
    text=my_string5,
    color=0xFFFFFF,
    max_glyphs=len(my_string5),
    background_color=0x000000,
    padding_bottom=0,
    padding_left=0,
    padding_right=0,
    padding_top=0,
    background_tight=True,
    x=10,
    y=200,
    line_spacing=1.25,
    anchor_point=(1, 0.5),
    anchored_position=(200, 200),
    scale=my_scale,
)


gc.collect()
bitmap_label_end = gc.mem_free()

bmap_group = displayio.Group(max_size=5)  # Create a group for displaying
bmap_group.append(bmap_label1)
bmap_group.append(bmap_label2)
bmap_group.append(bmap_label3)
bmap_group.append(bmap_label4)
bmap_group.append(bmap_label5)


#####
# Create the "label.py" versions of the text labels.

gc.collect()
label_start = gc.mem_free()

label1 = label.Label(
    font=fontList[0],
    text=my_string1,
    color=0xFFFFFF,
    max_glyphs=len(my_string1),
    background_color=0xFF0000,
    padding_bottom=0,
    padding_left=0,
    padding_right=0,
    padding_top=0,
    background_tight=True,
    x=10,
    y=60,
    line_spacing=1.25,
    scale=my_scale,
    anchor_point=(0.5, 0),
    anchored_position=(160, 50),
)

label2 = label.Label(
    font=fontList[0],
    text=my_string23,
    color=0x000000,
    max_glyphs=len(my_string23),
    background_color=0xFFFF00,
    padding_bottom=label2_padding,
    padding_left=0,
    padding_right=0,
    padding_top=label2_padding,
    background_tight=False,
    x=10,
    y=100,
    line_spacing=1.25,
    scale=my_scale,
    anchor_point=(0, 0),
    anchored_position=(200, 150),
)

label3 = label.Label(
    font=fontList[0],
    text=my_string23,
    color=0x000000,
    max_glyphs=len(my_string23),
    background_color=0xFFFF00,
    padding_bottom=0,
    padding_left=0,
    padding_right=0,
    padding_top=0,
    background_tight=True,
    x=10,
    y=150,
    line_spacing=1.25,
    scale=my_scale,
)

label4 = label.Label(
    font=fontList[0],
    text=my_string_label,
    color=0x000000,
    max_glyphs=len(my_string_label),
    background_color=0xFFFF00,
    padding_bottom=0,
    padding_left=0,
    padding_right=0,
    padding_top=0,
    background_tight=True,
    x=10,
    y=200,
    line_spacing=1.25,
    scale=my_scale,
)


my_string5 = "<-- label"
label5 = label.Label(
    font=fontList[0],
    text=my_string5,
    color=0xFFFFFF,
    max_glyphs=len(my_string5),
    background_color=0x000000,
    padding_bottom=0,
    padding_left=0,
    padding_right=0,
    padding_top=0,
    background_tight=False,
    x=10,
    y=200,
    line_spacing=1.25,
    anchor_point=(0, 0.5),
    anchored_position=(50, 200),
    scale=my_scale,
)

gc.collect()
label_end = gc.mem_free()

label_group = displayio.Group(max_size=5)  # Create a group for displaying
label_group.append(label1)
label_group.append(label2)
label_group.append(label3)
label_group.append(label4)
label_group.append(label5)


print("***")

display.auto_refresh = True

while True:
    print("bitmap_label")
    time.sleep(0.1)
    display.show(bmap_group)

    time.sleep(2)

    print("label")
    time.sleep(0.1)
    display.show(label_group)
    time.sleep(2)
