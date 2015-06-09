__author__ = 'ckreuz'

import os
from evaluateDashOutput import calculateStatsForDASH

rootdir = "./output"

lst = os.listdir(rootdir)
lst.sort()

for dir1 in lst:
    if dir1.endswith(".csv"):
        continue
    try:
        print dir1
        # brite_FIFO_NCC_1000_0 <- remove the last _0, as this is the run number
        runType = dir1[:dir1.rfind("_")]
        #print runType
        if not os.path.isfile(os.path.join(rootdir, dir1 + ".csv")):
            outputFile = open(os.path.join(rootdir, dir1 + ".csv"), "w")
            print "writing outputfile", outputFile
            calculateStatsForDASH(os.path.join(rootdir, dir1, "dash-output.txt"), outputFile)
    except:
        print "Error parsing " + dir1
# TODO: Grab all .csv files and upload them

# end POST PROCESSING
