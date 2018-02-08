import sys, os
from JMTTools import *
from JMTROOTTools import *
import cablemap as cm
from mkDetConfig import mkNewConfigVersion, setAsDefault

run = run_from_argv()
run_dir = run_dir_from_argv()
in_fn = glob(os.path.join(run_dir, 'total.root'))
if not in_fn:
    root_flist = glob(os.path.join(run_dir, 'PixelAlive_Fed_*_Run_%i.root' % run))
    if not root_flist:
        raise RuntimeError('need to run analysis first!')
    out_root = os.path.join(run_dir,'total.root')
    args = ' '.join(root_flist)
    cmd = 'hadd %s %s' %(out_root, args)
    os.system(cmd)
in_fn = glob(os.path.join(run_dir, 'total.root'))
in_fn = in_fn[0]
out_dir = os.path.join(run_dir, 'dump_pixelalive')
if not os.path.isdir(out_dir):
    os.system('mkdir -p -m 777 %s' % out_dir)

f = ROOT.TFile(in_fn)
pdf_fn = os.path.join(out_dir,'all_map.pdf')
txt_fn = os.path.join(out_dir,'dead_pixels.txt')

if os.path.isfile(txt_fn):
    cmd = 'mv %s %s' %(txt_fn,txt_fn+'.old')
    os.system(cmd)

dirs = ['FPix/FPix_%(hc)s/FPix_%(hc)s_D%(dsk)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i' % locals() for hc in ['BmI', 'BmO', 'BpI', 'BpO'] for dsk in range(1,4) for bld in range(1,18) for pnl in range(1,3) for rng in range(1,3)]

DAC_VER = cm.findconfigversions(cm.findkey(run_dir))['mask']
CONFIG_DIR = os.environ['PIXELCONFIGURATIONBASE']
DAC_DIR = os.path.join(CONFIG_DIR,'mask')


def mkHistList(f,d):
    hs = []
    for key in f.Get(d).GetListOfKeys():
        hs.append(key.ReadObj())
    #assert(len(hs)==16)
    return [f.Get(d).GetName(), hs]

def countFromHist(h,thr):
    NDead = 0
    for x in xrange(1,h.GetNbinsX()):
        for y in xrange(1,h.GetNbinsY()):
            val = h.GetBinContent(x,y)
            if val < thr:
                NDead += 1
    return NDead

def countFromHist(hload,hfill):
    NDead = 0
    for x in xrange(1,hload.GetNbinsX()):
        for y in xrange(1,hload.GetNbinsY()):
            val = hload.GetBinContent(x,y)
            if val == 0:
                continue
            hfill.Fill(val)
    return 1

c=None
minThr = 100. #define maxmum value as 100, adjust if hot pixels exist.<F20>

hHotPixelDist = ROOT.TH1F("HotPixelDistribution","",75000,0,15)

dacOld = os.path.join(DAC_DIR,str(DAC_VER))
dacNewVer = str(mkNewConfigVersion('mask'))
dacNew = os.path.join(DAC_DIR, dacNewVer)
os.system('cp -r {0}/* {1}/.'.format(dacOld, dacNew))
 
for d in dirs:
    if not f.Get(d):
        continue
    ns = mkHistList(f,d)
    
    #if 'BmI_D3_BLD1_PNL2_RNG2' in ns[0] or 'BmI_D3_BLD1_PNL2_RNG1' in ns[0]:
    #   print 'skipping BmI_D3_BLD1_PNL2_RNG2'
    #   continue
    for h in ns[1]:
        rocname = h.GetName()
        modulename = rocname[0:rocname.find('_ROC')]
        countFromHist(h,hHotPixelDist)
        roc = rocname
        roc = roc.replace(modulename,"")
        roc = roc.replace("_ROC","")
        roc = int(roc)
        maskfilename = 'ROC_Masks_module_' + modulename + '.dat'
        maskfile = mask_dat(os.path.join(dacNew,maskfilename))
        for x in range(1,h.GetNbinsX()+1):
            for y in range(1,h.GetNbinsY()+1):
                thr = 0.01
                if(h.GetBinContent(x,y))<thr:
                    continue
                print "Hot pixel in ",rocname," col ",x-1," row ",y-1," hit eff ",h.GetBinContent(x,y),"percent"
                maskfile.m[roc][x-1][y-1] = 0
        maskfile.write(os.path.join(dacNew,maskfilename))

hHotPixelDist.SetBinContent(hHotPixelDist.GetNbinsX(),hHotPixelDist.GetBinContent(hHotPixelDist.GetNbinsX())+hHotPixelDist.GetBinContent(hHotPixelDist.GetNbinsX()+1) )
fout_fn = os.path.join(out_dir,'HotPixelsAnalysis.root') 
fout = ROOT.TFile(fout_fn,"RECREATE")
fout.cd()
hHotPixelDist.Write()
fout.Close()

print "Done."
#os.system('cat {0}'.format(txt_fn))
#os.system('evince %s' %pdf_fn)
