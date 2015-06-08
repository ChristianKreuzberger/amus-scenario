__author__ = 'ckreuz'


import psutil as ps
import os
import sys
import time
import threading
import requests



class StatsReporterThread(threading.Thread):
    def __init__(self, webserviceUrl, nodeName, updateInterval, maxNumJobs, maxPhyMem):
        threading.Thread.__init__(self)
        self.ws = webserviceUrl
        self.waitTime = updateInterval
        self.nodeId = ""
        self.nodeName = nodeName
        self.jobsRunning = 0
        self.running = True
        self.maxNumJobs = maxNumJobs
        self.maxPhyMem = maxPhyMem

    def run(self):
        while self.running:
            # get stats
            cpu_percentage = ps.cpu_percent(1.0)
            memory_usage = ps.phymem_usage().free / 1024 / 1024
            # report to WS
            self.reportToWS(cpu_percentage, memory_usage, time.time())
            # wait for next update
            time.sleep(self.waitTime)
        # end while
    # end method

    def reportToWS(self, cpu_percentage, memory_usage, current_time):
        payload = {'nodeId': self.nodeId, 'cpu': cpu_percentage, 'mem': memory_usage, 'time': current_time, 'jobs': self.jobsRunning}
        try:
            r = requests.get(self.ws, params=payload)
        except:
            # ignore
            print "error reporting stats to webservice..."
        # done
    # end method

    def setJobsRunning(self, numJobs):
        self.jobsRunning = numJobs


    def registerNode(self):
        payload = {'registerNode': self.nodeName, 'maxPhyMem': self.maxPhyMem, 'maxNumJobs': self.maxNumJobs}
        r = None

        try:
            r = requests.get(self.ws, params=payload)
            response = r.content
            self.nodeId = response
        except:
            print "Error registering node on webservice..."
            raise
        return self.nodeId

    def stopRunning(self):
        self.running = False

    def getNodeId(self):
        return self.nodeId

    def getNodeName(self):
        return self.nodeName
# end class