import cv2, subprocess, os
import cv2.aruco as aruco
from numpy import *
from utils import *
import projector

class Zone:
    used_vdi = []
    def __init__(self, idx, videodevices, arena):
        self.arena = arena
        self.id = idx   # Zone ID
        self.vdi = idx  # Video ID
        self.videodevices = videodevices    # list of video devices
        self.gridsize = (25, 18) # Grid size to apply to the zone.
        self.v4l2ucp = -1   # Flag for v4l2ucp sub process
        self.cap = -1        # Capture device object (OpenCV)
        self.resolutions = [(1920,1080)] # new camera crashes if resolution is changed
        self.ri = 0          # Selected resolution Index
        self.srcwidth = 0
        self.srcheight = 0

        self.image = None
        self.width = 0
        self.height = 0
        self.depth = 0

        self.cameraMatrix = None
        self.distCoefs = None
        self.rvecs = None
        self.tvecs = None
        self.warped = False
        self.warpwidth = 0
        self.warpheight = 0

        # Initialize the project for the zone.
        # Set the projector image height to a little less than the native vertical resolution.
        # Set the projector image width to the native horizontal resolution.
        self.projector = projector.Projector(600, 800)
        cv2.namedWindow("ZoneProjector"+str(idx), cv2.WND_PROP_FULLSCREEN)

        self.initVideoDevice()

        self.calibrated = False

        self.calibrationCorners = []
        self.calibrationIds = []

        self.corners            = []
        self.ids                = []
        self.rejectedImgPoints  = []
        self.aruco_dict         = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.parameters         = aruco.DetectorParameters_create()


        # Calibrate for the distortion of the camera lens.
        for fn in os.listdir("calibrationimages"):
            fn = "calibrationimages/"  +fn
            gray = cv2.imread(fn, 0)
            self.image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            cv2.imshow("ArenaScanner", self.image)
            self.corners, self.ids, self.rejectedImgPoints = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)

            if self.ids is not None and len(self.ids) == (self.projector.markercount):
                allfound = "!!!"
                if len(self.corners) > 0:
                    retval, charucoCorners, charucoIds = cv2.aruco.interpolateCornersCharuco(self.corners, self.ids, gray, self.projector.board)
                    if charucoCorners is not None and charucoIds is not None and len(charucoCorners)==len(charucoIds):
                        self.calibrationCorners.append(charucoCorners)
                        self.calibrationIds.append(charucoIds)
            else:
                allfound = ""

            print fn,len(self.ids),"found",allfound

        # Ready to calibrate when all calibration image have been processed.
        print "Calibrating..."
        try:
            retval, z.cameraMatrix, z.distCoefs, z.rvecs, z.tvecs = cv2.aruco.calibrateCameraCharuco(self.calibrationCorners, self.calibrationIds, z.projector.board, gray.shape,None,None)
            #print(retval, cameraMatrix, distCoeffs, rvecs, tvecs)
            print "Calibration successful"
            self.calibrated = True
        except:
            print "Calibration failed"

        return

    def recalibrate(self):
        self.calibrated = False
        self.cameraMatrix = None
        self.distCoefs = None
        self.rvecs = None
        self.tvecs = None
        self.projector.outputCalibrationImage()
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

        self.height,self.width,self.depth = self.image.shape

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
            self.srcwidth = self.resolutions[self.ri][0]
            self.srcheight = self.resolutions[self.ri][1]
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.srcwidth)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.srcheight)
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
        # Undistort the frame

        #img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        img = self.image
        h,  w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.distCoefs, (w, h), 1, (w, h))
        dst = cv2.undistort(img, self.cameraMatrix, self.distCoefs, None, newcameramtx)
        self.image = dst
        #print "roi:", roi

        # crop the image

        x, y, w, h = roi
        if w > 0 and h > 0:
            dst = dst[y:y+h, x:x+w]
            self.image  = dst
            self.height = h
            self.width  = w

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



