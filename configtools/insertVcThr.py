#!/usr/bin/python
import os,sys
import ROOT
from JMTTools import *
from cablemap import findconfigversions, findkey
from mkDetConfig import *

run_dir = run_dir_from_argv()
config='dac'

dacNewVersion = mkNewConfigVersion(config)
configDict = findconfigversions(findkey(run_dir))
dacOldVersion = configDict['dac']
dacOldDir = os.path.join(PIXELCONFIGURATIONBASE,config,str(dacOldVersion))
dacNewDir = os.path.join(PIXELCONFIGURATIONBASE,config,str(dacNewVersion))

dacDatList = glob(os.path.join(run_dir,'ROC_DAC_module_FPix*.dat'))
if len(dacDatList)==0:
    print 'WRONG run number/ NO new config generated!!\n Exit now...'
    os.system('rmdir %s'%dacNewDir)
    sys.exit(0)

cmd1 = 'cp -r %s/* %s/' %(dacOldDir,dacNewDir)
cmd2 = 'cp %s %s' %(os.path.join(run_dir,'ROC_DAC_module_FPix*.dat'),dacNewDir)
os.system(cmd1)
os.system(cmd2)

in_fn = os.path.join(run_dir, 'VcThrCalDel_1.root')
if not os.path.isfile(in_fn):
    raise RuntimeError('no file at %s' %in_fn)

f = ROOT.TFile(in_fn)

dirs = ['FPix/FPix_%(hc)s/FPix_%(hc)s_D%(dsk)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i' % locals() for hc in ['BmI', 'BmO', 'BpI', 'BpO'] for dsk in range(1,4) for bld in range(1,18) for pnl in range(1,3) for rng in range(1,3)]

for d in dirs:
    if not f.Get(d):
        continue
    
    dacfn = os.path.join(run_dir,'ROC_DAC_module_'+d.split('/')[-1]+'.dat')
    dacfile = dac_dat(dacfn)
    for ikey, key in enumerate(f.Get(d).GetListOfKeys()):
        canvas = key.ReadObj()
        name = canvas.GetName().replace(' (inv)', '').replace('_Canvas', '')
        obj = canvas.FindObject(name)
        newY = obj.GetYaxis().GetXmax()-30
        xBinSize = obj.GetXaxis().GetBinWidth(0)
        yBinSize = obj.GetYaxis().GetBinWidth(0)

        for x in canvas.GetListOfPrimitives():
            if x.GetName() == 'TLine':
                if x.GetLineColor() == 0:
                    newX = x.GetX1()
                if x.GetLineColor() == 38:
                    if x.GetX1() == x.GetX2():
                        oldX = x.GetX1()
                    if x.GetY1() == x.GetY2():
                        oldY = x.GetY1()
        val = obj.GetBinContent(int(newX/xBinSize), int(newY/yBinSize))
        dacfile.dacs_by_roc[name]['VcThr'] = int(newY)
        print '{0:34}{1:14} -> {2:14} {3:}'.format(name,(oldX,oldY),(newX,newY),val)
    dacfile.write(dacNewVersion)

save = raw_input("Do you want to set new version <%s/%d> as default? (y/N)?\n"%(config,dacNewVersion))

if save.lower() in ['n','no']:
    save = False
elif save.lower() in ['y','yes']:
    save = True
            
if save:
    setAsDefault(config,dacNewVersion)
