import cv2
from numpy import *
import arena

   
###############
## SETUP
###############
Arena = arena.Arena()

cv2.namedWindow("ArenaScanner")
cv2.namedWindow("ArenaProjector")
cv2.namedWindow("ArenaControlPanel")
cv2.startWindowThread()

cv2.createTrackbar('Scan (ms)', 'ArenaControlPanel', Arena.dm.timeout, 1000, Arena.dm.setTimeout)
#cv2.createTrackbar('Threshold0', 'ArenaControlPanel', Arena.zone[0].threshold, 255, Arena.zone[0].setThreshold)
cv2.setMouseCallback("ArenaControlPanel", Arena.ui.onMouse, Arena)

###############
## LOOP
###############
while True:
    if Arena.allFound():
        Arena.targettedScan()
    else:
        Arena.deepScan()
    outputImg = Arena.render() 
    
    controlPanelImg = Arena.ui.drawControlPanel(Arena)

    # Display the image or frame of video
    if size(outputImg,0) > 0 and size(outputImg,1) > 0:
        outputImg = Arena.ui.resize(outputImg)
        cv2.imshow("ArenaScanner", outputImg)
    
    # Display the control panel
    cv2.imshow("ArenaControlPanel", controlPanelImg)

    # Create a blank output image for the projector.
    projectorimage = zeros((570,800,3), uint8)
    projectorimage[:,:] = (254,254,254)

    pih = projectorimage.shape[0]
    piw = projectorimage.shape[1]

    # Import the corner images
    corner = cv2.imread("images/C0.png")
    ch = corner.shape[0]
    cw = corner.shape[1]
    yoffset = pih - ch
    xoffset = 0
    projectorimage[yoffset:(ch+yoffset),xoffset:(cw+xoffset)] = corner

    corner = cv2.imread("images/C1.png")
    yoffset = pih - ch
    xoffset = piw - cw
    projectorimage[yoffset:(ch+yoffset),xoffset:(cw+xoffset)] = corner

    corner = cv2.imread("images/C2.png")
    yoffset = 0
    xoffset = piw - cw
    projectorimage[yoffset:(ch+yoffset),xoffset:(cw+xoffset)] = corner
    
    corner = cv2.imread("images/C3.png")
    yoffset = 0
    xoffset = 0
    projectorimage[yoffset:(ch+yoffset),xoffset:(cw+xoffset)] = corner

    # Translate the position from the camera to a position for the projector.

    # Display the projector
    cv2.imshow("ArenaProjector", projectorimage)

    Arena.ui.calcFPS()

    #Exit
    if Arena.ui.exit: 
        break
      
###############
## END LOOP
###############
for z in Arena.zone:
    z.close()
cv2.destroyAllWindows()

print "Exiting."



