import cv2
import cv2.aruco as aruco
import numpy as np
from utils import *

class Projector:

    def __init__(self, height, width):
        self.width = width
        self.height = height
        self.flip = False
        self.baseimg        = None  # Base map texture on top of which output is drawn.
        self.calibrationimg = None  # The calibration image for lens adjustments.
        self.outputimg      = None  # The image being output by the projector.
        self.maxcalmarkerid = None  # Maximum marker id used by the calibration image
        self.outputtype     = None  # Type of output (zone, calibration)
        self.calibrated     = False

        self.markersize = 100
        margin = 10
        self.markerpos = [(margin, margin)
                        ,(self.height-self.markersize-margin, margin)
                        ,(self.height-self.markersize-margin, self.width-self.markersize-margin)
                        ,(margin, self.width-self.markersize-margin)
                        ]

        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)   # Prepare the marker dictionary.

        self.calibrationpoints = []

        self.renderZoneImage()
        self.renderCalibrationImage()
        self.outputCalibrationImage()
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
        self.outputimg = self.baseimg.copy()
        self.outputtype = "zone"
        return self.outputimg

    def renderCalibrationImage(self):
        # Create a empty white image.
        self.calibrationimg = np.zeros((self.height,self.width,3), np.uint8)
        self.calibrationimg[:,:] = (255,255,255)

        for markerid in range(0,4):
            marker = cv2.cvtColor(aruco.drawMarker(self.aruco_dict, markerid, self.markersize, borderBits=1), cv2.COLOR_GRAY2BGR)
            self.calibrationimg[self.markerpos[markerid][0]:self.markerpos[markerid][0]+self.markersize, self.markerpos[markerid][1]:self.markerpos[markerid][1]+self.markersize] = marker

        # Crosshair in center outputImg
        s = 20
        pt0 = (self.width/2, self.height/2-s)
        pt1 = (self.width/2, self.height/2+s)
        cv2.line(self.calibrationimg, pt0, pt1, (0,0,0), 2)
        pt0 = (self.width/2-s, self.height/2)
        pt1 = (self.width/2+s, self.height/2)
        cv2.line(self.calibrationimg, pt0, pt1, (0,0,0), 2)

        if self.flip:
            self.calibrationimg = cv2.flip(self.calibrationimg, 1) # Flip X axis

        return

    def outputCalibrationImage(self):
        self.outputimg = self.calibrationimg.copy()
        self.outputtype = "calibrate"
        return self.outputimg

