import sys, os
from JMTTools import *
from JMTROOTTools import *
import cablemap as cm
from TrimTools import *
from mkDetConfig import mkNewConfigVersion, setAsDefault

run = run_from_argv()
run_dir = run_dir(run)
#run_dir="/data/tif/Run_BmO/Run_1898/"
in_fn = glob(os.path.join(run_dir, 'total.root'))
if not in_fn:
    root_flist = glob(os.path.join(run_dir,'SCurve_Fed_*_Run_%s.root'%run)) 
    if not root_flist:
        raise RuntimeError('need to run analysis first!')
    out_root = os.path.join(run_dir,'total.root')
    args = ' '.join(root_flist)
    cmd = 'hadd %s %s' %(out_root, args)
    os.system(cmd)
in_fn = glob(os.path.join(run_dir, 'total.root'))
in_fn = in_fn[0]
out_dir = os.path.join(run_dir,'dump_scurve')
if not os.path.isdir(out_dir):
    os.system('mkdir -p -m 766 %s' %out_dir)

helpInfo = '''
            Usage: >python AnalyzeSCurveForTrimBits.py <run> <threshold>\n
            if no mean given, use threshold mean'''


DAC_VER = cm.findconfigversions(cm.findkey(run_dir))['trim']
CONFIG_DIR = os.environ['PIXELCONFIGURATIONBASE']
DAC_DIR = os.path.join(CONFIG_DIR,'trim')

print DAC_DIR,DAC_VER

f = ROOT.TFile(in_fn)
#out_fn = os.path.join(out_dir,'NumOfDeadPixels.txt')
#
#if os.path.isfile(out_fn):
#    cmd = 'mv %s %s' %(out_fn,out_fn+'.old')
#    os.system(cmd)

dirs = ['FPix/FPix_%(hc)s/FPix_%(hc)s_D%(dsk)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i' % locals() for hc in ['BmI', 'BmO', 'BpI', 'BpO'] for dsk in range(1,4) for bld in range(1,18) for pnl in range(1,3) for rng in range(1,3)]

#typeList = ['Threshold1D', 'Noise1D', 'Chisquare1D', 'Probability1D',
#            'Threshold2D', 'Noise2D', 'Chisquare2D', 'Probability2D']
typeList = ['Threshold1D','Threshold2D']

def mkHistList(f,d,tp):
    hs = []
    for key in f.Get(d).GetListOfKeys():
        if tp not in key.ReadObj().GetName():
            continue
        hs.append(key.ReadObj())
    assert(len(hs)==16)
    return [f.Get(d).GetName(), hs]
    
minThr = 30.
maxThr = 120.

meanthreshold=35.
if len(sys.argv) >= 3:
    meanthreshold = float(sys.argv[2])
else:
    meanthreshold = f.Get('Summaries/ThresholdOfAllPixels').GetMean()
    print "Mean taken from file",meanthreshold

minThr = meanthreshold - 1.0
maxThr = meanthreshold + 1.0

def main():
    dacOld = os.path.join(DAC_DIR,str(DAC_VER))
    dacNewVer = str(mkNewConfigVersion('trim'))
    dacNew = os.path.join(DAC_DIR, dacNewVer)
    os.system('cp -r {0}/* {1}/.'.format(dacOld, dacNew))

    for d in dirs:
        if not f.Get(d):
            continue
        ns = mkHistList(f,d,typeList[1])
        nshelp = mkHistList(f,d,typeList[0])
        badPixelList = []
        for h in ns[1]:
            name = h.GetName()
            modulename = name[0:name.find('_ROC')]
            rocname = name[0:name.find('_Threshold')]
            rocmean = 0
            for hh in nshelp[1]:
                helpname = hh.GetName()
                helprocname = helpname[0:helpname.find('_Threshold')]
                if rocname == helprocname:
                    rocmean = hh.GetMean()
                    minThr = rocmean - 1.0
                    maxThr = rocmean + 1.0
                    break
            trimfilename = 'ROC_Trims_module_' + modulename + '.dat'
            trimfile = trimdat(os.path.join(dacNew,trimfilename))
            trimfilename2 = trimfile.fn
            trimfilename2 = trimfilename2.replace(dacOld + '/ROC_Trims_module_','')
            trimfilename2 = trimfilename2.replace('.dat','')
            yy=0
            xx=0
            for x in range(1,h.GetNbinsX()+1):
                for y in range(1,h.GetNbinsY()+1):
                    trimbit = int(trimfile.trims_by_roc[rocname][x-1][y-1],16)
                    thr = h.GetBinContent(x,y)
                    changed = 0
                    if thr<1.0:
                        continue
                    if thr<minThr:
                        if trimbit==15:
                            continue
                        trimbit += 1
                        changed = 1
                    if thr>maxThr:
                        if trimbit==0:
                            continue
                        trimbit -= 1
                        changed = 1
                    if changed == 1:
                        trimbit = str(hex(trimbit)[2:]).capitalize()
                        xx = x-1
                        yy = y-1
                        trimfile.trims_by_roc[rocname][x-1] =  trimfile.trims_by_roc[rocname][x-1][:y-1] + trimbit +  trimfile.trims_by_roc[rocname][x-1][y:]
            trimfile.write(os.path.join(dacNew,trimfilename))


    save = raw_input("Do you want to set <trim/{0}> as default?\
                     (y/N)\n".format(dacNewVer))
    if save.lower() in ['n','no']:
        save = False
    elif save.lower() in ['y','yes']:
        save = True
    else:
        raise RuntimeError("Your decision cannot be recognized, however\
                           <trim/{0}> has been written.".format(dacNewVer))
    if save:
        setAsDefault('trim',dacNewVer)

if __name__ == '__main__':
    if len(sys.argv) < 1:
        exit(helpInfo)
    main()

                    
