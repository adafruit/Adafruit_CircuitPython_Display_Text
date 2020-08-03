# Sample code using the textMap library and the "textBox" wrapper class
# Creates four textBox instances
# Inserts each textBox into a tileGrid group
# Writes text into the box one character at a time
# Moves the position of the textBox around the display
# Clears each textBox after the full string is written (even if the text is outside of the box)

#import textmap
#from textmap import textBox

import board
import displayio
import time
import terminalio
import fontio
import sys
import busio
#from adafruit_st7789 import ST7789
from adafruit_ili9341 import ILI9341


# Use these two options to decide which system and font to use

##########
use_bitmap_label=True
##########
use_builtin_font=False
##########

my_scale=1

if use_bitmap_label: # use bitmap_label.py library (Bitmap)
    from adafruit_display_text import bitmap_label as label
    myString6='bitmap_label -->'
    label6_anchor_point=(1,0.5)
    label6_anchored_position=(200,200)

    version='bitmap_label.py'

else: # use label.py library (TileGrid)
    from adafruit_display_text import label as label
    myString6='<-- label'
    label6_anchor_point=(0,0.5)
    label6_anchored_position=(50,200)

    version='label.py'


#  Setup the SPI display

print('Starting the display...') # goes to serial only
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D9 # arbitrary, pin not used
tft_dc = board.D10
tft_backlight = board.D12
tft_reset=board.D11

while not spi.try_lock():
    spi.configure(baudrate=32000000)
    pass
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

print('spi.frequency: {}'.format(spi.frequency))

DISPLAY_WIDTH=320
DISPLAY_HEIGHT=240

#display = ST7789(display_bus, width=240, height=240, rotation=0, rowstart=80, colstart=0)
display = ILI9341(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180, auto_refresh=True)

display.show(None)

print ('Display is started')


# load all the fonts
print('loading fonts...')

import terminalio


fontList = []
fontHeight = []

##### the BuiltinFont terminalio.FONT has a different return strategy for get_glyphs and 
# is currently not handled by these functions.
#fontList.append(terminalio.FONT)
#fontHeight = [10] # somehow the terminalio.FONT needs to be adjusted to 10

# Load some proportional fonts
fontFiles =   [
            'fonts/Helvetica-Bold-16.bdf',
#            'fonts/BitstreamVeraSans-Roman-24.bdf', # Header2
#            'fonts/BitstreamVeraSans-Roman-16.bdf', # mainText
#            'fonts/Fayette-HandwrittenScript-64.bdf',
            ]

from adafruit_bitmap_font import bitmap_font

for i, fontFile in enumerate(fontFiles):
    thisFont = bitmap_font.load_font(fontFile) 

    if use_builtin_font:
        thisFont=terminalio.FONT  # comment this out to switch back to BDF loaded fonts

    fontList.append(thisFont)
    fontHeight.append( thisFont.get_glyph(ord("M")).height ) 



preloadTheGlyphs= True # set this to True if you want to preload the font glyphs into memory
    # preloading the glyphs will help speed up the rendering of text but will use more RAM

if preloadTheGlyphs:

    # identify the glyphs to load into memory -> increases rendering speed
    glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.:?! '

    print('loading glyphs...')
    for font in fontList:
        if font is not terminalio.FONT:
            font.load_glyphs(glyphs)

    print('Glyphs are loaded.')


#for char in glyphs:
#    my_glyph=font.get_glyph(char)
#    print('char: {}, size x,y ({},{}) offset x,y ({},{})'.format(chr(char), my_glyph.width, my_glyph.height, my_glyph.dx, my_glyph.dy))

print('Fonts completed loading.')

# create group 
import gc

#tileGridList=[] # list of tileGrids
#print( 'After creating Group,  Memory free: {}'.format(gc.mem_free()) )


myString12=('Bug Juice ({[]}) \'Monsters!\"\'\npuppy jump ({[]})')
myString34='\n none ' 
myString_bitmap_label='bitmap_label'
myString_label='label                               bitmap_label'


gc.collect()
label_start_memory=gc.mem_free()
bmap_label = label.Label(font=fontList[0], text=myString12, color=0xFFFFFF, max_glyphs=len(myString12),
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


bmap_label2 = label.Label(font=fontList[0], text=myString12, color=0xFFFFFF, max_glyphs=len(myString12),
                                background_color=0xFF0000,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=True,
                                x=10,
                                y=90,
                                line_spacing=1.25,
                                scale=my_scale,
                                #anchored_position=(10,60),
                                )
label3_padding=0
bmap_label3 = label.Label(font=fontList[0], text=myString34, 
                                color=0x000000, 
                                #color=0xFF00FF,
                                max_glyphs=len(myString34),
                                background_color=0xFFFF00,
                                #background_color=None,
                                padding_bottom=label3_padding,
                                padding_left=label3_padding,
                                padding_right=label3_padding,
                                padding_top=label3_padding,
                                background_tight=False,
                                x=10,
                                y=150,
                                line_spacing=1.25,
                                scale=my_scale,
                                anchor_point=(0,0),
                                anchored_position=(200,150),
                                )

bmap_label4 = label.Label(font=fontList[0], text=myString34, 
                                color=0x000000,
                                #color=0xFF00FF, 
                                max_glyphs=len(myString34),
                                background_color=0xFFFF00,
                                #background_color=None,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=True,
                                x=10,
                                y=150,
                                line_spacing=1.25,
                                scale=my_scale,
                                #anchored_position=(10,150),
                                )

bmap_label5 = label.Label(font=fontList[0], text=myString_label, color=0x000000, max_glyphs=len(myString_label),
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
                                #anchored_position=(10,200),
                                )


bmap_label6 = label.Label(font=fontList[0], text=myString6, color=0xFFFFFF, max_glyphs=len(myString6),
                                background_color=0x000000,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=True,
                                x=10,
                                y=200,
                                line_spacing=1.25,
                                anchor_point=label6_anchor_point,
                                anchored_position=label6_anchored_position,
                                scale=my_scale,
                                )



gc.collect()
label_end_memory=gc.mem_free()

bmap_group = displayio.Group( max_size=6 ) # Create a group for displaying
#bmap_group.append(bmap_label)
#bmap_group.append(bmap_label2)
#bmap_group.append(bmap_label3)
bmap_group.append(bmap_label4)
#bmap_group.append(bmap_label5)
#bmap_group.append(bmap_label6)


print('***')
print('{} memory used: {}'.format(version, label_start_memory-label_end_memory))
display.auto_refresh=True

#time.sleep(0.1)
display.show(bmap_group)

while True:
    pass



