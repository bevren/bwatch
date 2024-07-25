import time
import tft
import st7789
import screen_manager
import vga1_bold_16x32 as font

s_manager = screen_manager.ScreenManager()
screen = tft.TFT()
RED = st7789.RED
BLUE = st7789.BLUE
WHITE = st7789.WHITE
MAGENTA = st7789.MAGENTA
BLACK = st7789.BLACK

def millis():
    return time.ticks_ms()

def delay(delay):
    i = time.ticks_ms()
    while time.ticks_ms() - i <= delay:
        pass

def center(text):
    length = len(text)
    screen.text(
        font,
        text,
        screen.width() // 2 - length // 2 * font.WIDTH,
        0,
        WHITE)
    
def dead_center(text):
    length = len(text)
    screen.text(
        font,
        text,
        screen.width() // 2 - length // 2 * font.WIDTH,
        screen.height() // 2 - font.HEIGHT // 2,
        WHITE)





