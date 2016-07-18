import cv2, time, re
from numpy import *

class UI:
    def __init__(self):
        self.COLOR_WHITE = (255,255,255)
        self.COLOR_BLUE = (255,0,0)
        self.COLOR_LBLUE = (255, 200, 100)
        self.COLOR_GREEN = (0,240,0)
        self.COLOR_RED = (0,0,255)
        self.COLOR_YELLOW = (29,227,245)
        self.COLOR_PURPLE = (224,27,217)
        self.COLOR_GRAY = (127,127,127)
        self.h = 640 #control panel height
        self.w = 350 #control panel width
        self.lh = 20 #control panel line height
        self.pt = (0,self.lh) #control panel current text output position
        self.menurows = []
        self.display = 0
        self.displaySize = 100
        self.displayMode = 1
        self.numzones = 1

        self.frametime = time.time()
        self.fps = 0
        self.frametimes = []

        self.videoDevicePattern = re.compile('^videoDevice(\d)$')
        self.recalibratePattern = re.compile('^recalibrate(\d)$')

        self.exit = False

        # Display Modes
        self.SOURCE      = 0
        self.OVERLAY     = 1
        self.DATAONLY    = 2
        return

    def isDisplayed(self,idx):
        return self.display == idx or self.display == -1

    def displayAll(self):
        return self.display == -1

    def updateDisplayMode(self):
        self.displayMode += 1
        if self.displayMode > 2:
            self.displayMode = 0
        return

    def updateDisplay(self,v = None):
        if v is not None:
            self.display = v
        else:
            #print self.display, self.numzones
            self.display += 1
            if self.display >= self.numzones:
                self.display = -1
        return

    def updateDisplaySize(self):
        self.displaySize += 10
        if self.displaySize > 100:
            self.displaySize = 50
        return

    def menuSpacer(self):
        self.menurows.append("space")
        self.pt = (self.pt[0],self.pt[1]+self.lh)
        return

    #Calculate FPS
    def calcFPS(self):
        now = time.time()
        timediff = now - self.frametime
        self.frametimes.append(timediff)
        if len(self.frametimes) > 30:
            self.frametimes = self.frametimes[1:]

        self.fps = int(len(self.frametimes)/sum(self.frametimes))

        self.frametime = now
        return

    def onMouse(self,event,x,y,flags,param):
        #print "Mouse:",event,x,y,flags
        if event == cv2.EVENT_LBUTTONUP:
            Arena = param
            rowClicked = y/self.lh
            if rowClicked < len(self.menurows):
                if self.menurows[rowClicked] == "zones":
                    self.numzones = Arena.updateNumberOfZones()
                    self.updateDisplay(-1)

                elif self.menurows[rowClicked] == "exit":
                    self.exit = True

                elif self.menurows[rowClicked] == "displaymode":
                    self.updateDisplayMode()

                elif self.menurows[rowClicked] == "display":
                    if x <= 150:
                        self.updateDisplay()
                    else:
                        self.updateDisplaySize()

                else:
                    # Video device
                    match = self.videoDevicePattern.match(self.menurows[rowClicked])
                    if match:
                        zidx = int(match.group(1))
                        if x <= 28:
                            self.updateDisplay(zidx)
                        elif x <= 125:
                            Arena.zones[zidx].updateVideoDevice()
                        elif x <= 275:
                            Arena.zones[zidx].updateResolution()
                        else:
                            if Arena.zones[zidx].v4l2ucp != -1:
                                Arena.zones[zidx].closeV4l2ucp()
                            else:
                                Arena.zones[zidx].openV4l2ucp()
                        return

                    # Recalibrate zone
                    match = self.recalibratePattern.match(self.menurows[rowClicked])
                    if match:
                        zidx = int(match.group(1))
                        Arena.zones[zidx].recalibrate()
                        return
        return

    def nextrow(self):
        self.pt = (self.pt[0],self.pt[1]+self.lh)
        return

    def drawControlPanel(self, Arena):
        #Draw Control Panel
        self.pt = (0,self.lh)
        self.h = len(self.menurows)*self.lh+5 #calculate window height
        controlPanelImg = zeros((self.h,self.w,3), uint8) #create a blank image for the control panel
        menutextcolor = (255,255,255)
        self.menurows = []

        #Display Zones, video devices, and resolutions
        output = "Zones: "+str(Arena.numzones)
        cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("zones")
        self.nextrow()
        for z in Arena.zones:
            output = str(z.id)+": "
            cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            output = z.videodevices[z.vdi][5:] if z.vdi > -1 else "Off"
            cv2.putText(controlPanelImg, output, (self.pt[0]+28,self.pt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            output = str(z.resolutions[z.ri][0])+"x"+str(z.resolutions[z.ri][1])
            cv2.putText(controlPanelImg, output, (self.pt[0]+125,self.pt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            output = "settings"
            cv2.putText(controlPanelImg, output, (self.pt[0]+270,self.pt[1]-2), cv2.FONT_HERSHEY_PLAIN, 1.0, menutextcolor, 1)
            self.menurows.append("videoDevice"+str(z.id))
            self.nextrow()
            output = " "+str(z.width)+"x"+str(z.height)
            cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            self.menurows.append("calibartedres"+str(z.id))
            self.nextrow()

        self.menuSpacer()

        #Display
        output = "Display: "+str(self.display) if self.display>-1 else "Display: All"
        cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        #Display Size
        output = "Size: "+str(self.displaySize)+"%"
        cv2.putText(controlPanelImg, output, (self.pt[0]+150,self.pt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("display")
        self.nextrow()

        #Display Mode Labels
        output = "Mode: "
        if self.displayMode == self.SOURCE:   # Display source image
            output += "Source"
        elif self.displayMode == self.OVERLAY: # Display source with data overlay
            output += "Overlay"
        elif self.displayMode == self.DATAONLY: # Display data only
            output += "Data Only"
        cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)

        #Draw FPS
        output = "FPS: "+str(self.fps)
        cv2.putText(controlPanelImg, output, (self.w-105,self.pt[1]), cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("displaymode")
        self.nextrow()

        self.menuSpacer()

        # Draw card statuses and settings
        for k, c in Arena.cards.iteritems():
            output = str(c.id)+":"
            output += ' Z'+str(c.zid)
            output += ' '+str(c.locArena)
            output += ' '+str(c.heading)
            output += ' '+str(int(round((time.time()-c.time)*1000,0)))
            cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            self.menurows.append("card"+str(c.id))
            self.nextrow()

        self.menuSpacer()

        # Draw zone corner statuses
        for z in Arena.zones:
            for c in z.corners:
                output = "Z"+str(z.id)+" C"+str(c.symbolvalue)+":"
                #output += ' '+str(int(round((time.time()-c.time)*1000,0)))
                output += ' ' + str(c.found)
                cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
                self.menurows.append("z"+str(z.id)+"c"+str(c.idx))
                self.nextrow()
            # Draw the recalibrate button
            output = "Recalibrate Z"+str(z.id)
            cv2.putText(controlPanelImg, output, self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
            self.menurows.append("recalibrate"+str(z.id))
            self.nextrow()

        self.menuSpacer()

        # Draw Exit
        cv2.putText(controlPanelImg, "Exit", self.pt, cv2.FONT_HERSHEY_PLAIN, 1.5, menutextcolor, 1)
        self.menurows.append("exit")
        self.nextrow()

        return controlPanelImg

    def resize(self, img):
        # Resize output image
        if size(img,1) > 0 and size(img,0) > 0 and 0 < self.displaySize < 100:
            r = float(self.displaySize)/100
            img = cv2.resize(img, (0,0), fx=r, fy=r)
        return img

