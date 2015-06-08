#! /usr/bin/python

import time
import os
import glob
import collections
import shutil
import re
import subprocess
import threading
import time
import psutil
		
SIMULATION_DIR=os.getcwd()

SIMULATION_RUNS = 10
SIMULATION_OUTPUT = SIMULATION_DIR + "/output/"


maxNumThreads = 5
curNumThreads = 0



class Thread(threading.Thread):
	def __init__(self,job_number,sys_cal, output):
		super(Thread,self).__init__()
		self.sysCall = sys_cal
		self.jobNumber = job_number
		self.outputStr = output

	def run(self):
		global curNumThreads
		print "starting job number ", self.jobNumber
		print "command is: ", self.sysCall
		fpOut = open(self.outputStr, "w")

		start = time.time()

                proc = subprocess.Popen(self.sysCall, stdout=fpOut,stderr=fpOut) 
		# proc.communicate() # wait until finished
		proc.communicate()

		# sleep 0.5 seconds to be sure the OS really has finished the process
		time.sleep(0.5)
		end = time.time()
		calculatedTime = end - start
		fpOut.close()
		print "ending job number ", self.jobNumber, " after ", calculatedTime, " seconds"

		curNumThreads -= 1
# end class


processPool = []


SCENARIOS = {
# DASH
#"CongAvoid_DASH_6M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck6.top", "--cwnd=tcp"] },
#"CongAvoid_DASH_9M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck9.top", "--cwnd=tcp"] },
#"CongAvoid_DASH_12M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--#top=congavoid_100clients_bottleneck12.top", "--cwnd=tcp"] },
#"CongAvoid_DASH_15M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck15.top", "--cwnd=tcp"] },
#"CongAvoid_DASH_18M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck18.top", "--cwnd=tcp"] },
#	"CongAvoid_DASH_20M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck20.top", "--cwnd=tcp"] },
#	"CongAvoid_DASH_20M_STATIC":  { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck20.top", "--cwnd=static"] },
#	"CongAvoid_DASH_25M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck25.top", "--cwnd=tcp"] },
#	"CongAvoid_DASH_25M_STATIC":  { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck25.top", "--cwnd=static"] },
#	"CongAvoid_DASH_30M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck30.top", "--cwnd=tcp"] },
#	"CongAvoid_DASH_30M_STATIC":  { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck30.top", "--cwnd=static"] },
#	"CongAvoid_DASH_35M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck35.top", "--cwnd=tcp"] },
#	"CongAvoid_DASH_35M_STATIC":  { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck35.top", "--cwnd=static"] },
#	"CongAvoid_DASH_40M_CWND":    { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck40.top", "--cwnd=tcp"] },
#	"CongAvoid_DASH_40M_STATIC":  { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [dashStr, "--top=congavoid_100clients_bottleneck40.top", "--cwnd=static"] },
# INA
#"CongAvoid_INA_6M_CWND":     { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck6.top", "--cwnd=tcp"] },
#"CongAvoid_INA_9M_CWND":     { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck9.top", "--cwnd=tcp"] },
#"CongAvoid_INA_12M_CWND":     { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck12.top", "--cwnd=tcp"] },
#"CongAvoid_INA_15M_CWND":     { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck15.top", "--cwnd=tcp"] },
#	"CongAvoid_INA_18M_CWND":     { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck18.top", "--cwnd=tcp"] },
#	"CongAvoid_INA_20M_STATIC":   { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck20.top", "--cwnd=static"] },
#	"CongAvoid_INA_25M_CWND":     { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck25.top", "--cwnd=tcp"] },
#	"CongAvoid_INA_25M_STATIC":   { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck25.top", "--cwnd=static"] },
#	"CongAvoid_INA_30M_CWND":     { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck30.top", "--cwnd=tcp"] },
#	"CongAvoid_INA_30M_STATIC":   { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck30.top", "--cwnd=static"] },
#	"CongAvoid_INA_35M_CWND":     { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck35.top", "--cwnd=tcp"] },
#	"CongAvoid_INA_35M_STATIC":   { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck35.top","--cwnd=static"] },
#	"CongAvoid_INA_40M_CWND":     { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck40.top","--cwnd=tcp"] },
#	"CongAvoid_INA_40M_STATIC":   { "executeable": "congavoid", "numRuns": SIMULATION_RUNS, "params": [adapStr, "--top=congavoid_100clients_bottleneck40.top","--cwnd=static"] },
}


cachingStrategies = ["nocache", "LRU", "LFU", "FIFO"]
forwardingStrategies = ["bestroute", "broadcast", "NCC"]
cacheSizes = [100, 1000, 10000]



# generate scenarios
for cs in cachingStrategies:
	for fw in forwardingStrategies:
		if cs != "nocache":
			for cSize in cacheSizes:
				 SCENARIOS["brite_" + cs + "_" + fw + "_" + str(cSize)] = { "executeable": "ndn-brite-scenario", "numRuns": SIMULATION_RUNS,
						"params": ["--fwStrategy=" + fw, "--csStrategy=" + cs, "--cacheEntries=" + str(cSize)] }
		else:
			SCENARIOS["brite_" + cs + "_" + fw] = { "executeable": "ndn-brite-scenario", "numRuns": SIMULATION_RUNS,
						"params": ["--fwStrategy=" + fw, "--csStrategy=" + cs] }


#./waf --run "ndn-brite-scenario --fwStrategy=NCC --csStrategy=nocache --cacheEntries=1000"



#build project before
subprocess.Popen("./waf", shell=True)
###script start
print "\nCurring working dir = " + SIMULATION_DIR + "\n"


jobNumber = 0

stopSimulations = False

for scenarioName in SCENARIOS.keys():
	if stopSimulations:
		continue
	# end if
	runs = SCENARIOS[scenarioName]['numRuns']
	executeable = SCENARIOS[scenarioName]['executeable']
	
	executeable = ["./waf"] # , "--run \"" + executeable]
	print "------------------------------------------------------------------------"
	print "Starting", runs , "simulations of", scenarioName
	
	for i in range(0, runs):
		# check if stop.txt exists
		if os.path.isfile("stop.txt"):
			print "STOP FILE FOUND, NO MORE SIMULATIONS WILL BE STARTED!"
			stopSimulations = True
			continue
		# end if
 
		print "----------"
		print "Simulation run " + str(i) + " in progress..." 
		outputFolder = "output/" + scenarioName + "_" + str(i)
		if os.path.exists(outputFolder):
			continue

		os.makedirs(outputFolder)
		tmp = SCENARIOS[scenarioName]['params'] + ["--RngRun=" + str(i)] + ["--outputFolder=" + outputFolder] 
		commandLine =  " ".join(tmp) 
		executeable = [SIMULATION_DIR+ "/waf"] + ["--run"] + [ SCENARIOS[scenarioName]['executeable'] + " " + commandLine] 

		myThread = Thread(jobNumber, executeable, outputFolder + "/stdout.txt")
		myThread.start()
		time.sleep(1)
		
		jobNumber += 1
		curNumThreads += 1
		while curNumThreads >= maxNumThreads:
			time.sleep(5)
		# check memory usage
		while psutil.phymem_usage().free / 1024 / 1024 < 3000: # do not start any new jobs when there is less than 3 GB memory available
			time.sleep(10)
		# end while
		print "Free Memory: ", psutil.phymem_usage().free / 1024 / 1024 , " MegaByte"
	# end for
	# end for
	
# end for



print "Waiting for " , curNumThreads, " threads to finish..."
while curNumThreads > 0:
	time.sleep(20)

print "Finished."
exit();





