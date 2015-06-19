__author__ = 'ckreuz'


import os
import sys


rootdir = "./output"


def summarize(simName, lst, outfile=sys.stdout):
    global rootdir

    firstFile = True
    for fileName in lst:
        fp = open(rootdir + "/" + fileName, "r")

        lines = fp.readlines()
        if len(lines) == 0:
            continue
        if firstFile:
            outfile.write("Simulation Name\t" + lines[0])
            firstFile = False
        for line in lines[1:]:
            outfile.write(simName + "\t" + line)

lst = os.listdir(rootdir)
lst.sort()

resultFileList = {}

for csvFile in lst:
    if csvFile.endswith(".csv") and not csvFile.endswith("txt.csv") and not csvFile.endswith("gz.csv"):
        baseFile = csvFile[:csvFile.rfind("_")]
        if baseFile not in resultFileList:
            resultFileList[baseFile] = [csvFile]
        else:
            resultFileList[baseFile].append(csvFile)

print resultFileList.keys()

for simName in resultFileList.keys():
    summarize(simName, resultFileList[simName], open("results/" + simName + ".csv", "w"))


# TODO: Grab all .csv files and upload them

# end POST PROCESSING
