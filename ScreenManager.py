import os
import sys
import gc

manager = None

def init():
    global manager
    
    if manager == None:
        manager = _screenManager()
    else:
        print("manager is alreaady initialized")
    



class _screen:
    
    _on_start = None
    _on_event = None
    _on_update = None
    _on_exit = None
    _name = None
    
    def __init__(self,name, on_start, on_event, on_update, on_exit):
        self._name = name
        self._on_start = on_start
        self._on_event = on_event
        self._on_update = on_update
        self._on_exit = on_exit
        

class _screenManager:
    
    _screens = None
    _busy = False
    _stack = None
    _stack_top = 0
    _stack_size = 25
    _last_page = ""
    _current_page = ""
    
    def __init__(self):
        self._screens = []
        self._stack = [None] * self._stack_size
        self._stack[0] = "main"
        self._current_page = "main"
        
        for s in os.listdir("apps"):
            s = s[:len(s)-3]
            self._screens.append(s)    
        
        
    def reload_apps(self):
        self._screens = os.listdir("apps")
        
        for s in self._screens:
            s = s[:len(s)-3]
    
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
        
        return True
    
    def update(self):
        
        if self._current_page != self._last_page:
            
            print("SCREEN MANAGER NEW SCREEN FROM TO " + self._last_page + " " + self._current_page)
            
            self._busy = True
            
            try:
                if self._last_page != "":
                    sys.modules["apps."+ self._last_page].leave()
                    del sys.modules["apps."+ self._last_page]
                    del sys.modules["apps"]
                    del sys.modules["watch"]
                print(sys.modules)
                
                exec('import apps.' + self._current_page, {} )
                sys.modules["apps."+ self._current_page].enter()
                
                print(gc.mem_free())
                gc.collect()
                
            except KeyError:
                pass
            
            
            self._last_page = self._current_page
            
        else:
            
            self._busy = False
            
            try:
            
                sys.modules["apps."+ self._current_page].update()
                    
            except KeyError:
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
        