# The MIT License (MIT)
#
# Copyright (c) 2020 Kevin Matocha
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
"""
`bitmap_label`
================================================================================

Text graphics handling for CircuitPython, including text boxes


* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s). Use unordered list & hyperlink rST
   inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

#import terminalio
import displayio

def lineSpacingY(font, lineSpacing):
    # Note: Scale is not implemented at this time, any scaling is pushed up to the Group level
    #fontHeight = font.get_glyph(ord('M')).height
    fontHeight = font.get_bounding_box()[1]
    returnValue = int(lineSpacing * fontHeight)
    return returnValue

def text_bounding_box(text, font, lineSpacing, background_tight=False):  # **** change default background_tight=False

    label_position_yoffset = int( # for calibration with label.py positioning
            (
                font.get_glyph(ord("M")).height
                #- text.count("\n") * font.get_bounding_box()[1] * lineSpacing
                - font.get_bounding_box()[1] * lineSpacing
            )
            / 2
        )

    
    # this empirical approach checks several glyphs for maximum ascender and descender height
    # Alternate option: utilize `font.get_bounding_box()` to get max glyph dimensions
    glyphs = "M j'"     # choose glyphs with highest ascender and lowest
                        # descender, will depend upon font used
    ascender_max = descender_max = 0
    for char in glyphs:
        this_glyph = font.get_glyph(ord(char))
        if this_glyph:
            ascender_max = max(ascender_max, this_glyph.height + this_glyph.dy)
            descender_max = max(descender_max, -this_glyph.dy)
    font_height=ascender_max+descender_max
    font_yoffset=ascender_max

    base_point=(0,0) # entry point for the next glyph

    # calculate dimensions for both "tight" and "loose" bounding boxes
    x1_min=y1_min=x2_max=y2_max=None # initialize the bounding box corners (1:lower left, 2: upper right)

    y_offset=None # Provide the baseline y_offset for the bitmap

    firstline=True # handles special cases for first line

    box_height=0
    box_width=0
    box_height_adder=0

    for char in text:
        if char == '\n': # newline    
            if firstline: # This the first line
                firstline = False
                if background_tight:
                    if y1_min is None:
                        y_offset =  label_position_yoffset
                        box_height_adder = ( lineSpacingY(font, lineSpacing)-lineSpacingY(font, 1) ) + y_offset
                                            # for a leading newline, this adds to the box_height

                    else:
                        y_offset = -y1_min # The bitmap y-offset is the max y-position of the first line
                        
                else: # background is "loose"
                    y_offset = font_yoffset
                    if y1_min is None:
                        box_height_adder = lineSpacingY(font, lineSpacing)

            base_point=(0, base_point[1] + lineSpacingY(font, lineSpacing)) # baseline point for the next glyph

        else:
            myGlyph = font.get_glyph(ord(char))
            if myGlyph == None: # Error checking: no glyph found
                print('Glyph not found: {}'.format(repr(char)))
            else:

                x1=base_point[0]    # x1,y1 = upper left of glyph
                x2=x1+myGlyph.shift_x          # x2,y2 = lower right of glyph
                if background_tight:
                    y1=base_point[1]-(myGlyph.height+myGlyph.dy)    # Upper left corner Note: Positive Y is down
                    y2=y1+myGlyph.height
                else: # background is "loose"
                    y1=base_point[1]-font_yoffset
                    y2=y1+font_height
                base_point=(base_point[0]+myGlyph.shift_x, base_point[1]+myGlyph.shift_y) # update the next baseline point location
                
            # find the min bounding box size incorporating this glyph's bounding box
                if x1_min is not None:
                    x1_min = min(x1, x1_min)
                else:
                    x1_min = min(0, x1) # ****
                if y1_min is not None:
                    y1_min = min(y1, y1_min)
                else:
                    y1_min = y1
                if x2_max is not None:
                    x2_max = max(x2, x2_max)
                else:
                    x2_max = x2
                if y2_max is not None:
                    y2_max = max(y2, y2_max)
                else:
                    y2_max = y2

        if x1_min is not None and x2_max is not None:
            box_width = max(0, x2_max - x1_min)
        if y1_min is not None and y2_max is not None:
            box_height = y2_max - y1_min


        if firstline: # This the first line
            if background_tight:
                y_offset =-y1_min # The bitmap y-offset is the max y-position of the first line
            else: # background is "loose"
                y_offset=font_yoffset

    box_height=max(0, box_height+box_height_adder) # to add any additional height for leading newlines

    return(box_width, box_height, -x1_min, y_offset) # -x1_min is the x_offset





def place_text(
    bitmap, text, font, lineSpacing, xPosition, yPosition, 
    textPaletteIndex=1, 
    backgroundPaletteIndex=0, 
    scale=1,
    printOnlyPixels=True,   # printOnlyPixels = True: only update the bitmap where the glyph pixel 
                            # color is > 0 this is especially useful for script fonts where glyph
                            # bounding boxes overlap
):
    # placeText - Writes text into a bitmap at the specified location.
    #
    # Verify paletteIndex is working properly with * operator, especially if accommodating multicolored fonts
    #
    # Note: Scale is not implemented at this time


    fontHeight = font.get_glyph(ord("M")).height

    bitmapWidth = bitmap.width
    bitmapHeight = bitmap.height

    xStart=xPosition # starting x position (left margin)
    yStart=yPosition

    if backgroundPaletteIndex != 0: # the textbackground is different from the bitmap background
        # draw a bounding box where the text will go

        (ignore, fontLineHeight)=bounding_box('M g', font, lineSpacing, scale) # check height with ascender and descender.
        (boxX, boxY) = bounding_box(text, font, lineSpacing, scale)
        boxY=max(fontLineHeight, boxY)

        for y in range(boxY):
            for x in range(boxX):
                if (xPosition+x < bitmapWidth) and (yPosition+y < bitmapHeight): # check boundaries
                    #bitmap[xPosition+x, yPosition+y]=backgroundPaletteIndex
                    bitmap[(yPosition+y)*bitmapWidth + (xPosition + x)]=backgroundPaletteIndex

    left=right=xStart
    top=bottom=yStart
    #print('##place_text xStart, yStart: {}, {}'.format(xStart, yStart))
    
    for char in text:

        if char == '\n': # newline
            xPosition = xStart # reset to left column
            yPosition = yPosition + lineSpacingY(font, lineSpacing) # Add a newline

        else:

            myGlyph = font.get_glyph(ord(char))

            if myGlyph == None: # Error checking: no glyph found
                print('Glyph not found: {}'.format(repr(char)))
            else:

                right = max(right, xPosition + myGlyph.shift_x)
                if yPosition == yStart:  # first line, find the Ascender height
                    top = min(top, -myGlyph.height - myGlyph.dy)
                bottom = max(bottom, yPosition - myGlyph.dy)

                width = myGlyph.width
                height = myGlyph.height
                # print('glyph width: {}, height: {}'.format(width, height))
                dx = myGlyph.dx
                dy = myGlyph.dy
                shift_x = myGlyph.shift_x
                shift_y = myGlyph.shift_x
                glyph_offset_x = myGlyph.tile_index * width # for type BuiltinFont, this creates the x-offset in the glyph bitmap.
                                                            # for BDF loaded fonts, this should equal 0

                yOffset = fontHeight - height
                for y in range(height):
                    for x in range(width):
                        xPlacement = x + xPosition + dx
                        yPlacement = y + yPosition - height - dy #+ yOffset

                        #left=min(xPlacement, left)
                        #right=max(xPlacement, right)
                        #top=min(yPlacement, top)
                        #bottom=max(yPlacement, bottom)

                        if (
                            (xPlacement >= 0)
                            and (yPlacement >= 0)
                            and (xPlacement < bitmapWidth)
                            and (yPlacement < bitmapHeight)
                        ):

                            # Allows for remapping the bitmap indexes using paletteIndex for background and text.
                            paletteIndexes=(backgroundPaletteIndex, textPaletteIndex)
                        
                            thisPixelColor=paletteIndexes[myGlyph.bitmap[y*myGlyph.bitmap.width + x + glyph_offset_x]]
                            
                            if not printOnlyPixels or thisPixelColor > 0: 
                                # write all characters if printOnlyPixels = False, or if thisPixelColor is > 0
                                bitmap[yPlacement*bitmapWidth + xPlacement] = thisPixelColor
                        elif (yPlacement > bitmapHeight):
                            break
                
                xPosition = xPosition + shift_x

    return (left, top, left+right, bottom-top) # bounding_box 


class Label(displayio.Group):

	# Class variable
    # To save memory, set Bitmap.Label._memory_saver=True, to avoid storing the text string in the class.
    # If set to False, the class saves the text string for future reference. *** use getter
    _memory_saver=True 

    def __init__(
        		self, 
        		font,
                x=0,
                y=0,
                text="",
                max_glyphs=None, # This input parameter is ignored, only present for compatibility with label.py
        		#width, height, 
                color=0xFFFFFF,
        		background_color=None,  
        		line_spacing=1.25,
                background_tight=False,
                padding_top=0,
                padding_bottom=0,
                padding_left=0,
                padding_right=0,
                anchor_point=(0,0),
                anchored_position=None,
                **kwargs
    			):

        if text == "":
            raise RuntimeError("Please provide text string")

        # Scale will be passed to Group using kwargs.
        if "scale" in kwargs.keys():
            self._scale = kwargs["scale"]
        else:
            self._scale = 1

        self._line_spacing=line_spacing

        if self._memory_saver == False:
            self._text = text  # text to be displayed
        
        # limit padding to >= 0 *** raise an error if negative padding is requested
        padding_top = max(0, padding_top)
        padding_bottom = max(0, padding_bottom)
        padding_left = max(0, padding_left)
        padding_right = max(0, padding_right)

        # Calculate the text bounding box

        # Calculate tight box to provide bounding box dimensions to match label for anchor_position calculations
        (tight_box_x, tight_box_y, dummy_x_offset, tight_y_offset) = text_bounding_box(text, font, 
                                                                self._line_spacing, 
                                                                background_tight=True,
                                                                )

        if background_tight:
            box_x=tight_box_x
            box_y=tight_box_y
            x_offset=dummy_x_offset
            y_offset=tight_y_offset
        else:
            (box_x, box_y, x_offset, y_offset) = text_bounding_box(text, font, 
                                                                    self._line_spacing, 
                                                                    background_tight=background_tight,
                                                                    )
        # Calculate the background size including padding
        box_x = box_x + padding_left + padding_right
        box_y = box_y + padding_top + padding_bottom

        # Create the two-color palette 
        self.palette = displayio.Palette(2)
        if background_color is not None:
        	self.palette[0] = background_color
        else:
        	self.palette[0] = 0
        	self.palette.make_transparent(0)
        self.palette[1] = color

        # Create the bitmap and TileGrid
        self.bitmap = displayio.Bitmap(box_x, box_y, len(self.palette)) 

        # Place the text into the Bitmap 
        text_size=place_text(self.bitmap, text, font, self._line_spacing, padding_left+x_offset, padding_top+y_offset)
        
        label_position_yoffset = int(       # To calibrate with label.py positioning
            (
                font.get_glyph(ord("M")).height
                - text.count("\n") * font.get_bounding_box()[1] * self._line_spacing
            )
            / 2
        )

        self.tilegrid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette, 
                                            width=1, height=1, 
                                            tile_width=box_x, tile_height=box_y, 
                                            default_tile=0,
                                            x=0,
                                            y=label_position_yoffset - y_offset,
                                            )

        # instance the Group with super...    super().__init__(
        # this Group will contain just one TileGrid with one contained bitmap
        super().__init__(max_size=1, x=x, y=y, **kwargs) # this will include any arguments, including scale
        self.append(self.tilegrid) # add the bitmap's tilegrid to the group

        #######  *******
        # Set the tileGrid position in the parent based upon anchor_point and anchor_position
        # **** Should scale affect the placement of anchor_position?

        self.bounding_box=(self.tilegrid.x, self.tilegrid.y+(y_offset-tight_y_offset), tight_box_x, tight_box_y)
                            # Update bounding_box values.  Note: To be consistent with label.py, 
                            # this is the bounding box for the text only, not including the background.
                            # ******** Need repair
        # Create the TileGrid to hold the single Bitmap (self.bitmap)

        self._anchored_position=anchored_position
        self.anchor_point=anchor_point
        self.anchored_position=self._anchored_position # sets anchored_position with setter after bitmap is created


    @property
    def anchor_point(self):
        """Point that anchored_position moves relative to.
           Tuple with decimal percentage of width and height.
           (E.g. (0,0) is top left, (1.0, 0.5): is middle right.)"""
        return self._anchor_point

    @anchor_point.setter
    def anchor_point(self, new_anchor_point):
        self._anchor_point = new_anchor_point
        self.anchored_position = self._anchored_position # update the anchored_position using setter

    @property
    def anchored_position(self):
        return self._anchored_position

    @anchored_position.setter
    def anchored_position(self, new_position):

        self._anchored_position=new_position

        # Set anchored_position
        if (self._anchor_point is not None) and (self._anchored_position is not None):
            new_x = int(
                        new_position[0]
                        - self._anchor_point[0] * (self.bounding_box[2] * self._scale)
                        )
            new_y = int(
                new_position[1]
                - (self._anchor_point[1] * self.bounding_box[3] * self.scale)
                + round((self.bounding_box[3] * self.scale) / 2.0)
                        )
            self.x = new_x
            self.y = new_y







