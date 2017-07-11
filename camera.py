import cv2, os, subprocess
import numpy as np

class Camera:

    def __init__(self, height, width, device):
        self.height = height
        self.width = width
        self.device = device
        self.calibrationFile = "calibration.npz"
        self.calibrated = False
        self.cameraMatrix = None
        self.distCoefs = None
        self.newcameramtx = None
        self.v4l2ucp = None           # Flag for v4l2ucp sub process
        self.cap = None             # Capture device object (OpenCV)
        self.image = None
        self.initVideoDevice()
        self.loadCalibrationFile()
        return


    def initVideoDevice(self):
        self.cap = cv2.VideoCapture(self.device)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return


    def loadCalibrationFile(self):
        # Load the calibration.npz config file if it exists.
        if not os.path.exists(self.calibrationFile):
            print self.calibrationFile,"not found."
        else:
            data = np.load(self.calibrationFile)
            self.cameraMatrix = data['cameraMatrix']
            self.distCoefs = data['distCoefs']
            self.newcameramtx = data['newcameramtx']
            print self.calibrationFile,"loaded."
            self.calibrated = True
        return


    def getImage(self):
        #skip if capture is disabled
        if self.cap is None:
            return self.blank()

        #get the next frame from the cameras capture device
        success, self.image = self.cap.read()
        if not success:
            print "Error reading from camera: ", self.device
            global ui
            ui.exit = True
            return self.blank()

        self.height, self.width, self.depth = self.image.shape
        return self.image

    def undistort(self):
        if self.cameraMatrix is not None and self.distCoefs is not None and self.newcameramtx is not None:
            retimg = cv2.undistort(self.image, self.cameraMatrix, self.distCoefs, None, self.newcameramtx)
        else:
            retimg = self.blank()
        return retimg


    def openV4l2ucp(self):
        self.v4l2ucp = subprocess.Popen(['v4l2ucp',self.device])
        return

    def closeV4l2ucp(self):
        if self.v4l2ucp is not None:
            self.v4l2ucp.kill()
            self.v4l2ucp = None
        return

    def closeCap(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        return

    def close(self):
        self.closeV4l2ucp()
        self.closeCap()
        return

    def blank(self):
        return np.zeros((self.height, self.width, 3), np.uint8)
