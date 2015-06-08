__author__ = 'Christian Kreuzberger'
__maintainer__ = 'Christian Kreuzberger'
__email__ = 'christian.kreuzberger@itec.aau.at'

import csv
import sys
import numpy as np # sudo apt-get install python-numpy
import os


def calculateStatsForDASH(filename, outputStream=sys.stdout):
    """ Calculates stats for a dash output from amus-ndnSIM, and writes it to outputstream (requires numpy to work)
    :param filename: the input file (csv file, with \t as separator)
    :param outputStream: where to write the output statistics (sys.stdout per default)
    :return: True on Success, else False
    """
    o = outputStream
    csvfile = open(filename, 'rb')
    csvreader = csv.reader(csvfile, delimiter='\t')
    # first row is header
    firstRow = True

    collection = {}
    startupDelay = {}

    for row in csvreader:
        if not firstRow: # ignore first row
            #print row
            timestamp, nodeId, segmentNumber, segmentDuration, segmentRepId, segmentBitrate, stallingTime, \
                segmentDepId = row
            #print timestamp, nodeId

            if not nodeId in collection:
                collection[nodeId] = []
                # save the first delay, this is the startup delay
                startupDelay[nodeId] = stallingTime
            # end if

            collection[nodeId].append({'timestamp': timestamp, 'segmentNumber': segmentNumber,
                                       'stallingTime': stallingTime, 'segmentRepId': segmentRepId,
                                       'segmentBitrate': segmentBitrate})
        firstRow = False

    # end for

    # parse collection and make a summary

    o.write("NodeId\tMinBitrate\tMaxBitrate\tAvgBitrate\tLower95\tUpper95\tLower50\tUpper50\tMedian\tStartupDelay\t" \
        + "StallingTime\tNumStallEvents\tDownloadedSegments\n")

    for nodeId in collection:
        sumStalls = 0
        sumBitrates = 0
        numberStallEvents = 0
        minBitrate = sys.maxint
        maxBitrate = 0
        bitrates = []
        for row in collection[nodeId]:
            bitrate = int(row['segmentBitrate'])
            stallingTime = int(row['stallingTime'])
            bitrates.append(bitrate)

            sumStalls += stallingTime
            sumBitrates += bitrate
            if stallingTime != 0:
                numberStallEvents += 1
            # end if
            if bitrate > maxBitrate:
                maxBitrate = bitrate
            if bitrate < minBitrate:
                minBitrate = bitrate
        # end for
        avgBitrate = float(sumBitrates)/float(len(collection[nodeId]))

        upper95Quantile = np.percentile(bitrates, 97.5)
        lower95Quantile = np.percentile(bitrates, 2.5)
        upper50Quantile = np.percentile(bitrates, 75.0)
        lower50QUantile = np.percentile(bitrates, 25.0)
        medianBitrate   = np.percentile(bitrates, 50.0)

        o.write(str(nodeId) + "\t" + str(minBitrate) + "\t" + str(maxBitrate) + "\t" + str(avgBitrate) + "\t" \
            + str(lower95Quantile) + "\t" + str(upper95Quantile) + "\t" + str(lower50QUantile) + "\t" \
            + str(upper50Quantile) + "\t" + str(medianBitrate) + "\t" + str(startupDelay[nodeId]) + "\t" \
            + str(sumStalls) + "\t"  + str(numberStallEvents) + "\t" + str(len(collection[nodeId])) + "\n")

    return True
# end for


