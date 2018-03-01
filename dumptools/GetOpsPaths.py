import commands as cmd

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
args = parser.parse_args()
