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

from adafruit_display_text import bitmap_label
#from adafruit_display_text import bitmap_label as Label

from adafruit_display_text import label

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
#            'fonts/Helvetica-Bold-16.bdf',
#            'fonts/BitstreamVeraSans-Roman-24.bdf', # Header2
            'fonts/BitstreamVeraSans-Roman-16.bdf', # mainText
            ]

from adafruit_bitmap_font import bitmap_font

for i, fontFile in enumerate(fontFiles):
    thisFont = bitmap_font.load_font(fontFile) 


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


myString12=('Bit Juice ({[]}) Monsters!\"\'ABCDEFGHIJKLMNOPQRSTUVWXYZ\npuppy bug jump ({[]})')
myString34=' none ' 
myString_bitmap_label='bitmap_label'
myString_label='label                               bitmap_label'
#myString=('Full Screen Size: This is a stationary box, not a stationery box')
#myString=('Full Screen Size: This is a stationary box, not a stationery box. Full Screen Size: This is a stationary box, not a stationery box. Full Screen Size: This is a stationary box, not a stationery box. Full Screen Size: This is a stationary box, not a stationery box. Full Screen Size: This is a stationary box, not a stationery box. Full Screen Size: This is a stationary box, not a stationery box. Full Screen Size: This is a stationary box, not a stationery box. Full Screen Size: This is a stationary box, not a stationery box. Full Screen Size: This is a stationary box, not a stationery box. Full Screen Size: This is a stationary box, not a stationery box.')
#myString=('MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM')
#print('myString: {}'.format(myString))
#print('string length: {}'.format(len(myString)))

gc.collect()
bitmap_label_start=gc.mem_free()
bmap_label = bitmap_label.Label(font=fontList[0], text=myString12, color=0xFFFFFF, max_glyphs=len(myString12),
                                background_color=0xFF0000,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=False,
                                x=10,
                                y=10,
                                line_spacing=1.25,
                                #anchored_position=(10,10),
                                )

#print("***bmap_label[0] (x,y): ({},{})".format(bmap_label[0].x, bmap_label[0].y))
#
bmap_label2 = bitmap_label.Label(font=fontList[0], text=myString12, color=0xFFFFFF, max_glyphs=len(myString12),
                                background_color=0xFF0000,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=True,
                                x=10,
                                y=60,
                                line_spacing=1.25,
                                #anchored_position=(10,60),
                                )
label3_padding=0
bmap_label3 = bitmap_label.Label(font=fontList[0], text=myString34, color=0x000000, max_glyphs=len(myString34),
                                background_color=0xFFFF00,
                                padding_bottom=label3_padding,
                                padding_left=label3_padding,
                                padding_right=label3_padding,
                                padding_top=label3_padding,
                                background_tight=False,
                                x=10,
                                y=100,
                                line_spacing=1.25,
                                #anchored_position=(10,100),
                                )

bmap_label4 = bitmap_label.Label(font=fontList[0], text=myString34, color=0x000000, max_glyphs=len(myString34),
                                background_color=0xFFFF00,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=True,
                                x=10,
                                y=150,
                                line_spacing=1.25,
                                #anchored_position=(10,150),
                                )
#bmap_label5 = bitmap_label.Label(font=fontList[0], text=myString_bitmap_label, color=0x000000, max_glyphs=len(myString_bitmap_label),
bmap_label5 = bitmap_label.Label(font=fontList[0], text=myString_label, color=0x000000, max_glyphs=len(myString_label),
                                background_color=0xFFFF00,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=False,
                                x=10,
                                y=200,
                                line_spacing=1.25,
                                #anchored_position=(10,200),
                                )

myString6='bitmap_label -->'
bmap_label6 = bitmap_label.Label(font=fontList[0], text=myString6, color=0xFFFFFF, max_glyphs=len(myString6),
                                background_color=0x000000,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=True,
                                x=10,
                                y=200,
                                line_spacing=1.25,
                                anchor_point=(1,0.5),
                                anchored_position=(200,200),
                                )



gc.collect()
bitmap_label_end=gc.mem_free()

bmap_group = displayio.Group( max_size=6 ) # Create a group for displaying
bmap_group.append(bmap_label)
bmap_group.append(bmap_label2)
bmap_group.append(bmap_label3)
bmap_group.append(bmap_label4)
bmap_group.append(bmap_label5)
bmap_group.append(bmap_label6)



gc.collect()
label_start=gc.mem_free()

label1 = label.Label(font=fontList[0], text=myString12, color=0xFFFFFF, max_glyphs=len(myString12),
                                background_color=0xFF0000,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=False,
                                x=10,
                                y=10,
                                line_spacing=1.25,
                                #anchored_position=(10,10),
                                )

#print('label1 bounding_box: {}'.format(label1.bounding_box))
#print('label1[0].width: {}, height: {}, x,y: ({},{})'.format(label1[0].tile_width, label1[0].tile_height, label1[0].x, label1[0].y))

#print("***label1[0] (x,y): ({},{})".format(label1[0].x, label1[0].y))
#print("***label1 (x,y): ({},{})".format(label1.x, label1.y))


label2 = label.Label(font=fontList[0], text=myString12, color=0xFFFFFF, max_glyphs=len(myString12),
                                background_color=0xFF0000,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=True,
                                x=10,
                                y=60,
                                line_spacing=1.25,
                                #anchored_position=(10,60),
                                )

label3 = label.Label(font=fontList[0], text=myString34, color=0x000000, max_glyphs=len(myString34),
                                background_color=0xFFFF00,
                                padding_bottom=label3_padding,
                                padding_left=label3_padding,
                                padding_right=label3_padding,
                                padding_top=label3_padding,
                                background_tight=False,
                                x=10,
                                y=100,
                                line_spacing=1.25,
                                #anchored_position=(10,100),
                                )

label4 = label.Label(font=fontList[0], text=myString34, color=0x000000, max_glyphs=len(myString34),
                                background_color=0xFFFF00,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=True,
                                x=10,
                                y=150,
                                line_spacing=1.25,
                                #anchored_position=(10,150),
                                )

label5 = label.Label(font=fontList[0], text=myString_label, color=0x000000, max_glyphs=len(myString_label),
                                background_color=0xFFFF00,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=True,
                                x=10,
                                y=200,
                                line_spacing=1.25,
                                #anchored_position=(10,200),
                                )


myString6 = '<-- label'
label6 = label.Label(font=fontList[0], text=myString6, color=0xFFFFFF, max_glyphs=len(myString6),
                                background_color=0x000000,
                                padding_bottom=0,
                                padding_left=0,
                                padding_right=0,
                                padding_top=0,
                                background_tight=False,
                                x=10,
                                y=200,
                                line_spacing=1.25,
                                anchor_point=(0,0.5),
                                anchored_position=(50,200),
                                )

gc.collect()
label_end=gc.mem_free()

label_group = displayio.Group( max_size=6 ) # Create a group for displaying
label_group.append(label1)
label_group.append(label2)
label_group.append(label3)
label_group.append(label4)
label_group.append(label5)
label_group.append(label6)



print('bitmap_label mem usage: {}, label mem usage: {}'.format(bitmap_label_start-bitmap_label_end, label_start-label_end))


gc.collect()
memBeforeLoop=gc.mem_free()
print('After display.show(myGroup), just before loop start  Memory free: {}'.format(memBeforeLoop) )

print('bmap_label bounding_box: {}'.format(bmap_label.bounding_box))
print('label1 bounding_box: {}'.format(label1.bounding_box))
print('bmap_label2 bounding_box: {}'.format(bmap_label2.bounding_box))
print('label2 bounding_box: {}'.format(label2.bounding_box))


print('***')
print('bmap_label3 bounding_box: {}'.format(bmap_label3.bounding_box))
print('bmap_label3 x,y: {},{}'.format(bmap_label3.x, bmap_label3.y))
print('label3 bounding_box: {}'.format(label3.bounding_box))
print('label3 x,y: {},{}'.format(label3.x, label3.y))
print('***')


print('bmap_label4 bounding_box: {}'.format(bmap_label4.bounding_box))
print('label4 bounding_box: {}'.format(label4.bounding_box))
print('bmap_label5 bounding_box: {}'.format(bmap_label5.bounding_box))
print('label5 bounding_box: {}'.format(label5.bounding_box))

print('**************')
print('before ** bmap_label3 x,y: {},{}'.format(bmap_label3.x, bmap_label3.y))
print('1 - bmap_label3 bounding_box: {}'.format(bmap_label3.bounding_box))  #### how is this changing it?
print('before ** bmap_label3 x,y: {},{}'.format(bmap_label3.x, bmap_label3.y))
bmap_label3.anchor_point=(0,0)
bmap_label3.anchored_position=(200,150)

label3.anchor_point=(0,0)
label3.anchored_position=(200,150)


print('***')
print('bmap_label3 bounding_box: {}'.format(bmap_label3.bounding_box))
print('bmap_label3 x,y: {},{}'.format(bmap_label3.x, bmap_label3.y))
print('bmap_label3 tilegrid.x,y: {},{}'.format(bmap_label3.tilegrid.x, bmap_label3.tilegrid.y))
print('bmap_label3[0].x,y: {},{}'.format(bmap_label3[0].x, bmap_label3[0].y))
print('****')
print('label3 bounding_box: {}'.format(label3.bounding_box))
print('label3 x,y: {},{}'.format(label3.x, label3.y))
print('label3 tilegrid.x,y: {},{}'.format(label3[1].x, label3[1].y))

print('***')

display.auto_refresh=True

while True:
    print('bitmap_label')
    time.sleep(0.1)
    display.show(bmap_group)
    
    time.sleep(2)

    print('label')
    time.sleep(0.1)
    display.show(label_group)
    time.sleep(2)






