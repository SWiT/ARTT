import time
import utils

class Corner:
    def __init__(self, zid, idx):
        self.zid = zid
        self.idx = idx
        self.location = (-1, -1)
        self.symbolvalue = idx
        self.symbolcenter = (-1,-1)
        self.scanDistance = 0
        self.time = time.time()
        self.symboldimension = 10
        self.gap = 1
        self.symbol = None
        self.found = False
        return
    
    def setData(self, symbol, found = True):
        self.symbol = symbol
        self.location = symbol[self.idx]
        self.symbolcenter = utils.findCenter(symbol)
        
        offset = int((symbol[1][0]-symbol[0][0]) * self.gap / self.symboldimension)
        offset_x_sign = 1 if (self.idx%3 != 0) else -1
        offset_y_sign = 1 if (self.idx < 2) else -1
        
        self.location = (self.location[0] + offset_x_sign * offset, self.location[1] + offset_y_sign * offset)
        self.time = time.time()
        self.found = found
        return

