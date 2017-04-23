import cv2
import cv2.aruco as aruco
from numpy import *
from utils import *

class Projector:

    def __init__(self, height, width):
        self.width = width
        self.height = height
        self.outputimg  = None
        self.baseimg    = None
        self.outputtype = None
        self.outputCalibrationImage()
        return


    def outputArenaImage(self):
        if self.outputtype != "arena":
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

            self.outputtype = "arena"
        self.outputimg = self.baseimg.copy()
        return


    def outputCalibrationImage(self):
        # Don't regenerate the calibrate image if already outputing it.
        if self.outputtype != "calibrate":
            # Create an empty white image.
            self.baseimg = zeros((self.height,self.width,3), uint8)
            self.baseimg[:,:] = (255,255,255)

            # Prepare the marker dictionary.
            aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
            # Set the marker size and margin.
            markersize = 48
            spacer = 48
            outermargin = 16

            markerid = 0

            # Calculate the initial marker position.
            yoffset = outermargin
            xoffset = outermargin

            for markerid in range(0,50):
                # Draw the marker and convert it to a color image.
                marker = cv2.cvtColor(aruco.drawMarker(aruco_dict, markerid, markersize), cv2.COLOR_GRAY2BGR)

                #calculate markers position
                if (xoffset + markersize) > (self.width - outermargin):
                    xoffset = outermargin
                    yoffset = yoffset + markersize + spacer

                if (yoffset + markersize) > (self.height - outermargin):
                    print "calibration marker: 0 - " + str(markerid-1)
                    break

                self.baseimg[yoffset:(yoffset+markersize),xoffset:(xoffset+markersize)] = marker

                xoffset = xoffset + markersize + spacer


            self.outputtype = "calibrate"

        #self.baseimg = cv2.flip(self.baseimg, 1) # Flip X axis
        #self.baseimg = cv2.flip(self.baseimg, 0) # Flip Y axis
        self.outputimg = self.baseimg.copy()
        return