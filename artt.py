import cv2
from numpy import *

import arena, projector
   
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
    # Scan the arena for symbols.
    if Arena.allFound():
        Arena.targettedScan()
    else:
        Arena.deepScan()

    # Render the output of the arena.
    outputImg = Arena.render() 
    
    # Display the image or frame of video
    if size(outputImg,0) > 0 and size(outputImg,1) > 0:
        outputImg = Arena.ui.resize(outputImg)
        cv2.imshow("ArenaScanner", outputImg)
    
    # Display the control panel
    controlPanelImg = Arena.ui.drawControlPanel(Arena)    
    cv2.imshow("ArenaControlPanel", controlPanelImg)


    proj = projector.Projector(570, 800)

    # Warp the arena to be a Rectangle

    # Translate the position from the camera to a position for the projector.

    # Display the projector
    cv2.imshow("ArenaProjector", proj.outputimg)


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


