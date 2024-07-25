from watch import center, dead_center
import time

from state_machine import StateMachine, State

from components import Text, Menu, MenuItem
import ble_manager
import tft
import screen_manager

screen = tft.TFT()
s_manager = screen_manager.ScreenManager()
ble = ble_manager.BLE()

sm = StateMachine()


class ModalConfirm(State):
    def __init__(self):
        super().__init__("modal_confirm")
        self.menu = Menu(10, 48)
        
        
        self.menu.add(MenuItem("Yes", cb=self.on_item_selected))
        self.menu.add(MenuItem("No", cb=self.on_item_selected))
    
    def on_item_selected(self, menu_item):
        
        if menu_item.name == "Yes":
            if self.locals.get("on_confirm") is not None:
                self.locals["on_confirm"]()
        else:
            if self.locals.get("on_reject") is not None:
                self.locals["on_reject"]()
                
        sm.pop()
    
    def on_enter(self):
        screen.fill(tft.BLACK)
        
        title = self.locals.get('title')
        
        center(title if title is not None else "Confirm")
        screen.hline(10, 37, 220, tft.WHITE)
        
        self.menu.update()
    
    def on_update(self):
        pass
    
    def on_event(self, event_name, data):
        if event_name == "button_up":
            self.menu.select()
            
        if event_name == "encoder_left":
            self.menu.move_up()
        
        if event_name == "encoder_right":
            self.menu.move_down()
    
    def on_exit(self):
        self.menu.reset()


class ServerPage(State):
    def __init__(self, name):
        super().__init__(name)
        self.menu = Menu(10, 48)
        self._start = MenuItem("stop", cb=self.on_start_stop_selected)
        self.menu.add(self._start)
        self.menu.add(MenuItem("back", cb=lambda x: sm.pop()))
        
        
    def on_modal_confirmed(self):
        if ble.advertising():
            ble._stop_advertise()
            print("stopped advertising")
        else:
            ble._advertise()
            print("started advertising")
        
    def on_modal_rejected(self):
        print("rejected")
    
    def on_start_stop_selected(self, menu_item):
        
        title = "Stop Adv" if ble.advertising() else "Start Adv"
            
        sm.push("modal_confirm", data={'title' : title, 'on_confirm' : self.on_modal_confirmed, 'on_reject' : self.on_modal_rejected })
    
    def on_dc_all_selected(self, menu_item):
        ble.disconnect_all()
        self.menu.remove(menu_item)
        self.menu.update()
    
    def on_enter(self):
        
        screen.fill(tft.BLACK)
        center("Server")
        
        if ble.advertising():
            self._start.set_text("stop adv")
            if ble.is_connected():
                mi = self.menu.get("disconnect all")
                if mi is None:
                    self.menu.add(MenuItem("disconnect all", cb=self.on_dc_all_selected))
            else:
                mi = self.menu.get("disconnect all")
                if mi is not None:
                    self.menu.remove(mi)
        else:
            self._start.set_text("start adv")
            
        self.menu.update()
        
    def on_update(self):
        pass
    
    def on_event(self, event_name, data):
        if event_name == "button_up":
            self.menu.select()
            
        if event_name == "encoder_left":
            self.menu.move_up()
        
        if event_name == "encoder_right":
            self.menu.move_down()
    
    def on_exit(self):
        self.menu.reset()

class MainPage(State):
    def __init__(self, name):
        super().__init__(name)
        self.menu = Menu(10, 48)
        
        self.menu.add(MenuItem("info", cb=self.on_item_selected))
        self.menu.add(MenuItem("test", cb=self.on_item_selected))
        self.menu.add(MenuItem("server", cb=self.on_item_selected))
        self.menu.add(MenuItem("client", cb=self.on_item_selected))
        self.menu.add(MenuItem("exit", cb=lambda x: s_manager.pop()))
    
    def on_modal_confirmed(self):
        if ble.active():
            ble.stop()
            print("stopped advertising")
        else:
            ble.start()
            print("started advertising")
        
    def on_modal_rejected(self):
        print("rejected")
    
    def on_item_selected(self, menu_item):
        print(menu_item.name)
        #sm.push(menu_item.name, data={'text' : {'me' : 'yo'}, 'kral' : self.test })
        if menu_item.name == "test":
            title = ""
            if ble.active():
                title = "Disable BLE"
            else:
                title = "Enable BLE"
                
            sm.push("modal_confirm", data={'title' : title, 'on_confirm' : self.on_modal_confirmed, 'on_reject' : self.on_modal_rejected })
        else:
            sm.push(menu_item.name)
            
    
    
    def on_enter(self):
        
        screen.fill(tft.BLACK)
        center("Bluetooth")
        self.menu.update()
    
    def on_update(self):
        pass
    
    def on_event(self, event_name, data):
        if event_name == "button_up":
            self.menu.select()
            
        if event_name == "encoder_left":
            self.menu.move_up()
        
        if event_name == "encoder_right":
            self.menu.move_down()
    
    def on_exit(self):
        pass
    
class InfoPage(State):
    def __init__(self, name):
        super().__init__(name)
    
    def on_enter(self):
        screen.fill(tft.RED)
        center("Info")
        
    
    def on_update(self):
        pass
    
    def on_event(self, event_name, data):
        if event_name == "button_up":
            sm.pop()
    
    def on_exit(self):
        pass

def enter():
    print("start bluetooth")
    
    sm.add(MainPage("main"))
    sm.add(InfoPage("info"))
    sm.add(ServerPage("server"))
    sm.add(ModalConfirm())

def event(event_name, data):
    sm.send_event(event_name, data)
#     if event_name == "button_up":
#        s_manager.pop()

def update():
    #print("update settings")
    sm.update()

def leave():
    print("bluetooth exit ")

