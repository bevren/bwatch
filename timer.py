from watch import screen, RED, BLACK, MAGENTA, BLUE, s_manager,center
import time

def enter():
    print("start timer")
    screen.fill(BLUE)
    center("timer!")

def event(event_name, data):
    if event_name == "button_up":
       s_manager.pop()
    if event_name == "button_held":
        print("held")

def update():
    #print("update settings")
    pass

def leave():
    print("timer exit ")
