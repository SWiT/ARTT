import cv2, time, subprocess
from numpy import *
from utils import *

class Corner:
    def __init__(self, zid, idx):
        self.zid = zid
        self.idx = idx
        self.location = (-1, -1)
        self.symbolvalue = idx
        self.symbolcenter = (-1,-1)
        self.scanDistance = 0
        self.time = time.time()
        self.symboldimension = 10
        self.gap = 1
        self.symbol = None
        self.found = False
        return
    
    def setData(self, symbol):
        self.symbol = symbol
        self.location = symbol[self.idx]
        self.symbolcenter = findCenter(symbol)
        
        offset = int((symbol[1][0]-symbol[0][0]) * self.gap / self.symboldimension)
        offset_x_sign = 1 if (self.idx%3 != 0) else -1
        offset_y_sign = 1 if (self.idx < 2) else -1
        
        self.location = (self.location[0] + offset_x_sign * offset, self.location[1] + offset_y_sign * offset)
        self.time = time.time()
        return

class Zone:
    used_vdi = []
    def __init__(self, idx, videodevices):
        self.id = idx   # Zone ID
        self.vdi = idx  # Video ID
        self.videodevices = videodevices    # list of video devices
        self.actualsize = (72, 48) # Zone size in inches
        self.v4l2ucp = -1   # Flag for v4l2ucp sub process
        self.cap = -1        # Capture device object (OpenCV)
        self.resolutions = [(640,480),(1280,720),(1920,1080)]
        self.ri = 1          # Selected resolution Index
        
        self.image = None
        self.width = 0;
        self.height = 0;
    
        # Add the corners.        
        self.corners = []
        self.corners.append(Corner(idx, 0))
        self.corners.append(Corner(idx, 1))
        self.corners.append(Corner(idx, 2))
        self.corners.append(Corner(idx, 3))
        
        self.calibrated = False # All corners were found.

        self.initVideoDevice()
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
