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

        # Initial marker positions.
        if markerid == 0:
            pos = (projector.height/2 - self.sizewithborder, projector.width/2 - self.sizewithborder)
        elif markerid == 1:
            pos = (projector.height/2 - self.sizewithborder, projector.width/2)
        elif markerid == 2:
            pos =(projector.height/2, projector.width/2)
        elif markerid == 3:
            pos = (projector.height/2, projector.width/2 - self.sizewithborder)

        self.pos = pos
        self.startpos = pos
        self.calpos = pos

        # Draw marker image with a white border
        arucodict = aruco.Dictionary_get(aruco.DICT_4X4_50)   # Prepare the marker dictionary.
        self.image = cv2.cvtColor(aruco.drawMarker(arucodict, markerid, self.size, borderBits=1), cv2.COLOR_GRAY2BGR)
        b = self.border
        self.image = cv2.copyMakeBorder(self.image, b, b, b, b, cv2.BORDER_CONSTANT, value=[255,255,255])

        self.lastmove = ""
        self.lastseen = 0
        self.maxtime = 3.0 # seconds
        return


    def resolve(self):
        detectedIds = self.projector.zone.detectedIds
        # Marker was found
        if detectedIds is not None and self.markerid in self.projector.zone.detectedIds:
            idx = list(detectedIds).index([self.markerid])
            self.lastseen = time.time()
            self.calpos = self.projector.zone.detectedCorners[idx][0][self.markerid]
            if self.markerid == 0:
                if self.lastmove == "left" or self.lastmove == "right":
                    self.moveMarker("up", 2)
                else:
                    self.moveMarker("left", 6)


        # Marker was not found for maxtime.
        elif time.time() - self.lastseen >= self.maxtime:
            if self.markerid == 0:
                if self.lastmove == "left" or self.lastmove == "right":
                    if self.pos[0] <= self.startpos[0]:
                        self.moveMarker("down", 1)
                else:
                    if self.pos[1] <= self.startpos[1]:
                        self.moveMarker("right", 1)

        return

    def moveMarker(self, direction, amount):
        y,x = self.pos
        if direction == "left":
            x -= amount
            if x < 0:
                x = 0
        elif direction == "right":
            x += amount
            if x > self.projector.width - self.sizewithborder:
                x = self.projector.width - self.sizewithborder
        elif direction == "up":
            y -= amount
            if y < 0:
                y = 0
        elif direction == "down":
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

