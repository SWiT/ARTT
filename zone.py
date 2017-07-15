import cv2, subprocess, os
import cv2.aruco as aruco
import numpy as np

from utils import *

import projector
import camera

class Zone:
    used_vdi = []
    def __init__(self, idx, videodevices, arena):
        self.arena = arena
        self.id = idx   # Zone ID
        self.gridsize = (36, 24) # Grid size to apply to the zone.

        self.image = None
        self.width = 0
        self.height = 0
        self.depth = 0

        # Initialize the project for the zone.
        # Set the projector image height and width to a little more than the projector's native resolution.
        self.projector = projector.Projector(600, 800)
        cv2.namedWindow("ZoneProjector"+str(idx), cv2.WND_PROP_FULLSCREEN)

        self.camera = camera.Camera(1080, 1920, "/dev/video0")
        self.calibrated = False
        self.calibrationCorners = [0,1,2,3]
        self.detectedCorners    = []
        self.detectedIds        = []
        self.rejectedPoints     = []
        self.aruco_dict         = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.parameters         = aruco.DetectorParameters_create()
        return

    def moveMarker(self, markerid, direction, amount):
        y,x = self.projector.markerpos[markerid]
        if direction == "left":
            x -= amount
            if x < 0:
                x = 0
        elif direction == "right":
            x += amount
            if x > self.projector.width - self.projector.markertotalsize:
                x = self.projector.width - self.projector.markertotalsize
        elif direction == "up":
            y -= amount
            if y < 0:
                y = 0
        elif direction == "down":
            y += amount
            if y > self.projector.height - self.projector.markertotalsize:
                y = self.projector.height - self.projector.markertotalsize
        self.projector.markerpos[markerid] = (y, x)
        return


    def moveMarkers(self, markerids, direction, amount):
        for markerid in markerids:
            self.moveMarker(markerid, direction, amount)
        return


    def scan(self):
        self.detectedCorners, self.detectedIds, self.rejectedPoints = aruco.detectMarkers(self.grayimage, self.aruco_dict, parameters=self.parameters)
        if not self.projector.calibrated and self.detectedIds is not None:
            
            # If 0 and 1 found move them left
            if 0 in self.detectedIds and 1 in self.detectedIds:
                self.moveMarkers((0,1), "left", 5)
            else:
                self.moveMarkers((0,1), "right", 1)

            if 1 in self.detectedIds and 2 in self.detectedIds:
                self.moveMarkers((1,2), "down", 5)
            else:
                self.moveMarkers((1,2), "up", 1)

            if 2 in self.detectedIds and 3 in self.detectedIds:
                self.moveMarkers((2,3), "right", 5)
            else:0
                self.moveMarkers((2,3), "left", 1)

            if 3 in self.detectedIds and 0 in self.detectedIds:
                self.moveMarkers((3,0), "up", 5)
            else:
                self.moveMarkers((3,0), "down", 1)
        print self.calibrationCorners
        return


    def recalibrate(self):
        self.calibrated = False
        self.projector.renderCalibrationImage()
        self.projector.outputCalibrationImage()
        return


    def getImage(self):
        self.image = self.camera.getImage()
        if self.camera.calibrated:
            self.image = self.camera.undistort()
            #TODO: Trim and warpPerspective of the undistorted image.

        self.grayimage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return


    def close(self):
        self.camera.close()
        cv2.destroyWindow("ZoneProjector"+str(self.id))
        return


    def render(self):
        outputImg = self.image

        if self.calibrated and self.projector.calibrated:
            self.projector.outputZoneImage()
        else:
            self.projector.outputCalibrationImage()

        # Draw Objects on Scanner window
        # Crosshair in centeroutputImg
        pt0 = (self.width/2, self.height/2-5)
        pt1 = (self.width/2, self.height/2+5)
        cv2.line(outputImg, pt0, pt1, self.arena.ui.COLOR_PURPLE, 1)
        pt0 = (self.width/2-5, self.height/2)
        pt1 = (self.width/2+5, self.height/2)
        cv2.line(outputImg, pt0, pt1, self.arena.ui.COLOR_PURPLE, 1)

        # Draw the markers
        outputImg = aruco.drawDetectedMarkers(outputImg, self.detectedCorners, self.detectedIds)

        return outputImg


    def warpImage(self):
        # crop the image
        #x, y, w, h = roi
        #if w > 0 and h > 0:
        #    dst = dst[y:y+h, x:x+w]
        #    self.image  = dst
        #    self.height = h
        #    self.width  = w

        #self.image  = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
#        if self.image is not None:
#            self.height, self.width, self.depth = self.image.shape

        # Warp the image to be the optimal size
#        warpedimage = zeros((self.warpheight, self.warpwidth, 3), uint8)
#        dsize = (self.warpwidth, self.warpheight)
#        cv2.warpPerspective(self.image, self.M, dsize, dst=warpedimage, borderMode=cv2.BORDER_TRANSPARENT)
#        self.image = warpedimage
#        self.height,self.width,self.depth = self.image.shape
#        self.warped = True
        return



