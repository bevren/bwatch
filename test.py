import machine
import st7789
import utime
import vga1_bold_16x32 as font
import random

def center(text):
    length = len(text)
    tft.text(
        font,
        text,
        tft.width() // 2 - length // 2 * font.WIDTH,
        tft.height() // 2 - font.HEIGHT,
        st7789.WHITE,
        st7789.RED)

def main():
    
    tft.fill(st7789.RED)
    center("Hello!")
    utime.sleep(2)
    tft.fill(st7789.BLACK)

    while True:
        for rotation in range(4):
            tft.rotation(rotation)
            tft.fill(0)
            col_max = tft.width() - font.WIDTH*6
            row_max = tft.height() - font.HEIGHT

            for _ in range(128):
                tft.text(
                    font,
                    "Hello!",
                    random.randint(0, col_max),
                    random.randint(0, row_max),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8)),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8)))
                
                
main()