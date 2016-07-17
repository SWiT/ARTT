import time, math, re, os
from utils import *

idmin   = 0 
idmax   = 53

class Card:
    def __init__(self, idx):
        self.id = idx
        self.zid = 0
        self.scanDistance = 0
        self.locZonePx = (0,0)
        self.locZone = (0,0)
        self.locArena = (0,0)
        self.heading = 0
        self.symbol = None
        self.time = time.time() # time last found
        self.found = False

        self.color_lastknown    = (255, 200, 100)   # Light Blue
        self.color_detected     = (0,240,0)         # Green
        self.color_roi          = (255, 200, 100)   # Light blue
        return

    
    def setData(self, symbol, z, found = True):
        global Arena
        self.time = time.time()
        self.symbol = symbol
        self.zid = z.id

        self.found = found

        #update the card's location
        self.locZonePx = findCenter(self.symbol)
        wallCenterX = findCenter([z.corners[1].location, z.corners[0].location])
        wallCenterY = findCenter([z.corners[3].location, z.corners[0].location])
        maxX = z.corners[1].location[0] - z.corners[0].location[0]
        maxY = z.corners[3].location[1] - z.corners[0].location[1]
        if abs(maxX) > 0 and abs(maxY) > 0:
            zoneX = int(float(self.locZonePx[0]-wallCenterY[0])/float(maxX)*z.gridsize[0])
            zoneY = int(float(self.locZonePx[1]-wallCenterX[1])/float(maxY)*z.gridsize[1])
            self.locZone = (zoneX, zoneY)
            # Set Arena location, only side by side currently supported.
            self.locArena = (self.locZone[0] + (z.gridsize[0] * z.id), self.locZone[1])
            
        #update the cards's heading
        x = self.symbol[3][0] - self.symbol[0][0]
        y = self.symbol[0][1] - self.symbol[3][1]
        h = math.degrees(math.atan2(y,x))
        if h < 0: h = 360 + h
        self.heading = int(round(h,0))
        return
    

    def drawOutput(self, outputImg):
        drawBorder(outputImg, self.symbol, self.color_detected, 2)
                     
        x,y = self.locZonePx
        cv2.putText(outputImg, str(self.id), (x-8, y+8), cv2.FONT_HERSHEY_PLAIN, 1.5, self.color_detected, 2)
        
        return
        

    def drawLastKnownLoc(self, outputImg):
        global Arena
        x,y = self.locZonePx
        if x == 0 and y == 0:
            return
        
        color = self.color_lastknown

        # Draw the cards outline.        

        cv2.circle(outputImg, (x,y), 30, color, 2)
        cv2.putText(outputImg, str(self.id), (x-8, y+8), cv2.FONT_HERSHEY_PLAIN, 1.5, color, 2)
        ang = self.heading*(math.pi/180) #convert back to radians
        hl = 3.0    # Heading length
        pt0 = ((x+int(math.cos(ang)*30)), (y-int(math.sin(ang)*30)))
        pt1 = ((x+int(math.cos(ang)*30*hl)), (y-int(math.sin(ang)*30*hl)))
        cv2.line(outputImg, pt0, pt1, color, 2)
        return       
        
