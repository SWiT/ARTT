import cv2
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
            pos = (projector.height/2, projector.width/2 - self.sizewithborder)
        elif markerid == 2:
            pos =(projector.height/2, projector.width/2)
        elif markerid == 3:
            pos = (projector.height/2 - self.sizewithborder, projector.width/2)
        self.pos = pos

        # Draw marker image with a white border
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)   # Prepare the marker dictionary.
        self.image = cv2.cvtColor(aruco.drawMarker(aruco_dict, markerid, self.size, borderBits=1), cv2.COLOR_GRAY2BGR)
        b = self.border
        self.image = cv2.copyMakeBorder(self.image, b, b, b, b, cv2.BORDER_CONSTANT, value=[255,255,255])

        self.lastmove = ""
        self.lastseen = 0
        self.maxtime = 1000 #ms?
        return


    def resolve(self):
        print self.markerid
        return

    def moveMarker(self, markerid, direction, amount):
        y,x = self.projector.markerpos[markerid]
        if direction == "left":
            x -= amount
            if x < 0:
                x = 0
        elif direction == "right":
            x += amount
            if x > self.projector.width - self.projector.markertotalsize:
                x = self.projector.width - self.projector.markertotalsize
        elif direction == "up":
            y -= amount
            if y < 0:
                y = 0
        elif direction == "down":
            y += amount
            if y > self.projector.height - self.projector.markertotalsize:
                y = self.projector.height - self.projector.markertotalsize
        self.projector.markerpos[markerid] = (y, x)
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

