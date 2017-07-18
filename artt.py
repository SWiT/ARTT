import cv2
import numpy as np

import arena

if __name__ == '__main__':
    ###############
    ## SETUP
    ###############
    print "SWiT's Augmented Reality Table Top";
    print "**********************************";
    cv2.namedWindow("ArenaScanner")
    cv2.namedWindow("ArenaControlPanel")
    cv2.startWindowThread()

    Arena = arena.Arena() # Initialize the arena.

    cv2.setMouseCallback("ArenaControlPanel", Arena.ui.onMouse, Arena)

    cv2.createTrackbar('bgcolor','ArenaControlPanel', 127, 255, Arena.ui.updateBGColor)

    ###############
    ## LOOP
    ###############
    while True:
        # Scan the arena for symbols.
        Arena.scan()

        # Render the output of the arena scanning.
        image = Arena.render()
        if np.size(image,0) > 0 and np.size(image,1) > 0:
            image = Arena.ui.resize(image)
            cv2.imshow("ArenaScanner", image)

        # Display the control panel
        controlPanelImg = Arena.ui.drawControlPanel(Arena)
        cv2.imshow("ArenaControlPanel", controlPanelImg)

        # Display the projectors
        for z in Arena.zones:
            cv2.imshow("ZoneProjector"+str(z.id), z.projector.image)

        Arena.ui.calcFPS()

        #Exit
        if Arena.ui.exit:
            break

    ###############
    ## END LOOP
    ###############
    for z in Arena.zones:
        z.close()
    cv2.destroyAllWindows()

    print "Exiting."



