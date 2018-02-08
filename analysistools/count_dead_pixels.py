import sys, os
from JMTTools import *
from JMTROOTTools import *

run = run_from_argv()
run_dir = run_dir(run)
in_fn = glob(os.path.join(run_dir, 'SCurve_Fed*.root'))
if not in_fn:
    raise RuntimeError('Generate root file first!')
if len(in_fn)>1:
    raise RuntimeError('too many root files, check please!')
in_fn = in_fn[0]
out_dir = os.path.join(run_dir, 'dump_bb3')
if not os.path.isdir(out_dir):
    os.system('mkdir -p %s' % out_dir)

f = ROOT.TFile(in_fn)
out_fn = os.path.join(out_dir,'NumOfDeadPixels.txt')

if os.path.isfile(out_fn):
    cmd = 'mv %s %s' %(out_fn,out_fn+'.old')
    os.system(cmd)

dirs = ['FPix/FPix_%(hc)s/FPix_%(hc)s_D%(dsk)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i' % locals() for hc in ['BmI', 'BmO', 'BpI', 'BpO'] for dsk in range(1,4) for bld in range(1,18) for pnl in range(1,3) for rng in range(1,3)]

typeList = ['Threshold1D', 'Noise1D', 'Chisquare1D', 'Probability1D',
            'Threshold2D', 'Noise2D', 'Chisquare2D', 'Probability2D']

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

for d in dirs:
    if not f.Get(d):
        continue
    ns = mkHistList(f,d,typeList[4])
    badPixelList = []
    for h in ns[1]:
        NBadPixel = 0
        for x in range(1,h.GetNbinsX()):
            for y in range(1,h.GetNbinsY()):
                thr = h.GetBinContent(x,y)
                if thr<minThr or thr>maxThr:
                    NBadPixel += 1
        badPixelList.append(NBadPixel)
    outline = ns[0]+'\t'+str(sum(badPixelList))+'\t'+str(badPixelList)+'\n'
    with open(out_fn,'a+') as output:
        output.write(outline)

os.system('cat %s' %out_fn)
