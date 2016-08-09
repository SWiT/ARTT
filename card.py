import time, math, re, os
from utils import *

idmin   = 0
idmax   = 53

class Card:
    def __init__(self, idx):
        self.id = idx
        self.zid = 0
        self.roiminy = 0
        self.roiminx = 0
        self.roi =  [(0,0),(0,0),(0,0),(0,0)]
        self.scanDistance = 0
        self.locZonePx = (0,0)
        self.locZone = (0,0)
        self.locArena = (0,0)
        self.heading = 0
        self.radians = 0
        self.symbol = None
        self.symbolDimension = 2.0
        self.gap = 0.35
        self.symbolDimensionPx = 0
        self.time = time.time() # time last found
        self.found = False

        self.dimensions = (2.5, 3.5)

        self.color_lastknown    = (0, 0, 255)       # Red
        self.color_detected     = (0,240,0)         # Green
        self.color_roi          = (255, 200, 100)   # Light blue
        self.color_augtext      = (255, 0, 0)       # Blue
        return

    def updateRoi(self):
        self.scanDistance = 200
        miny = self.locZonePx[0] - self.scanDistance
        minx = self.locZonePx[1] - self.scanDistance
        maxy = self.locZonePx[0] + self.scanDistance
        maxx = self.locZonePx[1] + self.scanDistance
        self.roiminy = miny
        self.roiminx = minx
        self.roi =  [(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)]

    def setData(self, symbol, z):
        global Arena
        self.time = time.time()
        self.symbol = symbol
        self.zid = z.id

        self.found = True

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

        # Update the region of interest.
        updateRoi()

        # Update the cards's heading
        x = self.symbol[3][0] - self.symbol[0][0]
        y = self.symbol[0][1] - self.symbol[3][1]
        self.radians = math.atan2(y,x)
        h = math.degrees(self.radians)
        if h < 0: h = 360 + h
        self.heading = int(round(h,0))

        self.symbolDimensionPx = dist(self.symbol[0], self.symbol[3])
        return


    def drawAugText(self, outputImg):
        x,y = self.locZonePx
        cv2.putText(outputImg, str(self.id), (x-8, y+100), cv2.FONT_HERSHEY_PLAIN, 1.5, self.color_augtext, 2)

        return

    def drawDetected(self, outputImg):
        drawBorder(outputImg, self.symbol, self.color_detected, 1)

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
        op = (float(self.gap) * self.symbolDimensionPx / float(self.symbolDimension) ) + (self.symbolDimensionPx/2)
        adj = op + (0.8 * self.symbolDimensionPx / float(self.symbolDimension))
        d = math.sqrt(op**2 + adj**2)

        ang = self.radians + (math.pi - math.atan2(op,adj))
        pt0 = ( (x+int(math.cos(ang)*d)), (y-int(math.sin(ang)*d)) )

        ang = self.radians - (math.pi - math.atan2(op,adj))
        pt1 = ( (x+int(math.cos(ang)*d)), (y-int(math.sin(ang)*d)) )

        op = (float(self.gap) * self.symbolDimensionPx / float(self.symbolDimension) ) + (self.symbolDimensionPx/2)
        adj = op
        d = math.sqrt(op**2 + adj**2)

        ang = self.radians - (math.pi/4) + 0.05
        pt2 = ( (x+int(math.cos(ang)*d)), (y-int(math.sin(ang)*d)) )

        ang = self.radians + (math.pi/4) - 0.05
        pt3 = ( (x+int(math.cos(ang)*d)), (y-int(math.sin(ang)*d)) )

        drawBorder(outputImg, [pt0, pt1, pt2, pt3], color, 1)

        return

