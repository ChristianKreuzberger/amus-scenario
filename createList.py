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


def calculateMemory(cs, fw, csize = 0):
	if cs == "nocache":
		return 700
	else:
		if fw == "NCC":
			if csize == 100:
				return 900
			elif csize == 1000:
				return 1500
			elif csize == 10000:
				return 4100
		else:
			if csize == 100:
				return 800
			elif csize == 1000:
				return 1400
			elif csize == 10000:
				return 4000
	return 4000 # else



cachingStrategies = ["nocache", "LRU", "LFU", "FIFO"]
forwardingStrategies = ["bestroute", "broadcast", "NCC"]
cacheSizes = [100, 1000, 10000]

SCENARIOS = {}


# generate scenarios
for cs in cachingStrategies:
	for fw in forwardingStrategies:
		if cs != "nocache":
			for cSize in cacheSizes:
				 SCENARIOS["brite_" + cs + "_" + fw + "_" + str(cSize)] = { "executeable": "ndn-brite-scenario", "numRuns": SIMULATION_RUNS,
						"params": ["--fwStrategy=" + fw, "--csStrategy=" + cs, "--cacheEntries=" + str(cSize)] , "memoryNeeded": calculateMemory(cs,fw,cSize)  }
		else:
			SCENARIOS["brite_" + cs + "_" + fw] = { "executeable": "ndn-brite-scenario", "numRuns": SIMULATION_RUNS,
						"params": ["--fwStrategy=" + fw, "--csStrategy=" + cs] , "memoryNeeded": calculateMemory(cs,fw)  }



jobNumber = 0

stopSimulations = False

for scenarioName in SCENARIOS.keys():
	runs = SCENARIOS[scenarioName]['numRuns']
	executeable = SCENARIOS[scenarioName]['executeable']
	
	executeable = ["./waf"] # , "--run \"" + executeable]
	
	for i in range(0, runs):
		outputFolder = "output/" + scenarioName + "_" + str(i)
		if os.path.exists(outputFolder):
			continue

		#os.makedirs(outputFolder)
		tmp = SCENARIOS[scenarioName]['params'] + ["--RngRun=" + str(i)] + ["--outputFolder=" + outputFolder] 
		commandLine =  " ".join(tmp) 
		executeable = [SIMULATION_DIR+ "/waf"] + ["--run"] + [ SCENARIOS[scenarioName]['executeable'] + " " + commandLine] 
		title = scenarioName + ", Run " + str(i)
		executeableString = "[" + ', '.join('"{0}"'.format(w) for w in executeable) + "]"

		print "INSERT INTO job (title, commandline, registeredby, memory_needed, priority, job_status) VALUES ('" + title + "', '" + executeableString + "', 'ckreuz', " + str(SCENARIOS[scenarioName]['memoryNeeded']) + ", 0, 0);";


# end for






