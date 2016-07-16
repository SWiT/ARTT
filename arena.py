import re, os, cv2, time, re
from numpy import *

import card, zone, ui, dm
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
        self.dm = dm.DM(1, 200)
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
        self.zone = []
        for idx in range(0,self.numzones):
            self.zone.append(zone.Zone(idx, self.videodevices))
  
    def targettedScan(self):
        # Get the latest image for the zone.
        for z in self.zone:
            z.getImage()
            
        for k, c in self.cards.iteritems():
            c.scanDistance = int(dist(c.symbol[0], c.symbol[1]) * 1.5)
            z = self.zone[c.zid]
            xmin = c.locZonePx[0] - c.scanDistance
            xmax = c.locZonePx[0] + c.scanDistance
            ymin = c.locZonePx[1] - c.scanDistance
            ymax = c.locZonePx[1] + c.scanDistance
            if xmin < 0:
                xmin = 0
            if xmax > z.width:
                xmax = z.width
            if ymin < 0:
                ymin = 0
            if ymax > z.height:
                ymax = z.height
            roi = z.image[ymin:ymax,xmin:xmax]
            
            #Scan for DataMatrix
            if time.time() - c.time > .5:
                c.found = False
            self.dm.scan(roi, offsetx = xmin, offsety = ymin)
            for content,symbol in self.dm.symbols:
               match = self.cardPattern.match(content)
               if match:
                   if int(match.group(1)) == c.id and size(self.zone) > c.zid:
                       c.setData(symbol, z)    #update the card's data
                       
            if not c.found:
                #try the other zone
                print "Card",c.id, "Z",c.zid, c.locArena, time.time() - c.time
        return


    def scan(self):
        for z in self.zone:
            z.getImage()

            # Scan for DataMatrix
            self.dm.scan(z.image)

            # For each detected DataMatrix symbol
            for content,symbol in self.dm.symbols:
                # Card Symbol
                match = self.cardPattern.match(content)
                if match:
                    cardid = int(match.group(1))
                    try:
                        c = self.cards[cardid]
                        
                    except KeyError:
                        c = card.Card(cardid)
                        self.cards[cardid] = c
                    c.setData(symbol, z)    #update the cards's data
                    continue;

                # Zone Corner
                match = self.cornerPattern.match(content)
                if match:
                    cid = int(match.group(1))
                    z.corners[cid].setData(symbol)
                    continue;

        #End of zone loop
        return

    def render(self):
        # Start Output Image
        # Create a blank image
        if self.ui.displayAll():
            widthAll = 0
            heightAll = 0
            for z in self.zone:
                widthAll += z.width
                heightAll = z.height
            outputImg = zeros((heightAll, widthAll, 3), uint8)
        elif size(self.zone) > 0:
            outputImg = zeros((self.zone[self.ui.display].height, self.zone[self.ui.display].width, 3), uint8)
        else:
            outputImg = zeros((720, 1280, 3), uint8)
        
        for z in self.zone:
            if self.ui.isDisplayed(z.id):
                if self.ui.displayMode == 0:
                    img = cv2.cvtColor(z.imageThresh, cv2.COLOR_GRAY2BGR)
                elif self.ui.displayMode >= 2:
                    img = zeros((z.height, z.width, 3), uint8) #create a blank image
                else:
                    img = z.image
                    
                # Draw Objects on Scanner window if this zone is displayed
                # Crosshair in center
                pt0 = (z.width/2, z.height/2-5)
                pt1 = (z.width/2, z.height/2+5)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                pt0 = (z.width/2-5, z.height/2)
                pt1 = (z.width/2+5, z.height/2)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                
                # Zone edges
                corner_pts = []
                for corner in z.corners:
                    corner_pts.append(corner.location)
                    if self.ui.displayMode < 3 and corner.found:
                        xmin = corner.symbolcenter[0] - corner.scanDistance
                        xmax = corner.symbolcenter[0] + corner.scanDistance
                        ymin = corner.symbolcenter[1] - corner.scanDistance
                        ymax = corner.symbolcenter[1] + corner.scanDistance
                        drawBorder(img, [(xmin,ymax),(xmax,ymax),(xmax,ymin),(xmin,ymin)], self.ui.COLOR_LBLUE, 2)
                        drawBorder(img, corner.symbol, self.ui.COLOR_BLUE, 2)
                        pt = (corner.symbolcenter[0]-5, corner.symbolcenter[1]+5)  
                        cv2.putText(img, str(corner.symbolvalue), pt, cv2.FONT_HERSHEY_PLAIN, 1.5, self.ui.COLOR_BLUE, 2)
                drawBorder(img, corner_pts, self.ui.COLOR_BLUE, 2)
                
                # Last known card locations
                for cid, c in self.cards.iteritems():
                    if c.zid == z.id:                
                        c.drawLastKnownLoc(img)
                        if self.ui.displayMode < 3 and c.found:
                            xmin = c.locZonePx[0] - c.scanDistance
                            xmax = c.locZonePx[0] + c.scanDistance
                            ymin = c.locZonePx[1] - c.scanDistance
                            ymax = c.locZonePx[1] + c.scanDistance
                            drawBorder(img, [(xmin,ymax),(xmax,ymax),(xmax,ymin),(xmin,ymin)], self.ui.COLOR_LBLUE, 2)
                            c.drawOutput(img)   #draw the detection symbol
                        
                if self.ui.displayAll():
                    outputImg[0:z.height, z.id*z.width:(z.id+1)*z.width] = img
                else:
                    outputImg = img
                        
        return outputImg

