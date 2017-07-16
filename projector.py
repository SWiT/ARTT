import cv2, time
import cv2.aruco as aruco
import numpy as np
from utils import *

class CalibrationMarker:
    def __init__(self, projector, markerid):
        self.projector = projector
        self.markerid = markerid

        self.size = 100
        self.border = self.size/6
        self.sizewithborder = self.size + self.border * 2

        self.pos = [0,0]
        self.resetpos()
        self.startpos = self.pos

        self.calpos = [0,0]

        # Draw marker image with a white border
        arucodict = aruco.Dictionary_get(aruco.DICT_4X4_50)   # Prepare the marker dictionary.
        self.image = cv2.cvtColor(aruco.drawMarker(arucodict, markerid, self.size, borderBits=1), cv2.COLOR_GRAY2BGR)
        b = self.border
        self.image = cv2.copyMakeBorder(self.image, b, b, b, b, cv2.BORDER_CONSTANT, value=[255,255,255])

        self.foundX = False
        self.foundY = False
        self.lastmove = ""
        self.lastseen = 0
        self.maxtime = 3.0 # seconds
        return

    def resetpos(self):
        # Initial marker positions.
        if self.markerid == 0:
            self.pos = (self.projector.height/2 - self.sizewithborder, self.projector.width/2 - self.sizewithborder)
        elif self.markerid == 1:
            self.pos = (self.projector.height/2 - self.sizewithborder, self.projector.width/2)
        elif self.markerid == 2:
            self.pos =(self.projector.height/2, self.projector.width/2)
        elif self.markerid == 3:
            self.pos = (self.projector.height/2, self.projector.width/2 - self.sizewithborder)
        self.foundX = False
        self.foundY = False
        return

    def resolve(self):
        detectedIds = self.projector.zone.detectedIds

        # Marker was found
        if detectedIds is not None and self.markerid in self.projector.zone.detectedIds:
            self.lastseen = time.time()
            idx = list(detectedIds).index([self.markerid])
            self.calpos = self.projector.zone.detectedCorners[idx][0][self.markerid]
            if self.markerid == 0:
                if self.lastmove == "left":
                    self.moveMarker("up", 2)
                elif self.lastmove == "right":
                    self.foundX = True
                    self.lastmove = "left"
                elif self.lastmove == "down":
                    self.foundY = True
                    self.lastmove = "up"
                else:
                    self.moveMarker("left", 3)

            elif self.markerid == 1:
                if self.lastmove == "right":
                    self.moveMarker("up", 2)
                elif self.lastmove == "left":
                    self.foundX = True
                    self.lastmove = "right"
                elif self.lastmove == "down":
                    self.foundY = True
                    self.lastmove = "up"
                else:
                    self.moveMarker("right", 3)

            elif self.markerid == 2:
                if self.lastmove == "right":
                    self.moveMarker("down", 2)
                elif self.lastmove == "left":
                    self.foundX = True
                    self.lastmove = "right"
                elif self.lastmove == "up":
                    self.foundY = True
                    self.lastmove = "down"
                else:
                    self.moveMarker("right", 3)

            elif self.markerid == 3:
                if self.lastmove == "left":
                    self.moveMarker("down", 2)
                elif self.lastmove == "right":
                    self.foundX = True
                    self.lastmove = "left"
                elif self.lastmove == "up":
                    self.foundY = True
                    self.lastmove = "down"
                else:
                    self.moveMarker("left", 3)

        # Marker was not found for maxtime.
        elif self.lastseen > 0 and time.time() - self.lastseen >= self.maxtime:
            if self.markerid == 0:
                if self.lastmove == "left" or self.lastmove == "right":
                    if self.pos[0] <= self.startpos[0]:
                        self.moveMarker("down", 1)
                else:
                    if self.pos[1] <= self.startpos[1]:
                        self.moveMarker("right", 1)

            elif self.markerid == 1:
                if self.lastmove == "left" or self.lastmove == "right":
                    if self.pos[0] <= self.startpos[0]:
                        self.moveMarker("left", 1)
                else:
                    if self.pos[1] >= self.startpos[1]:
                        self.moveMarker("down", 1)

            elif self.markerid == 2:
                if self.lastmove == "left" or self.lastmove == "right":
                    if self.pos[0] >= self.startpos[0]:
                        self.moveMarker("left", 1)
                else:
                    if self.pos[1] >= self.startpos[1]:
                        self.moveMarker("up", 1)

            elif self.markerid == 3:
                if self.lastmove == "left" or self.lastmove == "right":
                    if self.pos[0] >= self.startpos[0]:
                        self.moveMarker("right", 1)
                else:
                    if self.pos[1] <= self.startpos[1]:
                        self.moveMarker("up", 1)

        return

    def moveMarker(self, direction, amount):
        y,x = self.pos
        if direction == "left" and not self.foundX:
            x -= amount
            if x < 0:
                x = 0
        elif direction == "right" and not self.foundX:
            x += amount
            if x > self.projector.width - self.sizewithborder:
                x = self.projector.width - self.sizewithborder
        elif direction == "up" and not self.foundY:
            y -= amount
            if y < 0:
                y = 0
        elif direction == "down" and not self.foundY:
            y += amount
            if y > self.projector.height - self.sizewithborder:
                y = self.projector.height - self.sizewithborder
        self.pos = (y, x)
        self.lastmove = direction
        return


class Projector:

    def __init__(self, zone):
        self.zone = zone
        self.width = 800
        self.height = 600
        self.flip = True
        self.baseimg        = None  # Base map texture on top of which output is drawn.
        self.calibrationimg = None  # The calibration image for lens adjustments.
        self.image          = None  # The image being output by the projector.
        self.maxcalmarkerid = None  # Maximum marker id used by the calibration image
        self.outputtype     = None  # Type of output (zone, calibration)
        self.calibrated     = False

        self.calmarker = [CalibrationMarker(self, 0)
                        , CalibrationMarker(self, 1)
                        , CalibrationMarker(self, 2)
                        , CalibrationMarker(self, 3)
                        ]



        self.renderZoneImage()
        self.renderCalibrationImage()
        self.outputCalibrationImage()
        return

    def resolve(self):
        if not self.calibrated:
            for cm in self.calmarker:
                cm.resolve()
        return

    def renderZoneImage(self):
        # TODO: Option to load a base map image

        # Create a empty white image.
        self.baseimg = np.zeros((self.height,self.width,3), np.uint8)
        self.baseimg[:,:] = (255,255,255)

        # Draw the arena border
        offset = 2
        border = [(offset, self.height-offset)
                 ,(self.width-offset, self.height-offset)
                 ,(self.width-offset, offset)
                 ,(offset, offset)
                 ]
        drawBorder(self.baseimg, border, (0,240,0), 3)
        #cv2.line(self.baseimg, pt0, pt1, color, thickness)
        return

    def outputZoneImage(self):
        self.image = self.baseimg.copy()
        self.outputtype = "zone"
        return self.image

    def renderCalibrationImage(self):
        # Create a empty image.
        self.calibrationimg = np.zeros((self.height,self.width,3), np.uint8)
        self.calibrationimg[:,:] = (127,127,127) #TODO: Make this adjustable via the control panel

        for markerid in range(0,4):
            y0 = self.calmarker[markerid].pos[0]
            y1 = self.calmarker[markerid].pos[0] + self.calmarker[markerid].sizewithborder
            x0 = self.calmarker[markerid].pos[1]
            x1 = self.calmarker[markerid].pos[1] + self.calmarker[markerid].sizewithborder
            self.calibrationimg[y0:y1, x0:x1] = self.calmarker[markerid].image

        # Crosshair in center output image
        pt0 = (0, self.height/2)
        pt1 = (self.width, self.height/2)
        cv2.line(self.calibrationimg, pt0, pt1, (0,0,0), 2)
        pt0 = (self.width/2, 0)
        pt1 = (self.width/2, self.height)
        cv2.line(self.calibrationimg, pt0, pt1, (0,0,0), 2)

        if self.flip:
            self.calibrationimg = cv2.flip(self.calibrationimg, 1) # Flip X axis

        return

    def outputCalibrationImage(self):
        self.renderCalibrationImage()
        self.image = self.calibrationimg.copy()
        self.outputtype = "calibrate"
        return self.image

