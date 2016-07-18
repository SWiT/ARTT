import cv2
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
        #TODO: generate Corner symbols on the fly based on a size value.
        if self.outputtype != "calibrate":
            # Base arena file not found.
            # Create a empty white image.
            self.baseimg = zeros((self.height,self.width,3), uint8)
            self.baseimg[:,:] = (255,255,255)

            # Import the corner images
            corner = cv2.imread("images/C0.png")
            ch = corner.shape[0]
            cw = corner.shape[1]
            yoffset = self.height - ch
            xoffset = 0
            self.baseimg[yoffset:(ch+yoffset),xoffset:(cw+xoffset)] = corner

            corner = cv2.imread("images/C1.png")
            yoffset = self.height - ch
            xoffset = self.width - cw
            self.baseimg[yoffset:(ch+yoffset),xoffset:(cw+xoffset)] = corner

            corner = cv2.imread("images/C2.png")
            yoffset = 0
            xoffset = self.width - cw
            self.baseimg[yoffset:(ch+yoffset),xoffset:(cw+xoffset)] = corner

            corner = cv2.imread("images/C3.png")
            yoffset = 0
            xoffset = 0
            self.baseimg[yoffset:(ch+yoffset),xoffset:(cw+xoffset)] = corner

            self.outputtype = "calibrate"

        self.outputimg = self.baseimg.copy()
        return