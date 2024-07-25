import gc

class State:
    
    def __init__(self, name):
        self._name = name
        self.locals = {}
    
    def on_enter(self):
        pass
    
    def on_update(self):
        pass
    
    def on_event(event_name, data):
        pass
    
    def on_exit(self):
        pass
    
    
class StateMachine:
    
    def __init__(self):
        self._states = []
        self._last_state = "nothing"
        self._current_state = ""
        self._current_state_obj = None
        self._busy = False
        self._stack_size = 25
        self._stack_top = 0
        self._stack = [None] * self._stack_size
        
    
    
    def change_to(self, page_name):
        if page_name == "":
            print("PAGEManager::change_to failed cannot get page name : " + page_name)
            return False
        
        page = self.get(page_name)
        if page == None:
            print("PAGEManager::change_to failed cannot get screen name : " + page_name)
            return False
        
        if self._busy:
            print("PAGEManager::change_to failed manager is busy : " + page_name)
            return False
        
        self._current_state = page_name
        
        self._busy = True
        
        return True
        
    def pop(self):
        
        if self._busy:
            return False
        
        if self._stack_top == 0:
            return False
        
        
        page = self.get(self._current_state)
        #print(page.locals.items())
        
        for k, v in page.locals.items():
            del page.locals[k]
        
        
        #print(page.locals.items())
        self._stack[self._stack_top] = ""
        
        self._stack_top -= 1
        
        self.change_to(self._stack[self._stack_top])
        
        return True
        
    def push(self, name, data=None):
        
        page_name = name
        page = self.get(page_name)
        
        if page == None:
            return False
        
        if self._busy:
            return False
        
        if self._stack[self._stack_top] == page_name:
            return False
        
        if self._stack_top >= self._stack_size:
            self._stack_top = self._stack_size
            return False
        
        if data is not None:
            if isinstance(data, dict):
                for k, v in data.items():
                    page.locals[k] = v
            else:
                print("PUSH::data is not dictionary")
        
        self._stack_top+=1
        
        self._stack[self._stack_top] = page_name
        
        self.change_to(page_name)
        
        return True
        
    def update(self):
        
        if self._current_state != self._last_state:
            
            self._busy = True
            
            last_state = self.get(self._last_state)
            
            if last_state != None:
                if last_state.on_exit:
                    last_state.on_exit()
            
            gc.collect()
            current_state = self.get(self._current_state)
            
            if current_state != None:
                self._current_state_obj = current_state
                if current_state.on_enter:
                    current_state.on_enter()
            
            self._last_state = self._current_state
            
            
        else:
            self._busy = False
            if self._current_state_obj != None:
                if self._current_state_obj.on_update:
                    self._current_state_obj.on_update()
                
    def send_event(self, event_name, data):
        if self._current_state_obj != None:
             if self._current_state_obj.on_event:
                    self._current_state_obj.on_event(event_name, data)
                    
    def get(self, name):
        
        for state in self._states:
            if state._name == name:
                return state
            
        return None
    
    def add(self, _state):
        for state in self._states:
            if state == _state:
                print("state already exists")
                return
            
        if len(self._states) == 0:
            self._current_state = _state._name
            self._stack[0] = _state._name
            
        self._states.append(_state)
                
    def remove(self, _state):
        for state in self._states:
            if state == _state:
                self._states.remove(_state)
            else:
                print("dont exists")
        