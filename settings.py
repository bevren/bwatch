from watch import screen, RED, BLACK, MAGENTA, BLUE, s_manager,center
import time

from components import Text
import ble_manager

test = None
ble = ble_manager.BLE()

def enter():
    print("start settings")
    screen.fill(BLACK)
    center("settings!")
    
    test = Text(20, 40, "Hello Mello")
    
    Text(20, test.bottom(), str(test.width()))
    
    test.update(fg=MAGENTA if ble.advertising() else RED)

def event(event_name, data):
    if event_name == "button_up":
       s_manager.pop()
    if event_name == "button_held":
        print("held")

def update():
    #print("update settings")
    pass

def leave():
    print("exit ")

