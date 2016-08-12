# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import multiprocessing as mp
import Queue

import dm

class ProcessManager:
    def __init__(self):
        self.resultsque = mp.Queue() # Queue of scanning results
        self.maxprocesses = mp.cpu_count()
        self.procpool = []  # Pool of processes
        self.dataque = mp.Queue() # Data waiting to be processed.
        return

    def scanSubprocess(self, timestamp, timeout, image, offsetx, offsety, resultsque):
        dmscanner = dm.DM(1, timeout)
        dmscanner.scan(image, offsetx = offsetx, offsety = offsety)
        resultsque.put([timestamp, dmscanner.symbols])
        resultsque.close()
        return

    def removeFinished(self):
        # Remove finished processes from the pool.
        for p in self.procpool:
            if not p.is_alive():
                self.procpool.remove(p)
        return


    def addProcess(self, timestamp, timeout, image, xoffset = 0, yoffset = 0):
        # Add process to the pool
        if len(self.procpool) < self.maxprocesses:
            p = mp.Process(target=self.scanSubprocess, args=(timestamp, timeout, image, xoffset, yoffset, self.resultsque))
            p.start()
            self.procpool.append(p)
            return True
        else:
            # Pool is full.
            pass
        return False


    def results(self):
        return not self.resultsque.empty()


    def getResult(self):
        try:
            r = self.resultsque.get(False)
        except Queue.Empty:
            print "no results in queue."
            r = []
        return r
