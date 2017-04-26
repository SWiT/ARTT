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

        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)   # Prepare the marker dictionary.
        # Set the marker size and margin.
        self.markersize = 48
        self.spacer = 48
        self.outermargin = 16
        self.calibrationpoints = None

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
        # Create an empty white image.
        self.calibrationimg = zeros((self.height,self.width,3), uint8)
        self.calibrationimg[:,:] = (255,255,255)


        # Calculate the initial marker position.
        yoffset = self.outermargin
        xoffset = self.outermargin

        markerid = 0
        for markerid in range(0,50):
            # Draw the marker and convert it to a color image.
            marker = cv2.cvtColor(aruco.drawMarker(self.aruco_dict, markerid, self.markersize), cv2.COLOR_GRAY2BGR)

            #calculate markers position
            if (xoffset + self.markersize) > (self.width - self.outermargin):
                xoffset = self.outermargin
                yoffset = yoffset + self.markersize + self.spacer

            if (yoffset + self.markersize) > (self.height - self.outermargin):
                markerid -= 1
                break

            self.calibrationimg[yoffset:(yoffset+self.markersize),xoffset:(xoffset+self.markersize)] = marker
            xoffset = xoffset + self.markersize + self.spacer

        self.maxcalmarkerid = markerid
        print "Calibration Markers: 0 - " + str(self.maxcalmarkerid)

        if self.flip:
            self.calibrationimg = cv2.flip(self.calibrationimg, 1) # Flip X axis

        return

    def outputCalibrationImage(self):
        self.outputimg = self.calibrationimg.copy()
        self.outputtype = "calibrate"
        return self.outputimg

