#!/usr/bin/env python2
#encoding: UTF-8
import cv2, os, time
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

        boardcols = 5
        boardrows = 4
        boardsquaresize = 100
        boardmarkersize = 50
        boardmargin = 20
        self.boardwidth = 800
        self.boardheight = 600
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
        self.boardimage = self.board.draw((self.boardwidth,self.boardheight), marginSize=boardmargin)
        cv2.imwrite('calibration_charuco.png', self.boardimage)

        self.folder = "calibrationimages"

        # Create the capture object
        self.imageWidth = 1920
        self.imageHeight = 1080
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.imageWidth)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.imageHeight)

        self.image     = None
        self.grayimage = None

        self.roiY = 5
        self.roiX = 7
        self.roiReady = np.zeros((self.roiY, self.roiX));
        self.roiPt0 = (0, 0)
        self.roiPt1 = (0, 0)
        self.roiWidth = self.imageWidth/((self.roiX+1)/2)
        self.roiHeight = self.imageHeight/((self.roiY+1)/2)
        self.roiCurr = [0, 0]
        self.setROI()

        self.calibrated = False
        self.exit = False

        self.cameraMatrix = None
        self.distCoefs = None
        self.rvecs = None
        self.tvecs = None
        self.undistort = True
        return


    def nextUnreadyROI(self):
        self.nextROI()
        while self.isROIReady():
            self.nextROI()
            if self.allROIReady():
                self.resetROI()
                break;
        return


    def allROIReady(self):
        return len(np.where(self.roiReady == 0)[0]) == 0


    def nextROI(self):
        self.roiCurr[0] += 1
        if self.roiCurr[0] % self.roiX == 0:
            self.roiCurr[0] = 0
            self.roiCurr[1] += 1
            if self.roiCurr[1] % self.roiY == 0:
                self.roiCurr[1] = 0
        self.setROI()
        return


    def setROI(self):
        pt0 = 0 + int(self.roiWidth/2 * self.roiCurr[0])
        pt1 = 0 + int(self.roiHeight/2 * self.roiCurr[1])
        self.roiPt0 = (pt0, pt1)
        pt0 = self.roiWidth + (self.roiWidth/2 * self.roiCurr[0]) - 1
        pt1 = self.roiHeight + (self.roiHeight/2 * self.roiCurr[1]) - 1
        self.roiPt1 = (pt0, pt1)
        #print "roi:", self.roiCurr, self.roiPt0, self.roiPt1
        return


    def resetROI(self):
        self.roiPt0 = (0, 0)
        self.roiPt1 = (self.imageWidth-1, self.imageHeight-1)
        #print "roi:", "All", self.roiPt0, self.roiPt1
        return


    def isROIReady(self):
        return self.roiReady[self.roiCurr[1], self.roiCurr[0]] == 1

    def scan(self):
        # Get the ROI
        roi = self.grayimage[self.roiPt0[1]:self.roiPt1[1],self.roiPt0[0]:self.roiPt1[0]]
        # Detect markers in the image
        self.corners, self.ids, self.rejectedImgPoints = aruco.detectMarkers(roi, self.aruco_dict, parameters=self.parameters)
        # If no markers were found.
        if self.corners is None or self.ids is None:
            self.ids = np.array([])
            self.corners = np.array([])
        return


    def allFound(self):
        return len(self.corners)==self.markercount and len(self.ids)==self.markercount

    def draw(self):
        # Get the ROI.
        roi = self.image[self.roiPt0[1]:self.roiPt1[1],self.roiPt0[0]:self.roiPt1[0]]
        # Draw detected markers.
        aruco.drawDetectedMarkers(roi, self.corners, self.ids)
        # Put the ROI back.
        self.image[self.roiPt0[1]:self.roiPt1[1],self.roiPt0[0]:self.roiPt1[0]] = roi

        #Draw region of interest
        cv2.rectangle(self.image, self.roiPt0, self.roiPt1, self.COLOR_PURPLE, 2)
        return


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


    def calibrate(self):
        self.calibrationCorners = []
        self.calibrationIds = []
        print "Reading image files..."
        listdir = os.listdir(self.folder)
        listdir.sort()
        self.resetROI()
        for fn in listdir:
            fullpath = self.folder + "/" + fn
            self.image = cv2.imread(fullpath)
            self.grayimage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

            self.scan()
            foundmsg = ""
            if self.allFound():
                foundmsg = "All Found"
                roiX = int(fn.split(".")[0].split("_")[1])
                roiY = int(fn.split(".")[0].split("_")[0])
                self.roiReady[roiY, roiX] = 1

                retval, charucoCorners, charucoIds = aruco.interpolateCornersCharuco(self.corners, self.ids, self.grayimage, self.board)
                if charucoCorners is not None and charucoIds is not None and len(charucoCorners)>3:
                    self.calibrationCorners.append(charucoCorners)
                    self.calibrationIds.append(charucoIds)

            else:
                foundmsg = "corners",len(self.corners),"ids",len(self.ids)
            self.display()
            print fn, foundmsg
            cv2.waitKey(25)

        print self.roiReady

        if self.allROIReady():
            # Ready to calibrate when all calibration image have been processed.
            print "Calibrating..."
            try:
                retval, self.cameraMatrix, self.distCoefs, self.rvecs, self.tvecs = aruco.calibrateCameraCharuco(self.calibrationCorners, self.calibrationIds, self.board, self.grayimage.shape,None,None)
                #print(retval, cameraMatrix, distCoeffs, rvecs, tvecs)
                print "Calibration successful"
                self.calibrated = True
            except:
                print "Calibration failed"
                exit()
        return


    def checkCalibrationFiles(self):
        listdir = os.listdir(self.folder)
        found = len(listdir)
        print found,"images found."
        return found == (self.roiX * self.roiY)


if __name__ == "__main__":
    print "SWiT's Calibration Script (Q to Exit, U to toggle undistorting)"

    cv2.namedWindow("Calibration")

    cal = Calibration()

    if cal.checkCalibrationFiles():
        cal.calibrate()

    cal.setROI()
    cal.nextUnreadyROI()

    while not cal.exit:
        # Get the next frame.
        cal.getFrame()
        if cal.calibrated:
            if cal.undistort:
                # Undistort the image
                h,  w = cal.image.shape[:2]
                newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cal.cameraMatrix, cal.distCoefs, (w, h), 1, (w, h))
                cal.image = cv2.undistort(cal.image, cal.cameraMatrix, cal.distCoefs, None, newcameramtx)

        else:
            if cal.allROIReady():
                cal.calibrate()

            else:
                # Scan the ROI
                cal.scan()
                # If all markers found.
                if cal.allFound():
                    print "found all in ROI"
                    # Now scan the whole image.
                    cal.resetROI()
                    cal.scan()
                    # If all markers found.
                    if cal.allFound():
                        print "found all in whole image"
                        # Set the ROI as ready for calibration
                        cal.roiReady[cal.roiCurr[1], cal.roiCurr[0]] = 1

                        # Save image
                        fn = cal.folder+"/"+str(cal.roiCurr[1])+"_"+str(cal.roiCurr[0])+".jpg"
                        cv2.imwrite(fn, cal.image)
                        print "wrote",fn

                        # Next region
                        cal.nextUnreadyROI()
                cal.draw()

        # Display the image or frame of video
        cal.resize()
        cv2.imshow('Calibration', cal.image)

        # Handle any command key presses.
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key == 27: # q or Esc to exit
            break
        elif key & 0xFF == ord('u'):            # u to toggle undistorting the image once calibrated.
            cal.undistort = not cal.undistort
        #elif key != 255:
        #    print "key",key

    #Exit
    cal.cap.release()
    cv2.destroyAllWindows()
    print("Exit.")