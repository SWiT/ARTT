import re, os, cv2, time, re
from numpy import *

import card, zone, ui, dm
from utils import *

class Arena:    
    def __init__(self):
        self.numzones = 1    #default number of Zones
        self.zones = []
        self.cards = []
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
        for z in self.zone:
            z.close()
            z.used_vdi = []
        self.zone = []
        for idx in range(0,self.numzones):
            self.zone.append(zone.Zone(idx, self.videodevices))
  
    def targettedScan(self):
        # Get the latest image for the zone.
        for z in self.zone:
            z.getImage()
            
        for card in self.cards:
            card.scanDistance = int(dist(card.symbol[0], card.symbol[1]) * 1.5)
            z = self.zone[card.zid]
            xmin = card.locZonePx[0] - card.scanDistance
            xmax = card.locZonePx[0] + card.scanDistance
            ymin = card.locZonePx[1] - card.scanDistance
            ymax = card.locZonePx[1] + card.scanDistance
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
            if time.time() - card.time > .5:
                card.found = False
            self.dm.scan(roi, offsetx = xmin, offsety = ymin)
            for content,symbol in self.dm.symbols:
               match = self.cardPattern.match(content)
               if match:
                   if int(match.group(1)) == card.id and size(self.zone) > card.zid:
                       card.setData(symbol, z)    #update the card's data
                       
            if not card.found:
                #try the other zone
                print "Card",card.id, "Z",card.zid, card.locArena, time.time() - card.time
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
                    self.card[cardid].setData(symbol, z)    #update the cards's datac
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
        #Start Output Image
        #create a blank image
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
                    
                #Draw Objects on Scanner window if this zone is displayed
                #Crosshair in center
                pt0 = (z.width/2, z.height/2-5)
                pt1 = (z.width/2, z.height/2+5)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                pt0 = (z.width/2-5, z.height/2)
                pt1 = (z.width/2+5, z.height/2)
                cv2.line(img, pt0, pt1, self.ui.COLOR_PURPLE, 1)
                
                #Zone edges
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
                
                #Last Known Bot Locations
                for bot in self.bot:
                    if bot.zid == z.id:                
                        bot.drawLastKnownLoc(img)
                        if self.ui.displayMode < 3 and bot.found:
                            xmin = bot.locZonePx[0] - bot.scanDistance
                            xmax = bot.locZonePx[0] + bot.scanDistance
                            ymin = bot.locZonePx[1] - bot.scanDistance
                            ymax = bot.locZonePx[1] + bot.scanDistance
                            drawBorder(img, [(xmin,ymax),(xmax,ymax),(xmax,ymin),(xmin,ymin)], self.ui.COLOR_LBLUE, 2)
                            bot.drawOutput(img)   #draw the detection symbol
                        
                if self.ui.displayAll():
                    outputImg[0:z.height, z.id*z.width:(z.id+1)*z.width] = img
                else:
                    outputImg = img
                        
        return outputImg

