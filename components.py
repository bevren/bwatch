import tft

screen = tft.TFT()
import vga1_bold_16x32 as default_font


class Menu:
    def __init__(self, x, y, visible_items=6, width=240, height=240):
        self._x = x
        self._y = y
        self._items = []
        self._count = 0
        self._current_selected_idx = 0
        self._last_selected_idx = 0
        self._height = height
        self._width = width
        self._shift = 0
        self._visible_items = visible_items
    
    
    def reset(self):
        self._current_selected_idx = 0
        self._last_selected_idx = 0
        self._shift = 0
        
        for item in self._items:
            item.deselect()
    
    def add(self, item):
        self._items.append(item)
        item._idx = self._count
        item._x = self._x
        item._y = self._y
        
        self._count += 1
    
    def remove(self, item):
        self._items.remove(item)
        self._count -= 1
        
        if self._current_selected_idx >= self._count - 1:
            self._current_selected_idx = self._count - 1
        
        #self.update()
    
    
    def clear(self):
        self._items.clear()
        self._count = 0
        
    
    
    def update(self, shift = 0):
        #screen.fill_rect(self._xoff, self._yoff, screen.width() - self._xoff, screen.height() - self._yoff, tft.BLACK)
        for idx,item in enumerate(self._items[shift:shift+self._visible_items]):
            if idx + shift == self._current_selected_idx:
                if item._selected == False:
                    item.select()
            else:
                item.deselect()
                
            item._idx = idx
            item.update()
            
    def move_down(self):
        
        if self._current_selected_idx >= self._count - 1:
            print("menu limit down")
            self._current_selected_idx = self._count - 1
            return
        
        self._current_selected_idx += 1
        print(self._current_selected_idx, self._count - 1)
        
        
        if self._current_selected_idx > self._shift + self._visible_items - 1:
            if self._shift + self._visible_items < self._count:
                
                self._shift += 1
                
                
        
        self.update(self._shift)
        self._last_selected_idx = self._current_selected_idx
        
        
    def move_up(self):
        
        if self._current_selected_idx <= 0:
            print("menu limit up")
            self._current_selected_idx = 0
            return
        
        self._current_selected_idx -= 1
        
        
        
        if self._current_selected_idx < self._shift:
            if self._shift > 0:
                self._shift -= 1
        
        
        self.update(self._shift)
        self._last_selected_idx = self._current_selected_idx
       
       
    def get(self, name):
        for item in self._items:
            if item.name == name:
                return item
            
        return None
        
    def current(self):
        return self._items[self._current_selected_idx]._text
    
    def select(self):
        if len(self._items) > 0:
            current = self._items[self._current_selected_idx]
            if current:
                if current._cb != None:
                    current._cb(current)

class MenuItem:
    def __init__(self, text, x = 0, y = 0, font=default_font, cb=None):
        self._x = x
        self._y = y
        self.name = text
        self._text = text
        self._font = font
        self._idx = 0
        self._height = self._font.HEIGHT
        self._width = len(text) * self._font.WIDTH
        self._selected = False
        self._cb = cb
    
    def update(self, txt="", selector=">", bg=tft.BLACK, fg=tft.WHITE):
        #screen.fill_rect(0, self._y + (self._height*self._idx), screen.width(), self._height, tft.BLACK)
        if txt != "":
            self._text = txt
        
        text = ""
        space = int((screen.width() - (self._x + self._width)) / self._font.WIDTH)
        
        if space < 0:
            space = 0
        
        if self._selected:
            if space > 1:
                space -= 1
            text = "{}{}{}".format(selector, self._text, " " * space)
            
        else:
            text = "{}{}".format(self._text, " " * space)
        
        #test_width = len(text) * self._font.WIDTH
        test_y = self._y + (self._height*self._idx)
        #screen.fill_rect(self._x, test_y, test_width, self._height, tft.WHITE)
        screen.text(self._font, text, self._x, test_y, fg, tft.RED if self._selected else bg)
    
    def set_text(self, text):
        self._text = text
    
    def select(self):
        self._selected = True
    
    def deselect(self):
        self._selected = False



class Text:
    def __init__(self, x, y, text, font=default_font):
        self._x = x
        self._y = y
        self._text = text
        self._font = font
        self._width = len(text) * self._font.WIDTH
        self._height = self._font.HEIGHT
        
        self.update()
        
    def update(self,text="", fg=tft.WHITE, bg=tft.BLACK):
        
        if text != "":
            screen.text(self._font, text, self._x, self._y, fg, bg)
        else:
            screen.text(self._font, self._text, self._x, self._y, fg, bg)
        
    def bottom(self):
        return self._y + self._height
    
    def top(self):
        return self._y
    
    def height(self):
        return self._height
    
    def width(self):
        return self._width
        
        
class ScrollText:
    def __init__(self, x, y, text, font=default_font):
        self._x = x
        self._y = y
        self._text = text
        self._font = font
        self._total_width = len(text) * self._font.WIDTH
        self._total_pages = 0
        print("*******************")
        
        self._total_row = int((screen.width() - self._x) / self._font.WIDTH)
        self._total_column = int((screen.height() - self._y) / self._font.HEIGHT)
        
        self._total_pages = int(len(text) / (self._total_row * self._total_column))
        
        print(self._total_pages)
        
        
        self._current_page = 0
        
        self._column = 0
        self._row = 0
        
        
        self.update()
        
    def update(self, fg=tft.WHITE, bg=tft.BLACK):
        
        self._column = 0
        self._row = 0
        
        screen.fill_rect(self._x, self._y, screen.width() - self._x, screen.height() - self._y, tft.BLACK)
        
        text_ref = self._text
        total = (self._total_row * self._total_column)
        idx = self._current_page * total
        print(text_ref[idx: idx + total])
        for c in text_ref[idx: idx + total]:
            
            if self._column + self._font.WIDTH > screen.width() - self._x:
                self._row += self._font.HEIGHT
                self._column = 0
            
            screen.text(self._font,c,self._x + (self._column), self._y + (self._row),fg, bg)
            self._column += self._font.WIDTH
        
        #screen.text(self._font, text_ref[idx: idx + self._total_column], self._x, self._y, fg, bg)
        
        
    def up(self):
        if self._current_page > 0:
            self._current_page -= 1
            self.update()
    
    def down(self):
        if self._current_page < self._total_pages:
            self._current_page += 1
            self.update()
        