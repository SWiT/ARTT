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
        self.maxcalmarker   = None  # Maximum marker id used by the calibration image
        self.outputtype     = None  # Type of output (zone, calibration)

        self.outputCalibrationImage()
        #load base image
        return


    def outputZoneImage(self):
        # Don't regenerate the base zone image if we are already outputing it.
        if self.outputtype != "zone":
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

            self.outputtype = "zone"
        self.outputimg = self.baseimg.copy()
        return


    def outputCalibrationImage(self):
        # Don't regenerate the calibration image if we are already outputing it.
        if self.outputtype != "calibrate":
            # Create an empty white image.
            self.calibrationimg = zeros((self.height,self.width,3), uint8)
            self.calibrationimg[:,:] = (255,255,255)

            # Prepare the marker dictionary.
            aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
            # Set the marker size and margin.
            markersize = 48
            spacer = 48
            outermargin = 16

            # Calculate the initial marker position.
            yoffset = outermargin
            xoffset = outermargin

            markerid = 0
            for markerid in range(0,50):
                # Draw the marker and convert it to a color image.
                marker = cv2.cvtColor(aruco.drawMarker(aruco_dict, markerid, markersize), cv2.COLOR_GRAY2BGR)

                #calculate markers position
                if (xoffset + markersize) > (self.width - outermargin):
                    xoffset = outermargin
                    yoffset = yoffset + markersize + spacer

                if (yoffset + markersize) > (self.height - outermargin):
                    markerid -= 1
                    break

                self.calibrationimg[yoffset:(yoffset+markersize),xoffset:(xoffset+markersize)] = marker
                xoffset = xoffset + markersize + spacer

            self.maxcalmarker = markerid
            print "Calibration Markers: 0 - " + str(self.maxcalmarker)

            if self.flip:
                self.calibrationimg = cv2.flip(self.calibrationimg, 1) # Flip X axis

            self.outputtype = "calibrate"

        self.outputimg = self.calibrationimg.copy()
        return