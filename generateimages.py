#!/usr/bin/env python2
#encoding: UTF-8

import cv2
import cv2.aruco as aruco
import os

if __name__ == "__main__":
    print("ARuco generate images")
    current_directory = os.getcwd()
    print(current_directory)

    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
    markersize = 22
    blackborder = 1
    whiteborder = 1

    for markerid in range(0, 50):
        marker = cv2.cvtColor(aruco.drawMarker(aruco_dict, markerid, markersize,borderBits=blackborder), cv2.COLOR_GRAY2BGR) #borderBits
        if whiteborder > 0:
            marker = cv2.copyMakeBorder(marker, whiteborder, whiteborder, whiteborder, whiteborder, cv2.BORDER_CONSTANT, value=[255,255,255])
        
        directory = "DICT_4X4_50"
        if not os.path.exists(directory):
            os.makedirs(directory)
        imagefile = directory + "/4x4_" + "{:02d}".format(markerid) + ".png"
        
        cv2.imwrite(imagefile, marker)
        print("wrote: " + imagefile)
