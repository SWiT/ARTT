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
            markersize = 60
            margin = 6

            # Draw the marker and convert it to a color image.
            marker = cv2.cvtColor(aruco.drawMarker(aruco_dict, 0, markersize), cv2.COLOR_GRAY2BGR)
            yoffset = self.height - markersize - margin
            xoffset = margin
            self.baseimg[yoffset:(markersize+yoffset),xoffset:(markersize+xoffset)] = marker

            marker = cv2.cvtColor(aruco.drawMarker(aruco_dict, 1, markersize), cv2.COLOR_GRAY2BGR)
            yoffset = self.height - markersize - margin
            xoffset = self.width - markersize - margin
            self.baseimg[yoffset:(markersize+yoffset),xoffset:(markersize+xoffset)] = marker

            marker = cv2.cvtColor(aruco.drawMarker(aruco_dict, 2, markersize), cv2.COLOR_GRAY2BGR)
            yoffset = margin
            xoffset = self.width - markersize - margin
            self.baseimg[yoffset:(markersize+yoffset),xoffset:(markersize+xoffset)] = marker

            marker = cv2.cvtColor(aruco.drawMarker(aruco_dict, 3, markersize), cv2.COLOR_GRAY2BGR)
            yoffset = margin
            xoffset = margin
            self.baseimg[yoffset:(markersize+yoffset),xoffset:(markersize+xoffset)] = marker

            self.outputtype = "calibrate"

        self.baseimg = cv2.flip(self.baseimg, 1) # Flip X axis
        #self.baseimg = cv2.flip(self.baseimg, 0) # Flip Y axis
        self.outputimg = self.baseimg.copy()
        return