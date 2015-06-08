__author__ = 'ckreuz'


import psutil as ps
import os
import sys
import time
import threading
import requests

from jobThread import JobThread




class CloudSchedulerThread(threading.Thread):
    def __init__(self, webserviceUrl, nodeId, maxNumJobs):
        threading.Thread.__init__(self)
        self.ws = webserviceUrl
        self.nodeId = nodeId
        self.running = True
        self.maxNumJobs = maxNumJobs
        self.currentlyRunningJobs = 0
        self.jobList = []
        self.incrementingNumber = 0

        # check if output directory exists
        if not os.path.exists("./output"):
            os.makedirs("./output")

    def run(self):
        while self.running:
            if self.currentlyRunningJobs < self.maxNumJobs:
                nextJob = self.getNextJob()

                if nextJob != None and nextJob != {}:
                    self.jobList.append(nextJob)
                    self.currentlyRunningJobs += 1
                    self.startJob(nextJob)
                    self.incrementingNumber += 1
            time.sleep(20)
        # end while
    # end method

    def calculateAvailableMemory(self): # in megabyte
        neededMemory = 0
        for job in self.jobList:
            neededMemory += job['neededMemory']
        # end for
        availPhymem = ps.TOTAL_PHYMEM / 1024 / 1024

        return availPhymem - neededMemory

    def getNextJob(self):
        availableMemory = self.calculateAvailableMemory()
        print "Requesting another job, availableMemory = ", availableMemory
        payload = {'requestJob': 1, 'nodeId': self.nodeId, 'availableMemory': availableMemory} # in megabyte
        try:
            r = requests.get(self.ws, params=payload)
            # TODO: parse r.content
            return r.json()
        except:
            print "error getting job from webservice..."
            return None
        # done
    # end method

    def reportJobFinished(self, job, timeNeeded, gzipOutputFile):
        job_id = job['jobId']
        print "Job finished:", job_id, ", outputFile=", gzipOutputFile
        self.currentlyRunningJobs -= 1

        payload = {'jobFinished': job_id, 'nodeId': self.nodeId }

        r = requests.get(self.ws, params=payload)

        # upload stdout file
        payload = {'uploadJobOutput': job_id}
        files = {'file': open(gzipOutputFile, 'rb') }

        r = requests.post(self.ws, params=payload, files=files)
        # print r.content
        # done?

    def startJob(self, job):
        outputFileName = "output/" + str(self.incrementingNumber) + "_" + str(job["jobId"]) + "_stdout.txt" # get a temporary directory filename
        jobthread = JobThread(job, outputFileName, self.reportJobFinished)
        jobthread.start()


    def reportJobMemoryConsumption(self):
        print "memory..."
    # end method

    def stopRunning(self):
        self.running = False

    def getNumberOfRunningJobs(self):
        return self.currentlyRunningJobs
# end class
