#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

import ROOT
import JMTTools as jt
import cablemap as cm

for i, arg in enumerate(sys.argv):
    if(arg[0]=='-') and arg[1].isdigit():
        sys.argv[i] = ' '+arg

from mkDetConfig import mkNewConfigVersion, setAsDefault

RUN_DIR = jt.run_dir(int(sys.argv[1]))
DAC_VER = cm.findconfigversions(cm.findkey(RUN_DIR))['dac']
CONFIG_DIR = os.environ['PIXELCONFIGURATIONBASE']
DAC_DIR = os.path.join(CONFIG_DIR,'dac')

DACS = ['Vdd', 'Vana', 'Vsh', 'Vcomp', 'VwllPr', 'VwllSh', 'VHldDel',\
        'Vtrim', 'VcThr', 'VIbias_bus', 'PHOffset', 'Vcomp_ADC','PHScale',\
        'VIColOr', 'Vcal', 'CalDel', 'TempRange', 'WBC', 'ChipContReg',\
        'Readback']

helpInfo = '''
            Usage: >python modifyDacByHand.py <run> <mode> <dac> <val>\n
            <mode>: rel/abs\n
            <dac>: '''+str(DACS)

if sys.argv[2].lower() not in ['rel','abs']:
    sys.exit('Wrong mode set!\n'+helpInfo)
else:
    MODE = sys.argv[2].lower()

if sys.argv[3] not in DACS:
    sys.exit('Wrong dac set!\n'+helpInfo)
else:
    FLAG = sys.argv[3]

try:
    val = sys.argv[4]
    PARAM = float(val) if '.' in val else int(val)
except:
    sys.exit('Wrong type for val, only int or float allowed!')

def main():
    dacOld = os.path.join(DAC_DIR,str(DAC_VER))
    dacNewVer = str(mkNewConfigVersion('dac'))
    dacNew = os.path.join(DAC_DIR, dacNewVer)

    for x in os.listdir(dacOld):
        if '.dat' not in x:
           continue
        print x
        print dacOld
        dacfile = jt.dac_dat(os.path.join(dacOld,x))
        for n in xrange(16):
            rocName = x.replace('.dat','').replace('ROC_DAC_module_','')+'_ROC'+str(n)
            if MODE == 'rel':
                dacfile.dacs_by_roc[rocName][FLAG] +=\
                    round(dacfile.dacs_by_roc[rocName][FLAG]*PARAM)
            elif MODE =='abs':
                dacfile.dacs_by_roc[rocName][FLAG] = PARAM

        dacfile.write(os.path.join(dacNew,x))

    msg = "<dac/{0}>:".format(DAC_VER)+FLAG
    msg += ' '.join([' +(',str(PARAM),')']) if MODE =='abs' else\
           ' '.join([' *',str(PARAM)])
    msg += " --> <dac/{0}>".format(dacNewVer)
    print msg

    save = raw_input("Do you want to set <dac/{0}> as default?\
                     (y/N)\n".format(dacNewVer))
    if save.lower() in ['n','no']:
        save = False
    elif save.lower() in ['y','yes']:
        save = True
    else:
        raise RuntimeError("Your decision cannot be recognized, however\
                           <dac/{0}> has been written.".format(dacNewVer))
    if save:
        setAsDefault('dac',dacNewVer)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        exit(helpInfo)
    main()
