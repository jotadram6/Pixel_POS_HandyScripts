#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

import ROOT
from JMTTools import *
from mkDetConfig import mkNewConfigVersion

CONFIG_DIR = os.environ['PIXELCONFIGURATIONBASE']
DAC_DIR = os.path.join(CONFIG_DIR,'dac')
DAC_DIR_OLD = os.path.join(DAC_DIR,sys.argv[1])
DAC_DIR_NEW = os.path.join(DAC_DIR,sys.argv[2])
DAC_DIR_RESULT = os.path.join(DAC_DIR,str(mkNewConfigVersion('dac')))

DACS = ['Vdd', 'Vana', 'Vsh', 'Vcomp', 'VwllPr', 'VwllSh', 'VHldDel',\
        'Vtrim', 'VcThr', 'VIbias_bus', 'PHOffset', 'Vcomp_ADC','PHScale',\
        'VIColOr', 'Vcal', 'CalDel', 'TempRange', 'WBC', 'ChipContReg',\
        'Readback']
FLAG = sys.argv[3]
if FLAG not in DACS:
    sys.exit("WRONG dac choosen! Tell me one more time")

def getFileOnlyInA(dirA,dirB):
    fileListA = os.listdir(dirA)
    fileListB = os.listdir(dirB)
    inAOnly = []
    for x in fileListA:
        if x in fileListB:
            continue
        inAOnly.append(x)
    return inAOnly

def moveDac(fromRun,toRun,filelist):
    for x in filelist:
        cmd = 'cp %s %s'\
        %(os.path.join(DAC_DIR,fromRun,x),os.path.join(DAC_DIR,toRun))
        os.system(cmd)

def main():
    modulesOnlyInOld = getFileOnlyInA(DAC_DIR_OLD,DAC_DIR_NEW)
    modulesOnlyInNew = getFileOnlyInA(DAC_DIR_NEW, DAC_DIR_OLD)
    moveDac(DAC_DIR_OLD,DAC_DIR_RESULT,modulesOnlyInOld)
    modulesInBoth    = getFileOnlyInA(DAC_DIR_OLD,DAC_DIR_RESULT)
    moveDac(DAC_DIR_NEW,DAC_DIR_RESULT,modulesOnlyInNew)

    for x in modulesInBoth:
        dacfile_old = dac_dat(os.path.join(DAC_DIR_OLD,x))
        dacfile_new = dac_dat(os.path.join(DAC_DIR_NEW,x))
        for n in xrange(16):
            rocName = x.replace('.dat','').replace('ROC_DAC_module_','')+'_ROC'+str(n)
            dacfile_old.dacs_by_roc[rocName][FLAG] =\
            dacfile_new.dacs_by_roc[rocName][FLAG]
        dacfile_old.write(os.path.join(DAC_DIR_RESULT,x))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        info = "WRONG number of arguments!\ne.g. python checkDacSetting.py\
        <OLD> <NEW> <DAC>"
        sys.exit(info)
    main()
