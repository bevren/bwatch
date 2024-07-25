import time
from machine import Pin
from rotary_irq import RotaryIRQ
import screen_manager

encoder_switch_pin = Pin(27, Pin.IN, Pin.PULL_UP)
r = RotaryIRQ(pin_num_clk=25,
              pin_num_dt=26,
              min_val=0,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_UNBOUNDED)

rotary_val_old = 0
rotary_button_old = 1


def update():
    
    global rotary_val_old
    global rotary_button_old
    
    
    sm = screen_manager.ScreenManager()
    
    rotary_button_new = encoder_switch_pin.value()
    rotary_val_new = r.value()

    if rotary_val_old != rotary_val_new:
        if rotary_val_new < rotary_val_old:
            sm.send_event("encoder_left", 0)
            #print("left")
        else:
            sm.send_event("encoder_right", 0)
            #print("right")
        
        rotary_val_old = rotary_val_new
        #print('result =', rotary_val_new)
        
    if rotary_button_old == 1 and rotary_button_new == 0:
        sm.send_event("button_down", 0)
    elif rotary_button_old == 0 and rotary_button_new == 0:
        sm.send_event("button_held", 0)
    elif rotary_button_old == 0 and rotary_button_new == 1:
        sm.send_event("button_up", 0)
    
    rotary_button_old = rotary_button_new


