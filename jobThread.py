__author__ = 'ckreuz'



import time
import threading
import subprocess
import gzip




class JobThread(threading.Thread):
    def __init__(self, job, outputFile, callback):
        threading.Thread.__init__(self)
        self.job = job
        self.callback = callback
        self.active = False
        self.finished = False
        self.outputFile = outputFile

    def run(self):
        print "starting job with id ", self.job['jobId'], ", commandline:"
        print self.job['commandLine']

        self.startTime = time.time()
        fpout = open(self.outputFile, "w")
        self.active = True

        proc = subprocess.Popen(self.job['commandLine'], stdout=fpout, stderr=fpout)
        proc.communicate()

        print "Finished job with id ", self.job['jobId'],

        self.stopTime = time.time()

        time.sleep(0.5)
        self.active = False
        self.finished = True

        fpout.close()

        # gzip output
        fpin = open(self.outputFile, 'rb')
        fpout = gzip.open(self.outputFile + ".gz", 'wb')
        fpout.writelines(fpin)
        fpout.close()
        fpin.close()


        self.callback(self.job, self.stopTime - self.startTime, self.outputFile + ".gz")
    # end method

# end class