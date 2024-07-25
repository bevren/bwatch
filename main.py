
import time
from machine import Pin
import sys

import screen_manager
import tft
import ble_manager
import input_manager
import bluetooth
import socket_manager

# try:
#     exec('import  apps.' + name, {} )
#     sys.modules["apps."+ name].enter()
#     del sys.modules["apps."+name]
# except ImportError:
#     print("failed to import")
#     return

def main():
    tft.init()
    
    screen = tft.TFT()
    screen.fill(tft.BLACK)
    
    import vga1_bold_16x32 as font
    text = "Loading..."
    length = len(text)
    screen.text(
        font,
        text,
        screen.width() // 2 - length // 2 * font.WIDTH,
        screen.height() // 2 - font.HEIGHT ,
        tft.WHITE)
    
    screen_manager.init()
    ble_manager.init()
    socket_manager.init()
    
    def on_rcv(data):
        print(data)
    
    server = socket_manager.Server()
    ble = ble_manager.BLE()
    ble.on_write(on_rcv)
    sm = screen_manager.ScreenManager()
    
    while True:
        
        server.update()
        input_manager.update()
        sm.update()
        
        time.sleep_ms(10)
        



if __name__ == "__main__":
    main()
    