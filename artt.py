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

    ###############
    ## LOOP
    ###############
    while True:
        # Scan the arena for symbols.
        Arena.scan()

        # Render the output of the arena.
        outputimg = Arena.render()

        # Display the image or frame of video
        if np.size(outputimg,0) > 0 and np.size(outputimg,1) > 0:
            outputimg = Arena.ui.resize(outputimg)
            cv2.imshow("ArenaScanner", outputimg)

        # Display the control panel
        controlPanelImg = Arena.ui.drawControlPanel(Arena)
        cv2.imshow("ArenaControlPanel", controlPanelImg)

        for z in Arena.zones:
            # Display the projector
            cv2.imshow("ZoneProjector"+str(z.id), z.projector.outputimg)

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



