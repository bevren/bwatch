import tft
import screen_manager

screen = tft.TFT()
s_manager = screen_manager.ScreenManager()
bork
def enter():
    screen.fill(tft.BLACK)


def update():
    pass

def leave():
    pass
    
def event(event_name, data):
    if event_name == "button_up":
        s_manager.pop()