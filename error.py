from watch import center, dead_center
import time
import network

from state_machine import StateMachine, State

from components import Text,ScrollText
import ble_manager
import tft
import screen_manager
from socket_manager import Server
import vga1_8x16
import vga2_8x16

screen = tft.TFT()
s_manager = screen_manager.ScreenManager()
test = None

def enter(error=None):
    print("start error")
    screen.fill(tft.BLACK)
    center("error!")
    
    if error is None:
        error = "No Error"
    
    global test
    test = ScrollText(20, 40, error, font=vga1_8x16)

def event(event_name, data):
    if event_name == "button_up":
        s_manager.pop()
       
    if event_name == "encoder_left":
        test.up()
        
    if event_name == "encoder_right":
        test.down()

def update():
    #print("update settings")
    pass

def leave():
    print("leave error")