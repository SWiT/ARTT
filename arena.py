import re, os, cv2, time, re
from numpy import *

import card, zone, ui, dm, procman
from utils import *

class Arena:
    def __init__(self):
        self.numzones = 1    #default number of Zones
        self.zones = []
        self.cards = dict()
        self.videodevices = []

        self.cardPattern = re.compile('^(\d{2})$')
        self.cornerPattern = re.compile('^C(\d)$')

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
        self.scantimeout = 300
        self.dm = dm.DM(1, self.scantimeout)

        self.procman = procman.ProcessManager()

        return

    def setScanTimeout(self, v):
        self.scantimeout = v
        self.dm.setTimeout(self.scantimeout)

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
            self.zones.append(zone.Zone(idx, self.videodevices))


    def scan(self):
        # Scan each zone.
        for z in self.zones:
            z.getImage()
            timestamp = time.time()

            # If the zone is calibrated
            if z.calibrated:
                # Warp the zone part of the image and make it rectangular.
                z.warpImage()

                # Do Stuff with any returned symbol data.
                while self.procman.results():
                    data = self.procman.getResult()
                    if len(data) == 2:
                        ts = data[0]    # timestamp
                        symbols = data[1]
                    else:
                        continue

                    if len(symbols) == 1:
                        content = symbols[0][0]
                        points = symbols[0][1]
                    else:
                        continue

                    # Update or Add if it is a card symbol.
                    match = self.cardPattern.match(content)
                    if match:
                        cardid = int(match.group(1))
                        # Don't update invalid card numbers.
                        if cardid < card.idmin or card.idmax < cardid :
                            print cardid,"invalid"
                            continue

                        # Try to update the card. If it doesn't exist yet, create it.
                        try:
                            c = self.cards[cardid]
                        except KeyError:
                            c = card.Card(cardid)
                            self.cards[cardid] = c
                        c.setData(points, z)

                # Remove finished processes from the pool.
                self.procman.removeFinished()

                # Scan for all known cards.
                print self.cards
                for c in self.cards:
                    roi = z.image[c.roiminy:c.roimaxy, c.roiminx:c.roimaxx]
                    self.procman.addProcess(timestamp, self.scantimeout, roi, c.roiminx, c.roiminy)

                    # Blank the region of the image where the symbol was last seen.
                    poly = array(c.symbol, int32)
                    cv2.fillConvexPoly(z.image, poly, (245,255,245))

                # Scan for a new symbol.
                self.procman.addProcess(timestamp, self.scantimeout, z.image)


            # If the zone is not calibrated
            else:
                # Scan each unfound corner's region of interst
                calibrated = True
                for c in z.corners:
                    if not c.found:
                        calibrated = False
                        # Scan the roi
                        roi = z.image[c.roiymin:c.roiymax, c.roixmin:c.roixmax]
                        self.dm.scan(roi, offsetx = c.roixmin, offsety = c.roiymin)
                        # For each detected DataMatrix symbol, Should be only 1.
                        for content,symbol in self.dm.symbols:
                            # Blank the region of the image where the symbol was found.
                            poly = array(symbol, int32)
                            cv2.fillConvexPoly(z.image, poly, (255,255,255))

                            # Check if zone corner
                            match = self.cornerPattern.match(content)
                            if match:
                                # Update the corners position.
                                cid = int(match.group(1))
                                z.corners[cid].setData(symbol)

                z.calibrated = calibrated

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
        elif size(self.zones) > 0:
            outputImg = zeros((self.zones[self.ui.display].height, self.zones[self.ui.display].width, 3), uint8)
        else:
            outputImg = zeros((720, 1280, 3), uint8)

        for z in self.zones:
            if z.calibrated:
                z.projector.outputArenaImage()

            if self.ui.isDisplayed(z.id):
                # Prepare image based on display mode.
                if self.ui.displayMode == self.ui.DATAONLY:
                    img = zeros((z.height, z.width, 3), uint8) # Create a blank image
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
                # Crosshair in center
                pt0 = (z.width/2, z.height/2-5)
                pt1 = (z.width/2, z.height/2+5)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                pt0 = (z.width/2-5, z.height/2)
                pt1 = (z.width/2+5, z.height/2)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)

                # Zone edges
                if not z.calibrated:
                    corner_pts = []
                    for c in z.corners:
                        corner_pts.append(c.location)
                        if c.found:
                            drawBorder(img, c.symbol, self.ui.COLOR_BLUE, 1)
                            pt = (c.symbolcenter[0]-5, c.symbolcenter[1]+5)
                            cv2.putText(img, str(c.idx), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, self.ui.COLOR_BLUE, 2)
                    drawBorder(img, corner_pts, self.ui.COLOR_BLUE, 1)

                # Last known card locations
                for cid, c in self.cards.iteritems():
                    if c.zid == z.id:
                        c.drawLastKnownLoc(img)
                        if (time.time() - c.time) > 3:
                            c.found = False
                        else:
                            c.drawLastKnownLoc(z.projector.outputimg)
                            c.drawAugText(z.projector.outputimg)

                        if c.found:
                            # Draw the scanning area
                            xmin = c.locZonePx[0] - c.scanDistance
                            xmax = c.locZonePx[0] + c.scanDistance
                            ymin = c.locZonePx[1] - c.scanDistance
                            ymax = c.locZonePx[1] + c.scanDistance
                            drawBorder(img, [(xmin,ymax),(xmax,ymax),(xmax,ymin),(xmin,ymin)], self.ui.COLOR_LBLUE, 2)

                            c.drawDetected(img)   # Draw a border on the symbol.

                if self.ui.displayAll():
                    outputImg[0:z.height, z.id*z.width:(z.id+1)*z.width] = img
                else:
                    outputImg = img


        return outputImg

