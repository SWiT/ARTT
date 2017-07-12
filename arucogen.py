#!/usr/bin/env python2
#encoding: UTF-8

import cv2, os
import cv2.aruco as aruco

if __name__ == "__main__":
    print "Creating DICT_4X4_100 arucos"

    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
    markersize = 22
    blackborder = 1
    whiteborder = 1
    folder = "arucos"
    if not os.path.isdir(folder):
        os.mkdir(folder)

    for markerid in range(0, 100):
        marker = cv2.cvtColor(aruco.drawMarker(aruco_dict, markerid, markersize,borderBits=blackborder), cv2.COLOR_GRAY2BGR) #borderBits
        if whiteborder > 0:
            marker = cv2.copyMakeBorder(marker, whiteborder, whiteborder, whiteborder, whiteborder, cv2.BORDER_CONSTANT, value=[255,255,255])
        imagefile = folder+"/4X4_" + str(markerid)+".png"
        cv2.imwrite(imagefile, marker)
        print "wrote: " + imagefile