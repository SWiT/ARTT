import cv2
from numpy import *

class Projector:

    def __init__(self, height, width):
        self.width = width
        self.height = height
        filename = "images/arena_" + str(self.width) + "_" + str(self.height) + ".png"
        self.baseimg = cv2.imread(filename)
        if self.baseimg == None:
            # Base arena file not found.
            # Create a empty gray image.
            self.baseimg = zeros((self.height,self.width,3), uint8)
            self.baseimg[:,:] = (254,254,254)

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
            
            # Save base arena as an image file, for later use.
            cv2.imwrite(filename, self.baseimg)

        self.outputimg = self.baseimg
        return
