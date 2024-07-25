import machine
import st7789

_tft = None
BLACK = st7789.BLACK
RED = st7789.RED
WHITE = st7789.WHITE


def init():
    
    global _tft
    if _tft != None:
        print("tft already initialized")
        return
    else:
        spi = machine.SPI(2, baudrate=40000000, polarity=1, sck=machine.Pin(18), mosi=machine.Pin(23))
        _tft = st7789.ST7789(spi, 240, 240, reset=machine.Pin(4, machine.Pin.OUT), dc=machine.Pin(2, machine.Pin.OUT))
        _tft.init()
        print("initializing tft...")


def TFT():
    global _tft
    return _tft