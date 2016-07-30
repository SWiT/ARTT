import time
import utils

class Corner:
    def __init__(self, zone, idx):
        self.zone = zone
        width = self.zone.srcwidth
        height = self.zone.srcheight
        self.idx = idx
        self.location = (-1, -1)
        self.symbolcenter = (-1,-1)
        self.time = time.time()
        self.symboldimension = 10
        self.gap = 2
        self.symbol = None
        self.found = False
        
        if idx == 0:
            self.roixmin = 0;
            self.roixmax = width/2;
            self.roiymin = height/2;
            self.roiymax = height;
        elif idx == 1:
            self.roixmin = width/2;
            self.roixmax = width;
            self.roiymin = height/2;
            self.roiymax = height;
        elif idx == 2:
            self.roixmin = width/2;
            self.roixmax = width;
            self.roiymin = 0;
            self.roiymax = height/2;
        elif idx == 3:
            self.roixmin = 0;
            self.roixmax = width/2;
            self.roiymin = 0;
            self.roiymax = height/2;

        self.roi =  [(self.roixmin, self.roiymin), (self.roixmin, self.roiymax), (self.roixmax, self.roiymax), (self.roixmax, self.roiymin)]
        return
    
    def setData(self, symbol):
        # Update the symbol and location points.
        self.symbol = symbol
        self.symbolcenter = utils.findCenter(self.symbol)

        offset = int(self.gap * (self.symbol[1][0]-self.symbol[0][0]) / self.symboldimension)
        offset_x_sign = 1 if (self.idx%3 != 0) else -1
        offset_y_sign = 1 if (self.idx < 2) else -1
        
        self.location = self.symbol[self.idx]
        self.location = (self.location[0] + (offset_x_sign * offset), self.location[1] + (offset_y_sign * offset))
        self.time = time.time()
        self.found = True
        return

