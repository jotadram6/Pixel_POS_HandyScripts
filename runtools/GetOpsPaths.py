import commands as cmd
import sys, os

PWD = cmd.getoutput('pwd')
if len(PWD.split('dumptools'))>1:
    PWD=PWD.split('dumptools')[0][:-1]

sys.path.append(os.path.join(PWD,"common/"))

from CommonTools import *

#######################
######ARG PARSER#######
#######################

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('run', help='Run Number')
args = parser.parse_args()
