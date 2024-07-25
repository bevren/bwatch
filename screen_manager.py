import os
import io
import sys
import gc
import tft
_screen_manager = None
import vga1_bold_16x32 as default_font

import socket_manager
import struct
def init():
    global _screen_manager
    
    if _screen_manager == None:
        _screen_manager = _screenManager()
    else:
        print("manager is alreaady initialized")
    

def ScreenManager():
    global _screen_manager
    return _screen_manager


class _screenManager:
    
    def __init__(self):
        self._screens = []
        self._stack_size = 25
        self._stack_top = 0
        self._stack = [None] * self._stack_size
        self._stack[0] = "main"
        self._last_page = ""
        self._current_page = "main"
        self._busy = False
        self._popped = False
        self._reloaded = False
        
        for s in os.listdir("apps"):
            s = s[:len(s)-3]
            self._screens.append(s)    
        
    
    def reload(self):
        
        self._busy = True
        
        screen = tft.TFT()
        screen.fill(tft.BLACK)
        
        screen.text(default_font, "Reloading...", 10, 20)
        last_app = self._stack[self._stack_top]
        
        if self._current_page != last_app:
            self._current_page = last_app
        else:
            sys.modules["apps."+ last_app].leave()
            self._last_page = ""
        
        del sys.modules["apps."+ last_app]
        
        self._reloaded = True
        
        
        
    def get_apps(self):
        self.reload_apps()
        return self._screens
    
    def reload_apps(self):
        self._screens.clear()
        
        for s in os.listdir("apps"):
            s = s[:len(s)-3]
            self._screens.append(s)    
    
    def get(self,name):
        
        if name == "":
            return ""
        
        for screen in self._screens:
            if screen == name:
                return screen
            
        return ""
    
    def push(self, name):
        
        screen = self.get(name)
        
        if screen == "":
            return False
        
        if self._busy:
            return False
        
        if self._stack[self._stack_top] == screen:
            return False
        
        if self._stack_top >= self._stack_size:
            self._stack_top = self._stack_size
            return False
        
        self._stack_top+=1
        
        self._stack[self._stack_top] = screen
        
        self.change_to(screen)
        
        
        return True
    
    def pop(self):
        
        if self._busy:
            return False
        
        if self._stack_top == 0:
            return False
        
        
        self._stack[self._stack_top] = ""
        
        self._stack_top -= 1
        
        self.change_to(self._stack[self._stack_top])
        
        self._popped = True
        
        return True
    
    def update(self):
        
        if self._current_page != self._last_page:
            
            print("SCREEN MANAGER NEW SCREEN FROM TO " + self._last_page + " " + self._current_page)
            
            self._busy = True
            
            if self._last_page != "":
                sys.modules["apps."+ self._last_page].leave()   
                del sys.modules["apps."+ self._last_page]
                
                    
            #print(sys.modules)
            error = None
            try:
                exec('import apps.' + self._current_page)
                
            except Exception as err:
                print("yooooooooooooooooooooooooo")
                #self._stack[self._stack_top] = ""
                #self._stack_top -= 1
                del sys.modules["apps."+ self._current_page]
                buf = io.StringIO()
                sys.print_exception(err, buf)
                print(buf.getvalue())
                error = buf.getvalue()
                
                test = (struct.pack("<BBI", 0x25,0x1,len(error)) + error)
                
                socket_manager.Server().send(test)
                
                exec('import apps.error')
                
                self._current_page = "error"
            finally:
                print(self._current_page)
                try:
                    if error:
                        sys.modules["apps."+ self._current_page].enter(error)
                    else:
                        sys.modules["apps."+ self._current_page].enter()
                        
                    if self._reloaded:
                        test = (struct.pack("<BBI", 0x30,0x1,0))
                        socket_manager.Server().send(test)
                        self._reloaded = False
                        
                except Exception as err:
                    pass
                
                #print(sys.modules)
                print(gc.mem_free())
                gc.collect()
            
            
            
            self._popped = False
            self._last_page = self._current_page
            
        else:
            
            self._busy = False
            
            try:
                sys.modules["apps."+ self._current_page].update()
                    
            except Exception as err:
                pass
            
        
        
    
    def send_event(self, event_name, data):
        try:
            sys.modules["apps."+ self._current_page].event(event_name, data)
        except KeyError:
            pass
            
    
    def change_to(self, screen_name):
        
        
        if screen_name == "":
            print("ScreenManager::change_to failed cannot get screen name : " + screen)
            return False
        
        screen = self.get(screen_name)
        if screen == "":
            print("ScreenManager::change_to failed cannot get screen name : " + screen)
            return False
        
        if self._busy:
            print("ScreenManager::change_to failed manager is busy : " + screen)
            return False
        
        self._current_page = screen
        
        self._busy = True
        
        return True
        
