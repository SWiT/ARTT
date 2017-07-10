#!/usr/bin/env python2
#encoding: UTF-8
import cv2, os, time, re
import cv2.aruco as aruco
import numpy as np
import json


class Calibration:
    def __init__(self):
        self.COLOR_WHITE = (255,255,255)
        self.COLOR_BLUE = (255,0,0)
        self.COLOR_LBLUE = (255, 200, 100)
        self.COLOR_GREEN = (0,240,0)
        self.COLOR_RED = (0,0,255)
        self.COLOR_DRED = (0,0,139)
        self.COLOR_YELLOW = (29,227,245)
        self.COLOR_PURPLE = (224,27,217)
        self.COLOR_GRAY = (127,127,127)

        boardcols = 7
        boardrows = 6
        boardsquaresize = 100
        boardmarkersize = 80
        boardmargin = 0
        boardwidth = 800
        boardheight = 600
        self.markercount = (boardcols*boardrows)/2

        self.displaySize = 60

        self.corners            = []
        self.ids                = []
        self.rejectedImgPoints  = []
        self.aruco_dict         = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.parameters         = aruco.DetectorParameters_create()

        self.calibrationCorners = []
        self.calibrationIds = []

        self.board = cv2.aruco.CharucoBoard_create(boardcols,boardrows,boardsquaresize,boardmarkersize, self.aruco_dict)
        self.boardimage = self.board.draw((boardwidth,boardheight), marginSize=boardmargin, borderBits=1 )
        cv2.imwrite('charuco_board.png', self.boardimage)

        self.folder = "images"

        # Create the capture object
        self.imageWidth = 1920
        self.imageHeight = 1080
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.imageWidth)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.imageHeight)

        self.image     = None
        self.grayimage = None

        self.roiPt0 = (0, 0)
        self.roiPt1 = (0,0)
        self.resetROI()

        self.savenext = False
        self.calibrated = False
        self.undistort = True
        self.exit = False

        self.cameraMatrix = None
        self.distCoefs = None
        self.rvecs = None
        self.tvecs = None
        self.newcameramtx = None
        self.roi = None

        self.charucoCorners = None
        self.charucoIds = None

        return

    # Reset the Region Of Interest to the whole image
    def resetROI(self):
        self.roiPt0 = (0, 0)
        self.roiPt1 = (self.imageWidth-1, self.imageHeight-1)

    def scan(self):
        # Get the ROI
        roi = self.grayimage[self.roiPt0[1]:self.roiPt1[1],self.roiPt0[0]:self.roiPt1[0]]
        # Detect markers in the image
        self.corners, self.ids, self.rejectedImgPoints = aruco.detectMarkers(roi, self.aruco_dict, parameters=self.parameters)
        # If no markers were found.
        if self.corners is None or self.ids is None:
            self.ids = np.array([])
            self.corners = np.array([])
            self.charucoCorners = np.array([])
            self.charucoIds = np.array([])
        else:
            retval, self.charucoCorners, self.charucoIds = aruco.interpolateCornersCharuco(self.corners, self.ids, self.grayimage, self.board)
        return


    def foundAllMarkers(self):
        return len(self.corners)==self.markercount and len(self.ids)==self.markercount


    def draw(self):
        # Get the ROI.
        roi = self.image[self.roiPt0[1]:self.roiPt1[1],self.roiPt0[0]:self.roiPt1[0]]

        # Draw detected markers.
        aruco.drawDetectedMarkers(roi, self.corners)

        # Put the ROI back.
        self.image[self.roiPt0[1]:self.roiPt1[1],self.roiPt0[0]:self.roiPt1[0]] = roi

        #Draw the detected Charuco corners.
        aruco.drawDetectedCornersCharuco(self.image, self.charucoCorners, cornerColor=self.COLOR_BLUE)

        #Draw the detected calibration points.
        for idx, corners in enumerate(self.calibrationCorners):
            #print idx
            #aruco.drawDetectedCornersCharuco(self.image, self.calibrationCorners[idx], self.calibrationIds[idx], self.COLOR_LBLUE)
            aruco.drawDetectedCornersCharuco(self.image, self.calibrationCorners[idx], cornerColor=self.COLOR_LBLUE)

        return
        #Draw region of interest
        cv2.rectangle(self.image, self.roiPt0, self.roiPt1, self.COLOR_PURPLE, 2)




    def resize(self):
        # Resize output image
        if np.size(self.image,1) > 0 and np.size(self.image,0) > 0 and 0 < self.displaySize < 100:
            r = float(self.displaySize)/100
            self.image = cv2.resize(self.image, (0,0), fx=r, fy=r)
        return


    def display(self):
        self.resize()
        cv2.imshow("Calibration", self.image)
        return

    def getFrame(self):
        # Get the next frame.
        ret, self.image = self.cap.read()
        # Convert to grayscale.
        self.grayimage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return

    def loadimages(self):
        self.calibrationCorners = []
        self.calibrationIds = []
        print "Loading image files..."

        if not os.path.isdir(self.folder):
            os.mkdir(self.folder)
            if not os.path.isdir(self.folder):
                print "Error creating "+self.folder+"/"
                exit();
            else:
                print "created "+self.folder+"/"

        listdir = os.listdir(self.folder)
        if len(listdir) == 0:
            print "No image files found in "+self.folder+"/"
            return()

        listdir.sort()
        foundallcount = 0
        for fn in listdir:
            fullpath = self.folder + "/" + fn
            self.image = cv2.imread(fullpath)
            self.grayimage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

            self.scan()
            foundmsg = ""
            if self.foundAllMarkers():
                foundmsg = "Found All Markers"
                if self.charucoCorners is not None and self.charucoIds is not None and len(self.charucoCorners)>3:
                    self.calibrationCorners.append(self.charucoCorners)
                    self.calibrationIds.append(self.charucoIds)
                foundallcount += 1

            else:
                foundmsg = "corners",len(self.corners),"ids",len(self.ids)
            self.display()
            print fn, foundmsg
            cv2.waitKey(10)

        print foundallcount,"images loaded."
        return

    def calibrate(self):
        self.loadimages()

        # Ready to calibrate.
        print "Calibrating..."
        try:
            retval, self.cameraMatrix, self.distCoefs, self.rvecs, self.tvecs = aruco.calibrateCameraCharuco(self.calibrationCorners, self.calibrationIds, self.board, self.grayimage.shape,None,None)
            #print(retval, cameraMatrix, distCoeffs, rvecs, tvecs)

            self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.distCoefs, (self.imageWidth, self.imageHeight), 1, (self.imageWidth, self.imageHeight))
            #print(self.newcameramtx, self.roi)

            print "Calibration successful"
            self.calibrated = True
        except:
            print "Calibration failed"
            exit()
        return

    def printCameraData(self):
        print "cameraMatrix"
        print type(self.cameraMatrix)
        print self.cameraMatrix
        print
        print "distCoefs"
        print type(self.distCoefs)
        print self.distCoefs
        print
        print"newcameramtx"
        print type(self.newcameramtx)
        print self.newcameramtx
        print
        return

    def saveconfig(self):
        if self.calibrated:
            self.printCameraData()
            np.savez('calibration.npz', cameraMatrix=self.cameraMatrix, distCoefs=self.distCoefs, newcameramtx=self.newcameramtx)
            print "calibration.npz saved."
        else:
            print "Not calibrated. Press 'C' to calibrate."
        return


    def loadconfig(self):
        if not os.path.exists('calibration.npz'):
            print "calibration.npz not found."
            return

        data = np.load('calibration.npz')
        self.cameraMatrix = data['cameraMatrix']
        self.distCoefs = data['distCoefs']
        self.newcameramtx = data['newcameramtx']
        self.printCameraData()
        print "calibration.npz loaded."
        return

if __name__ == "__main__":
    print "***************************************"
    print "SWiT's Camera Lens Calibration Script"
    print "***************************************"
    print "Q or Esc to exit"
    print "[Space] to save the next valid image"
    print "L to load or reload images"
    print "C to calibrate"
    print "U to toggle undistorting"
    print "R to reset"
    print "S to save calibration.npz"
    print "F to load calibration.npz"
    print "***************************************"

    cv2.namedWindow("Calibration")
    cal = Calibration()

    while not cal.exit:
        # Get the next frame.
        cal.getFrame()

        if cal.calibrated:
            if cal.undistort:
                # Undistort the image
                cal.image = cv2.undistort(cal.image, cal.cameraMatrix, cal.distCoefs, None, cal.newcameramtx)

                if cal.roi is not None:
                    #Draw region of interest
                    cv2.rectangle(cal.image, (cal.roi[0], cal.roi[1]), (cal.roi[2], cal.roi[3]), cal.COLOR_PURPLE, 2)

        else:
            # Scan the ROI
            cal.scan()

            if len(cal.ids) > 0:
                retval, charucoCorners, charucoIds = aruco.interpolateCornersCharuco(cal.corners, cal.ids, cal.grayimage, cal.board)

            # If all markers found.
            if cal.foundAllMarkers() and cal.savenext:
                # Save image
                fn = cal.folder+"/"+time.strftime("%Y%m%d%H%M%S")+".png"
                cv2.imwrite(fn, cal.image)
                print "wrote",fn
                cal.savenext = False

            cal.draw()

        # Display the image or frame of video
        cal.resize()
        cv2.imshow('Calibration', cal.image)

        # Handle any command key presses.
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key == 27: # q or Esc to exit
            cal.exit = True

        elif key & 0xFF == ord('u'):            # u to toggle undistorting the image once calibrated.
            cal.undistort = not cal.undistort

        elif key & 0xFF == ord(' '):            # [Space] to save next valid image
            print "Save Next."
            cal.savenext = True

        elif key & 0xFF == ord('c'):            # c to run calibtaion on saved images
            cal.calibrate()

        elif key & 0xFF == ord('r'):            # r to reset
            cal.calibrated = False

        elif key & 0xFF == ord('l'):            # l to reload images
            cal.loadimages()

        elif key & 0xFF == ord('s'):            # s to save the calibration data to config.json
            cal.saveconfig()

        elif key & 0xFF == ord('f'):            # f to load the calibration data from calibration.npz
            cal.loadconfig()
            cal.calibrated = True

        elif key != 255 and key != -1:
            print "key",key

    #Exit
    cal.cap.release()
    cv2.destroyAllWindows()
    print("Exit.")