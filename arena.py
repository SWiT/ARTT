import re, os, cv2, time, re, os
import numpy as np

import zone, ui, procman
import cv2.aruco as aruco
from utils import *

class Arena:
    def __init__(self):
        self.numzones = 1    #default number of Zones
        self.zones = []
        self.videodevices = []

        self.corners            = []
        self.ids                = []
        self.rejectedImgPoints  = []
        self.aruco_dict         = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.parameters         = aruco.DetectorParameters_create()

        #Get lists of video devices
        video_pattern = re.compile('^video(\d)$')
        for dev in os.listdir('/dev/'):
            match = video_pattern.match(dev)
            if match:
                self.videodevices.append('/dev/'+dev)
        if len(self.videodevices) == 0:
            raise SystemExit('No video device found. (/dev/video#)')
        self.videodevices.sort()

        self.buildZones()

        self.ui = ui.UI()

        self.scantimeout = 1

        self.procman = procman.ProcessManager()

        return

    def updateNumberOfZones(self):
        self.numzones += 1
        if self.numzones > len(self.videodevices):
            self.numzones = 1
        self.buildZones()
        return self.numzones

    def buildZones(self):
        for z in self.zones:
            z.close()
            z.used_vdi = []
        self.zones = []
        for idx in range(0,self.numzones):
            self.zones.append(zone.Zone(idx, self.videodevices, self))


    def scan(self):
        # Scan each zone.
        for z in self.zones:
            z.getImage()
            timestamp = time.time()

            gray = cv2.cvtColor(z.image, cv2.COLOR_BGR2GRAY)
            self.corners, self.ids, self.rejectedImgPoints = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)


            # If the zone is calibrated
#            if z.calibrated:
                # Warp the zone part of the image and make it rectangular.
#                z.warpImage()

                # Handle any returned symbol data.
#                while self.procman.resultsAvailable():
#                    data = self.procman.getResult()
#                    if len(data) == 2:
#                        ts = data[0]    # timestamp
#                        symbols = data[1]
#                    else:
#                        continue
#
#                # Remove finished processes from the pool.
#                self.procman.removeFinished()
#
#                # Scan for all known markers.
#                #for marker in self.markers.iteritems():
#                    #roi = z.image[c.roiminy:c.roimaxy, c.roiminx:c.roimaxx]
#                    #self.procman.addProcess(timestamp, self.scantimeout, roi, c.roiminx, c.roiminy)
#
#                    # Blank the region of the image where the symbol was last seen.
#                    # Remove jitter by no includeing symbol[2]
#                    #s = copy(c.symbol)
#                    #s.pop(2)
#                    #s = np.delete()
#                    #print c.symbol
#                    #print s,"\n"
#
#                    #poly = array(c.symbol, int32)
#                    #cv2.fillConvexPoly(z.image, poly, (255,255,255))
#                    #cv2.putText(z.image, str(c.id), (c.location[0]-8, c.location[1]+8), cv2.FONT_HERSHEY_PLAIN, 1.5, c.color_augtext, 2)
#
#                # Scan for a new symbol.
#                self.procman.addProcess(timestamp, self.scantimeout, z.image)


            # If the zone is not calibrated
            #else:

            #    print "not calibrated."



        #End of zone loop
        return

    def render(self):
        # Start Output Image
        # Create a blank image
        if self.ui.displayAll():
            widthAll = 0
            heightAll = 0
            for z in self.zones:
                widthAll += z.width
                heightAll = z.height
            outputImg = zeros((heightAll, widthAll, 3), uint8)
        elif np.size(self.zones) > 0:
            outputImg = np.zeros((self.zones[self.ui.display].height, self.zones[self.ui.display].width, 3), np.uint8)
        else:
            outputImg = np.zeros((1080, 1920, 3), np.uint8)

        for z in self.zones:
            if z.calibrated:
                #z.projector.outputZoneImage()
                z.projector.outputCalibrationImage()
            else:
                z.projector.outputCalibrationImage()

            if self.ui.isDisplayed(z.id):
                # Prepare image based on display mode.
                if self.ui.displayMode == self.ui.DATAONLY:
                    img = np.zeros((z.height, z.width, 3), uint8) # Create a blank image
                else:
                    img = z.image

                # If we are only displaying the source image we are done.
                if self.ui.displayMode == self.ui.SOURCE:
                    if self.ui.displayAll():
                        outputImg[0:z.height, z.id*z.width:(z.id+1)*z.width] = img
                    else:
                        outputImg = img
                    continue;

                # Draw Objects on Scanner window
                # Crosshair in centeroutputImg
                pt0 = (z.width/2, z.height/2-5)
                pt1 = (z.width/2, z.height/2+5)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                pt0 = (z.width/2-5, z.height/2)
                pt1 = (z.width/2+5, z.height/2)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)


                # Draw the markers
                img = aruco.drawDetectedMarkers(img, self.corners, self.ids)


                if self.ui.displayAll():
                    outputImg[0:z.height, z.id*z.width:(z.id+1)*z.width] = img
                else:
                    outputImg = img


        return outputImg

