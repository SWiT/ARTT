import cv2
import cv2.aruco as aruco
from numpy import *
from utils import *

class Projector:

    def __init__(self, height, width):
        self.width = width
        self.height = height
        self.flip = True
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
        self.baseimg = zeros((self.height,self.width,3), uint8)
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
        cols = 12
        rows = 8
        square = 100
        marker = 50
        self.board = cv2.aruco.CharucoBoard_create(cols,rows,square,marker, self.aruco_dict)
        self.calibrationimg = self.board.draw((self.width,self.height), marginSize=10)
        cv2.imwrite('calibration_charuco.png', self.calibrationimg)

        self.maxcalmarkerid = (cols*rows)/2 - 1
        print "Calibration Markers: 0 - " + str(self.maxcalmarkerid)

        if self.flip:
            self.calibrationimg = cv2.flip(self.calibrationimg, 1) # Flip X axis

        return

    def outputCalibrationImage(self):
        self.outputimg = self.calibrationimg.copy()
        self.outputtype = "calibrate"
        return self.outputimg

