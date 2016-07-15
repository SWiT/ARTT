import cv2, time, subprocess
from numpy import *
from utils import *

class Corner:
    def __init__(self, zid, idx):
        self.zid = zid
        self.idx = idx
        self.location = (-1, -1)
        self.symbolvalue = zid*4 + idx
        self.symbolcenter = (-1,-1)
        self.scanDistance = 0
        self.time = time.time()
        self.symboldimension = 4.1875
        self.gap = 1.625
        self.symbol = None
        self.found = False
        return
    
    def setData(self, symbol):
        self.symbol = symbol
        self.location = symbol[self.idx]
        self.symbolcenter = findCenter(symbol)
        
        offset = int(self.gap * (symbol[1][0]-symbol[0][0]) / self.symboldimension)
        offset_x_sign = 1 if (self.idx%3 != 0) else -1
        offset_y_sign = 1 if (self.idx < 2) else -1
        
        self.location = (self.location[0] + offset_x_sign * offset, self.location[1] + offset_y_sign * offset)
        self.time = time.time()
        return

class Zone:
    used_vdi = []
    def __init__(self, idx, videodevices):
        self.id = idx
        self.vdi = idx
        self.videodevices = videodevices
        self.actualsize = (72, 48) #zone size in inches
        self.v4l2ucp = -1
        self.cap = -1        #capture device object (OpenCV)
        self.resolutions = [(640,480),(1280,720),(1920,1080)]
        self.ri = 1          #selected Resolution Index
        
        self.image = None
        self.threshold = 219
        self.imageThresh = None
        self.width = 0;
        self.height = 0;
        
        self.corners = []
        self.corners.append(Corner(idx, 0))
        self.corners.append(Corner(idx, 1))
        self.corners.append(Corner(idx, 2))
        self.corners.append(Corner(idx, 3))
        
        self.initVideoDevice()
        return
        
    def setThreshold(self, v):
        self.threshold = v
        return
    
    def getImage(self):
        #skip if capture is disabled
        if self.cap == -1:
            return False
            
        #get the next frame from the zones capture device
        success, self.image = self.cap.read()
        if not success:
            print("Error reading from camera: "+str(self.vdi));
            global ui
            ui.exit = True
            return False
            
        self.width = size(self.image, 1)
        self.height = size(self.image, 0)
        
        #Threshold the image for leds
        self.imageThresh = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) #convert to grayscale
        ret,self.imageThresh = cv2.threshold(self.imageThresh, self.threshold, 255, cv2.THRESH_BINARY)
            
        return True
        
    
    def nextAvailableDevice(self):
        self.vdi += 1
        if self.vdi >= len(self.videodevices):
            self.vdi = 0
        if self.vdi != -1:
            try:
                self.used_vdi.index(self.vdi)
            except ValueError:
                return
            self.nextAvailableDevice()
        return
        
    def updateVideoDevice(self):
        self.close()
        self.nextAvailableDevice()
        if self.vdi > -1:
            self.initVideoDevice()
        else:
            self.close()    
        return
        
    def openV4l2ucp(self):
        self.v4l2ucp = subprocess.Popen(['v4l2ucp',self.videodevices[self.vdi]])
        return

    def closeV4l2ucp(self):
        if self.v4l2ucp != -1:
            self.v4l2ucp.kill()
            self.v4l2ucp = -1
        return
             
    def initVideoDevice(self):
        if self.vdi != -1:
            self.cap = cv2.VideoCapture(self.vdi)
            self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.resolutions[self.ri][0])
            self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.resolutions[self.ri][1])
            self.used_vdi.append(self.vdi)          
        return
        
    def close(self):
        self.closeV4l2ucp()
        self.closeCap()
        try:
            self.used_vdi.remove(self.vdi)
        except ValueError:
            pass
        return
    
    def closeCap(self):
        if self.cap != -1: 
            self.cap.release()
            self.cap = -1
        return
        
    def updateResolution(self):
        self.ri += 1
        if self.ri >= len(self.resolutions):
            self.ri = 0
        x = self.resolutions[self.ri][0]
        y = self.resolutions[self.ri][1]
        self.close()
        self.initVideoDevice()
        for corner in self.corners:
            corner.location = (-1, -1)
            corner.symbolcenter = (-1,-1)
        return