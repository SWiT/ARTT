import cv2, subprocess
from numpy import *
from utils import *
import corner, projector

class Zone:
    used_vdi = []
    def __init__(self, idx, videodevices):
        self.id = idx   # Zone ID
        self.vdi = idx  # Video ID
        self.videodevices = videodevices    # list of video devices
        self.gridsize = (25, 18) # Grid size to apply to the zone. (inches or cm)
        self.v4l2ucp = -1   # Flag for v4l2ucp sub process
        self.cap = -1        # Capture device object (OpenCV)
        self.resolutions = [(640,480),(1280,720),(1920,1080)]
        self.ri = 1          # Selected resolution Index
        
        self.image = None
        self.width = 0
        self.height = 0
        
        self.warped = False        
        self.M = None  # Perspective Transform

        self.projector = projector.Projector(570, 800)
        cv2.namedWindow("ZoneProjector"+str(idx))

        # Add the corners.        
        self.corners = []
        self.corners.append(corner.Corner(idx, 0))
        self.corners.append(corner.Corner(idx, 1))
        self.corners.append(corner.Corner(idx, 2))
        self.corners.append(corner.Corner(idx, 3))
        
        self.initVideoDevice()
        return

    # The zone is calibrated if all corners are found.
    def calibrated(self):
        for c in self.corners:
            if not c.found:
                return False
        return True


    def recalibrate(self):
        for c in self.corners:
            c.found = False
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
        self.warped = False    
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
        cv2.destroyWindow("ZoneProjector"+str(self.id))
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

    def warpImage(self):
        # Prepare the transform if not done already.
        if self.M is None:
            pts1 = float32([self.corners[0].location, self.corners[1].location, self.corners[2].location, self.corners[3].location])
            pts2 = float32([[0,self.height],[self.width,self.height],[self.width,0],[0,0]])
            self.M = cv2.getPerspectiveTransform(pts1, pts2)

        # Get the destination for the warp from the output image. 
        # This is how transparency is done without alpha channel support.
        warpedimage = zeros((self.height, self.width, 3), uint8)
        dsize = (self.width, self.height)
        cv2.warpPerspective(self.image, self.M, dsize, dst=warpedimage, borderMode=cv2.BORDER_TRANSPARENT)
        self.image = warpedimage
        self.warped = True
        return



