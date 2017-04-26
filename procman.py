# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import multiprocessing as mp
import Queue
import cv2
import cv2.aruco as aruco

class ProcessManager:
    def __init__(self):
        self.resultsque = mp.Queue() # Queue of scanning results
        self.maxprocesses = mp.cpu_count()
        self.procpool = []  # Pool of processes
        self.dataque = mp.Queue() # Data waiting to be processed.
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.parameters =  aruco.DetectorParameters_create()

    def scanSubprocess(self, timestamp, timeout, image, offsetx, offsety, resultsque):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.corners, self.ids, self.rejectedImgPoints = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)

        resultsque.put([timestamp, self.corners, self.ids, self.rejectedImgPoints])
        resultsque.close()


    def removeFinished(self):
        # Remove finished processes from the pool.
        for p in self.procpool:
            if not p.is_alive():
                self.procpool.remove(p)


    def addProcess(self, timestamp, timeout, image, xoffset = 0, yoffset = 0):
        # Add process to the pool
        if len(self.procpool) < self.maxprocesses:
            p = mp.Process(target=self.scanSubprocess, args=(timestamp, timeout, image, xoffset, yoffset, self.resultsque))
            p.start()
            self.procpool.append(p)
            print "Process launched."
            return True
        else:
            # Pool is full.
            print "Pool is full."
            pass
        return False


    def resultsAvailable(self):
        return not self.resultsque.empty()


    def getResult(self):
        try:
            r = self.resultsque.get(False)
        except Queue.Empty:
            print "no results in queue."
            r = []
        return r
