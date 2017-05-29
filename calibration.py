#!/usr/bin/env python2
#encoding: UTF-8
import time
import cv2
import cv2.aruco as aruco
import numpy as np

class Calibration:
    def __init__(self):
        self.COLOR_WHITE = (255,255,255)
        self.COLOR_BLUE = (255,0,0)
        self.COLOR_LBLUE = (255, 200, 100)
        self.COLOR_GREEN = (0,240,0)
        self.COLOR_RED = (0,0,255)
        self.COLOR_YELLOW = (29,227,245)
        self.COLOR_PURPLE = (224,27,217)
        self.COLOR_GRAY = (127,127,127)

        cols = 6
        rows = 4
        squaresize = 100
        markersize = 50
        margin = 20
        self.boardwidth = 800
        self.boardheight = 600

        self.displaySize = 60

        self.corners            = []
        self.ids                = []
        self.rejectedImgPoints  = []
        self.aruco_dict         = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.parameters         = aruco.DetectorParameters_create()

        self.calibrationCorners = []
        self.calibrationIds = []

        self.markercount = (cols*rows)/2

        self.board = cv2.aruco.CharucoBoard_create(cols,rows,squaresize,markersize, self.aruco_dict)
        self.calibrationimg = self.board.draw((self.boardwidth,self.boardheight), marginSize=margin)
        cv2.imwrite('calibration_charuco.png', self.calibrationimg)

        #Start capturing images for calibration
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.image     = None
        self.grayimage = None

        self.regionsX = 5
        self.regionsY = 5


        return

    def scan(self):
        # Detect markers in the image
        self.corners, self.ids, self.rejectedImgPoints = aruco.detectMarkers(self.grayimage, self.aruco_dict, parameters=self.parameters)
        # If come markers were found.
        if self.corners is not None and self.ids is not None:
            # If all markers found.
            if len(self.corners)==self.markercount and len(self.ids)==self.markercount:
                print len(self.ids),"found!!!"
                retval, charucoCorners, charucoIds = aruco.interpolateCornersCharuco(self.corners, self.ids, self.grayimage, self.board)
                if charucoCorners is not None and charucoIds is not None and len(charucoCorners)>3:
                    self.calibrationCorners.append(charucoCorners)
                    self.calibrationIds.append(charucoIds)
            else:
                print len(self.ids),"found"

        return

    def draw(self):
        # Draw detected markers
        aruco.drawDetectedMarkers(self.image, self.corners, self.ids)

        #Draw region of interest
        h,w,d = self.image.shape
        pt0 = (0,0)
        pt1 = (w-1,h-1)
        cv2.rectangle(self.image, pt0, pt1, self.COLOR_PURPLE, 1)
        return

    def resize(self):
        # Resize output image
        if np.size(self.image,1) > 0 and np.size(self.image,0) > 0 and 0 < self.displaySize < 100:
            r = float(self.displaySize)/100
            self.image = cv2.resize(self.image, (0,0), fx=r, fy=r)
        return

    def getFrame(self):
        # Get the next frame.
        ret,self.image = self.cap.read()
        # Convert to grayscale.
        self.grayimage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return

if __name__ == "__main__":
    print "SWiT's Calibration Script (Q to Exit)"

    cv2.namedWindow("Calibration")
    #cv2.startWindowThread() #This and waitKey don't like each other. Not sure why.

    cal = Calibration()

    while True:
        # Get the next frame.
        cal.getFrame()

        cal.scan()

        cal.draw()

        # Display the image or frame of video
        cal.resize()
        cv2.imshow('Calibration', cal.image)

        #Exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

#    if False:
#        print("Calibrating...")
        #Calibration fails for lots of reasons. Release the video if we do
#        try:
#            imsize = gray.shape
#            retval, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(allCorners,allIds,board,imsize,None,None)
#            print(retval, cameraMatrix, distCoeffs, rvecs, tvecs)
#        except:
#            cap.release()

    cal.cap.release()
    cv2.destroyAllWindows()
    print("Exit...")