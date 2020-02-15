"""
This examples shows the use color and background_color
"""
import board
import terminalio
from adafruit_display_text import label


text = " Color Background Hello world"
text_area = label.Label(terminalio.FONT, text=text, color=0x0000FF, backgroud_color=0xFFAA00)
text_area.x = 10
text_area.y = 10
board.DISPLAY.show(text_area)
while True:
    pass
