import cv2, subprocess, os, time
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
        self.width = 1920
        self.height = 1080
        self.depth = 3

        # Initialize the project for the zone.
        # Set the projector image height and width to a little more than the projector's native resolution.
        self.projector = projector.Projector(self)
        cv2.namedWindow("ZoneProjector"+str(idx), cv2.WND_PROP_FULLSCREEN)

        self.camera = camera.Camera(self.height, self.width, "/dev/video0")
        self.calibrated = False
        self.detectedCorners    = None
        self.detectedIds        = None
        self.rejectedPoints     = None
        self.arucodict          = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.parameters         = aruco.DetectorParameters_create()
        return

    def scan(self):
        self.detectedCorners, self.detectedIds, self.rejectedPoints = aruco.detectMarkers(self.grayimage, self.arucodict, parameters=self.parameters)
        return

    def resolve(self):
        if not self.projector.calibrated:
            self.projector.resolve()
        return

    def recalibrate(self):
        self.calibrated = False
        for cm in self.projector.calmarker:
            cm.resetpos()
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

        # Draw the detected markers
        outputImg = aruco.drawDetectedMarkers(outputImg, self.detectedCorners, self.detectedIds)

        # Draw the projectors calibration points.
        region = []
        for cm in self.projector.calmarker:
            region.append(list(cm.calpos))
        pts = np.array(region, np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(outputImg, [pts], True, self.arena.ui.COLOR_BLUE, thickness = 2)

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



