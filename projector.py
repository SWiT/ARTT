import cv2
import cv2.aruco as aruco
import numpy as np
from utils import *

class Projector:

    def __init__(self, height, width):
        self.width = width
        self.height = height
        self.flip = True
        self.baseimg        = None  # Base map texture on top of which output is drawn.
        self.calibrationimg = None  # The calibration image for lens adjustments.
        self.image          = None  # The image being output by the projector.
        self.maxcalmarkerid = None  # Maximum marker id used by the calibration image
        self.outputtype     = None  # Type of output (zone, calibration)
        self.calibrated     = False

        self.markersize = 100
        margin = 0
        self.markerborder = self.markersize/6
        self.markertotalsize = self.markersize + self.markerborder * 2
        self.markerpos = [(self.height/2 - self.markertotalsize, self.width/2 - self.markertotalsize)
                        ,(self.height/2, self.width/2 - self.markertotalsize)
                        ,(self.height/2, self.width/2)
                        ,(self.height/2 - self.markertotalsize, self.width/2)
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
        self.image = self.baseimg.copy()
        self.outputtype = "zone"
        return self.image

    def renderCalibrationImage(self):
        # Create a empty image.
        self.calibrationimg = np.zeros((self.height,self.width,3), np.uint8)
        self.calibrationimg[:,:] = (127,127,127) #TODO: Make this adjustable via the control panel

        for markerid in range(0,4):
            marker = cv2.cvtColor(aruco.drawMarker(self.aruco_dict, markerid, self.markersize, borderBits=1), cv2.COLOR_GRAY2BGR)
            b = self.markerborder
            marker = cv2.copyMakeBorder(marker, b, b, b, b, cv2.BORDER_CONSTANT, value=[255,255,255])
            y0 = self.markerpos[markerid][0]
            y1 = self.markerpos[markerid][0] + self.markertotalsize
            x0 = self.markerpos[markerid][1]
            x1 = self.markerpos[markerid][1] + self.markertotalsize
            self.calibrationimg[y0:y1, x0:x1] = marker

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

