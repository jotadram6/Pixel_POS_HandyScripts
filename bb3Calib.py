import os,sys
from JMTTools import *

run_num = run_from_argv()

cwd=os.getcwd()
run_dir = os.path.join(POS_OUTPUT_DIRS,'Run_0','Run_%d'%run_num)

os.chdir(run_dir)
os.system("cp -n calib.dat calib.dat.real")
os.system("sed -i.bak -e 's/VcThr/Vcal/' -e '/Set: Vcal 200/d' calib.dat")
os.chdir(cwd)
