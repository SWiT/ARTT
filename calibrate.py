#!/usr/bin/env python2
#encoding: UTF-8
import time
import cv2
import cv2.aruco as aruco
import numpy as np

class Calibrate:
    def __init__(self):
        cols = 6
        rows = 4
        squaresize = 100
        markersize = 50
        margin = 20
        self.boardwidth = 800
        self.boardheight = 600

        self.displaySize = 70

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

        self.image     = None
        self.grayimage = None

        return

    def scan(self, image):
        self.image = image
        #convert to grayscale
        self.grayimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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

    def draw(self, image):
        aruco.drawDetectedMarkers(image, self.corners, self.ids)
        return image

    def resize(self, image):
        # Resize output image
        if np.size(image,1) > 0 and np.size(image,0) > 0 and 0 < self.displaySize < 100:
            r = float(self.displaySize)/100
            image = cv2.resize(image, (0,0), fx=r, fy=r)
        return image

if __name__ == "__main__":
    print "SWiT's Calibration Script (Q to Exit)"

    cv2.namedWindow("Calibration")
    #cv2.startWindowThread()

    calibrate = Calibrate()

    #Start capturing images for calibration
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while True:
        # Get the next frame.
        ret,image = cap.read()


        calibrate.scan(image)

        image = calibrate.draw(image)

        # Display the image or frame of video
        image = calibrate.resize(image)
        cv2.imshow('Calibration',image)

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

    cap.release()
    cv2.destroyAllWindows()
    print("Exit...")