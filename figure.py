#!/usr/bin/env python2
#encoding: UTF-8

import cv2
import cv2.aruco as aruco

if __name__ == "__main__":
    print "AR Figure"

    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
    markersize = 24
    blackborder = 1
    whiteborder = 100/8

    for markerid in range(0, 6):
        marker = cv2.cvtColor(aruco.drawMarker(aruco_dict, markerid, markersize,borderBits=blackborder), cv2.COLOR_GRAY2BGR) #borderBits
        marker = cv2.copyMakeBorder(marker, whiteborder, whiteborder, whiteborder, whiteborder, cv2.BORDER_CONSTANT, value=[255,255,255])
        imagefile = "images/aruco_4X4_" + str(markerid)+".png"
        cv2.imwrite(imagefile, marker)
        print "wrote: " + imagefile