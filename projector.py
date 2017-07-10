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
        self.board          = None

        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)   # Prepare the marker dictionary.

        # Set the marker size and margin.
        self.markersize = 48
        self.spacer = 48
        self.outermargin = 16
        self.rows = 0
        self.cols = 0
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

        markerid = 0
        markersize = 50
        marginsize = 5
        marker = cv2.cvtColor(aruco.drawMarker(self.aruco_dict, markerid, markersize, borderBits=1), cv2.COLOR_GRAY2BGR)
        self.calibrationimg[0+marginsize:markersize+marginsize, 0+marginsize:markersize+marginsize] = marker

        markerid = 1
        marker = cv2.cvtColor(aruco.drawMarker(self.aruco_dict, markerid, markersize, borderBits=1), cv2.COLOR_GRAY2BGR)
        self.calibrationimg[self.height-markersize-marginsize:self.height-marginsize, 0+marginsize:markersize+marginsize] = marker

        markerid = 2
        marker = cv2.cvtColor(aruco.drawMarker(self.aruco_dict, markerid, markersize, borderBits=1), cv2.COLOR_GRAY2BGR)
        self.calibrationimg[self.height-markersize-marginsize:self.height-marginsize, self.width-markersize-marginsize:self.width-marginsize] = marker

        markerid = 3
        marker = cv2.cvtColor(aruco.drawMarker(self.aruco_dict, markerid, markersize, borderBits=1), cv2.COLOR_GRAY2BGR)
        self.calibrationimg[0+marginsize:markersize+marginsize, self.width-markersize-marginsize:self.width-marginsize] = marker
        if self.flip:
            self.calibrationimg = cv2.flip(self.calibrationimg, 1) # Flip X axis

        return

    def outputCalibrationImage(self):
        self.outputimg = self.calibrationimg.copy()
        self.outputtype = "calibrate"
        return self.outputimg

