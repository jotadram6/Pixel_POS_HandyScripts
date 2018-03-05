import commands as cmd
import sys, os

PWD = cmd.getoutput('pwd')
if len(PWD.split('dumptools'))>1:
    PWD=PWD.split('dumptools')[0][:-1]

sys.path.append(os.path.join(PWD,"common/"))
sys.path.append(os.path.join(PWD,"configtools/"))

from CommonTools import *
from CommonROOTTools import *

#######################
######ARG PARSER#######
#######################

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('run', help='Run Number')
parser.add_argument('--FED', help='FED number to be used. Not needed in all scripts, just in: dumpAll_scurve.py, dumpAll_bb3.py')
parser.add_argument('--CalDel', help='CalDel root to be used on dumpAll_caldel script')
args = parser.parse_args()
