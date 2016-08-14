import time, math, re, os
from utils import *

idmin   = 0
idmax   = 53

class Card:
    def __init__(self, idx):
        self.id = idx
        self.z = None   # The zone the card is in.
        self.roiminy = 0
        self.roiminx = 0
        self.roimaxy = 0
        self.roimaxx = 0
        self.roi =  [(0,0),(0,0),(0,0),(0,0)]
        self.scanDistance = 150
        self.location = (0,0)   # The location of the object in the image in pixels.
        self.locZone = (0,0)    # The location of the object in the Zone's grid.
        self.locArena = (0,0)   # The location of the object in the Arena.
        self.heading = 0
        self.radians = 0
        self.symbol = None
        self.symbolDimensionPx = 0
        self.symbolDimension = 2.0 # Real life size
        self.gap = 0.35
        self.timeseen = 0 # time last found
        self.timescan = 0 # time last scanned for
        self.scandelay = 33 # ms to wait between scans.
        self.found = False

        self.dimensions = (2.5, 3.5)

        self.color_lastknown    = (0, 0, 255)       # Red
        self.color_detected     = (0,240,0)         # Green
        self.color_roi          = (255, 200, 100)   # Light blue
        self.color_augtext      = (255, 0, 0)       # Blue
        return

    def updateRoi(self):
        miny = max(self.location[1] - self.scanDistance, 0)
        minx = max(self.location[0] - self.scanDistance, 0)
        maxy = min(self.location[1] + self.scanDistance, self.z.height)
        maxx = min(self.location[0] + self.scanDistance, self.z.width)
        self.roiminy = miny
        self.roiminx = minx
        self.roimaxy = maxy
        self.roimaxx = maxx
        self.roi =  [(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)]

    def setData(self, symbol, z, timestamp):
        global Arena
        self.timeseen = timestamp
        self.symbol = symbol
        self.z = z

        self.found = True

        #update the card's location
        self.location = findCenter(self.symbol)

        zoneX = int((self.location[0] / z.width) * z.gridsize[0])
        zoneY = int((self.location[1] / z.height) * z.gridsize[1])
        self.locZone = (zoneX, zoneY)

        # Set Arena location, only side by side currently supported.
        # TODO: more elaborate arena/zone patterns.
        self.locArena = (self.locZone[0] + (z.gridsize[0] * z.id), self.locZone[1])

        # Update the region of interest.
        self.updateRoi()

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
        x,y = self.location
        cv2.putText(outputImg, str(self.id), (x-8, y+100), cv2.FONT_HERSHEY_PLAIN, 1.5, self.color_augtext, 2)
        return

    def drawRoi(self, outputImg):
        # Draw the scanning area (region of interest)
        drawBorder(outputImg, self.roi, self.color_roi, 2)
        return


    def draw(self, outputImg):
        global Arena
        x,y = self.location
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

