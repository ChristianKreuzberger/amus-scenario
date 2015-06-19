__author__ = 'ckreuz'

import psutil as ps
import os
import sys
import platform
import time

from statsReporter import StatsReporterThread
from cloudScheduler import CloudSchedulerThread

from evaluateDashOutput import calculateStatsForDASH


# check if stop.txt exists, if so, delete it
if os.path.isfile("stop.txt"):
    print "stop.txt found, deleting..."
    os.remove("stop.txt")
# end if


# main thread: schedule jobs
# secondary thread: report ram + cpu usage to webservice


webserviceUrl = "http://chkr.at/stats/ws.php"
maxNumJobs = ps.NUM_CPUS
maxPhysMem = ps.TOTAL_PHYMEM / 1024 / 1024

nodeName = platform.node() + " " + " ".join(platform.dist())

# nodeName = "UNI-KLU Laptop VBOX Ubuntu, 4G, Single Core"

stats = StatsReporterThread(webserviceUrl, nodeName, 60, maxNumJobs, maxPhysMem)
ret = stats.registerNode()
print "Registered node online as ", ret

print "Starting statistics thread"
stats.start()


cloudScheduler = CloudSchedulerThread(webserviceUrl, stats.getNodeId(), maxNumJobs)

cloudScheduler.start()

running = True

# main loop
while running:
    time.sleep(25)
    # update number of jobs running
    stats.setJobsRunning(cloudScheduler.getNumberOfRunningJobs())

    # check for stop.txt
    if os.path.isfile("stop.txt"):
        print "stop.txt found, exiting..."
        break
    # end if
# end while

cloudScheduler.stopRunning()

print "Waiting for all jobs to finish"
cloudScheduler.join() # wait for cloud scheduler stuff to finish
print "Jobs finished!"






print "Waiting for statistics thread to finish..."
stats.stopRunning()
stats.join()
print "Done!"

