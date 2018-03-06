#!/bin/python

from GetOpsPaths import *
import argparse
import threading
import multiprocessing
from glob import glob

run_dir = run_dir(args.run)
root_flist = glob(os.path.join(run_dir, 'SCurve_Fed_*_Run_%i.root' % args.run))
FEDlist = [x.split('_')[2] for x in root_flist]

TriDasExe='~/TriDAS_r63/pixel/PixelAnalysisTools/test/bin/linux/x86_64_centos7/PixelAnalysis.exe'
TriDasConfDir='~/TriDAS_r63/pixel/PixelAnalysisTools/test/configuration/'

def RunAna(xml):
    AnaOut=cmd.getoutput(TriDasExe+' '+TriDasConfDir+xml+' '+args.run)
    print AnaOut

ListOfXML=['SCurveAnalysis_1296.xml',
           'SCurveAnalysis_1297.xml',
           'SCurveAnalysis_1298.xml',
           'SCurveAnalysis_1299.xml',
           'SCurveAnalysis_1300.xml',
           'SCurveAnalysis_1301.xml',
           'SCurveAnalysis_1302.xml',
           'SCurveAnalysis_1308.xml',
           'SCurveAnalysis_1309.xml',
           'SCurveAnalysis_1310.xml',
           'SCurveAnalysis_1311.xml',
           'SCurveAnalysis_1312.xml',
           'SCurveAnalysis_1313.xml',
           'SCurveAnalysis_1314.xml',
           'SCurveAnalysis_1320.xml',
           'SCurveAnalysis_1321.xml',
           'SCurveAnalysis_1322.xml',
           'SCurveAnalysis_1323.xml',
           'SCurveAnalysis_1324.xml',
           'SCurveAnalysis_1325.xml',
           'SCurveAnalysis_1326.xml',
           'SCurveAnalysis_1332.xml',
           'SCurveAnalysis_1333.xml',
           'SCurveAnalysis_1334.xml',
           'SCurveAnalysis_1335.xml',
           'SCurveAnalysis_1336.xml',
           'SCurveAnalysis_1337.xml',
           'SCurveAnalysis_1338.xml']

ListOfXMLToRun=[x for x in ListOfXML if x.split('_')[-1].split('.')[0] in FEDlist]

cpus=multiprocessing.cpu_count()

print "I have detected ", cpus, " cpus, and will launch as many jobs in parallel"

JobsDoneCounter=0

while JobsDoneCounter<len(ListOfXML):
    if JobsDoneCounter+cpus>len(ListOfXMLToRun):
        MaxCpusToUse=len(ListOfXMLToRun)-JobsDoneCounter
    else: MaxCpusToUse=cpus

    thread_list = []
    for i in range(1, MaxCpusToUse+1):
        # Instantiates the thread
        # (i) does not make a sequence, so (i,)
        t = threading.Thread(target=RunAna, args=(ListOfXMLToRun[i-1+JobsDoneCounter],))
        # Sticks the thread in a list so that it remains accessible
        thread_list.append(t)

    # Starts threads
    for thread in thread_list:
        thread.start()

    # This blocks the calling thread until the thread whose join() method is called is terminated.
    # From http://docs.python.org/2/library/threading.html#thread-objects
    for thread in thread_list:
        thread.join()

    JobsDoneCounter=JobsDoneCounter+cpus

# Demonstrates that the main process waited for threads to complete
print "Done"
