from watch import center, dead_center
import time
import network

from state_machine import StateMachine, State

from components import Text, Menu, MenuItem
import ble_manager
import tft
import screen_manager
from socket_manager import Server


screen = tft.TFT()
s_manager = screen_manager.ScreenManager()
ble = ble_manager.BLE()

sm = StateMachine()
server = Server()


def http_get(url):
    import socket
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()

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



class MainPage(State):
    def __init__(self, name):
        super().__init__(name)
        self.menu = Menu(10, 48)
        
    
    def on_sta_modal_confirmed(self):
        
        screen.fill(tft.BLACK)
        
        sta = network.WLAN(network.STA_IF)
        ap = network.WLAN(network.AP_IF)
        
        if sta.active():
            
            if not ap.active() and server.active():
                dead_center("Closing WS")
                server.stop()
            
            dead_center("Closing STA")
            sta.active(False)
        else:
            sta.active(True)
            #"AirTies_Air5343", "nurbatu1991"
            #"AndroidAPpp", "msja9244"
            sta.connect("AirTies_Air5343", "nurbatu1991")
            dead_center("connecting")
            while sta.isconnected() == False:
                pass
            
            dead_center("connected      ")
    
    def on_ap_modal_confirmed(self):
        
        screen.fill(tft.BLACK)
        
        sta = network.WLAN(network.STA_IF)
        ap = network.WLAN(network.AP_IF)
        if ap.active():
            if not sta.active() and server.active():
                dead_center("Closing WS")
                server.stop()
            
            dead_center("Closing AP")
            ap.active(False)
        else:
            ap.active(True)
            dead_center("creating ap")
            ap.config(essid="alooooo",authmode=network.AUTH_WPA_WPA2_PSK, password="123123123")
            
            while ap.active() == False:
                pass
            
            dead_center("created ap  ")
            
            
    def on_ws_modal_confirmed(self):
        
        screen.fill(tft.BLACK)
        
        if server.active():
            dead_center("Closing")
            server.stop()
        else:
            dead_center("creating ws")
            server.start()
            
            while server.active() == False:
                pass
            
            dead_center("created ws ")
            
    def on_modal_rejected(self):
        print("rejected")
    
    def on_sta_selected(self, menu_item):
        print(menu_item.name)
        sm.push("modal_confirm", data={'title' : menu_item.name, 'on_confirm' : self.on_sta_modal_confirmed, 'on_reject' : self.on_modal_rejected })
    
    def on_ap_selected(self, menu_item):
        print(menu_item.name)
        sm.push("modal_confirm", data={'title' : menu_item.name, 'on_confirm' : self.on_ap_modal_confirmed, 'on_reject' : self.on_modal_rejected })
    
    
    def on_ifconfig_selected(self, menu_item):
        sm.push("ifconfig")
    
    def on_ws_selected(self, menu_item):
        #print(menu_item.name)
        sm.push("modal_confirm", data={'title' : menu_item.name, 'on_confirm' : self.on_ws_modal_confirmed, 'on_reject' : self.on_modal_rejected })
        #http_get('http://micropython.org/ks/test.html')
        
    def on_item_selected(self, menu_item):
        print(menu_item.name)
    
    def on_send_selected(self, menu_item):
        print(menu_item.name)
        
    def on_enter(self):
        
        screen.fill(tft.BLACK)
        center("Wifi")
        
        self.menu.clear()
        
        sta = network.WLAN(network.STA_IF)
        ap = network.WLAN(network.AP_IF)
        self.menu.add(MenuItem("stop wifi" if sta.active() else "start wifi", cb=self.on_sta_selected))
        self.menu.add(MenuItem("stop ap" if ap.active() else "start ap", cb=self.on_ap_selected))
        
        if sta.active() or ap.active():
            self.menu.add(MenuItem("ifconfig", cb=self.on_ifconfig_selected))
            self.menu.add(MenuItem("stop websocket" if server.active() else "start websocket", cb=self.on_ws_selected))
        
        if server.connected():
            self.menu.add(MenuItem("send", cb=self.on_send_selected))
        
        self.menu.add(MenuItem("reload", cb=lambda x: s_manager.reload()))
        self.menu.add(MenuItem("exit", cb=lambda x: s_manager.pop()))
        
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
        screen.fill(tft.BLACK)
        center("ifconfig")
        
        sta = network.WLAN(network.STA_IF)
        ap = network.WLAN(network.AP_IF)
        
        Text(10, 48, "STA")
        Text(10, 81, sta.ifconfig()[0] if sta.isconnected() else "None")
        
        Text(10, 120, "AP")
        Text(10, 152, ap.ifconfig()[0] if ap.active() else "None")
    
    def on_update(self):
        pass
    
    def on_event(self, event_name, data):
        if event_name == "button_up":
            sm.pop()
    
    def on_exit(self):
        pass

def enter(err=None):
    print("start wifi")
    
    sm.add(MainPage("main"))
    sm.add(InfoPage("ifconfig"))
    sm.add(ModalConfirm())

def event(event_name, data):
    sm.send_event(event_name, data)
#     if event_name == "button_up":
#        s_manager.pop()

def update():
    #print("update settings")
    sm.update()

def leave():
    print("wifi exit ")


