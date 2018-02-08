import sys, os
from JMTTools import *
from JMTROOTTools import *

run_dir = run_dir_from_argv()
in_fn = glob(os.path.join(run_dir, 'PixelAlive_Fed*.root'))
if not in_fn:
    raise RuntimeError('Generate root file first!')
if len(in_fn)>1:
    raise RuntimeError('too many root files, check please!')
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


def mkHistList(f,d):
    hs = []
    for key in f.Get(d).GetListOfKeys():
        hs.append(key.ReadObj())
    assert(len(hs)==16)
    return [f.Get(d).GetName(), hs]

def countFromHist(h,thr):
    NDead = 0
    for x in xrange(1,h.GetNbinsX()):
        for y in xrange(1,h.GetNbinsY()):
            val = h.GetBinContent(x,y)
            if val < thr:
                NDead += 1
    return NDead

c=None
minThr = 100. #define maxmum value as 100, adjust if hot pixels exist.<F20>

for d in dirs:
    if not f.Get(d):
        continue
    ns = mkHistList(f,d)
    badPixelList = [countFromHist(x,minThr) for x in ns[1]]
    with open(txt_fn,'a+') as output:
        for i,x in enumerate(badPixelList):
            assert(x>=0),"Number of pixels cannot be negative!"
            ROCname = ns[0]+'{0}{1}'.format('_ROC',i)
            outline = '{0:36}{1}\n'.format(ROCname,x)
            output.write(outline)
    h,fc,pt = fnal_pixel_plot(ns[1],ns[0].split('/')[-1],ns[0].split('/')[-1],None,existing_c=c)
    if c is None:
        c=fc
        c.SaveAs(pdf_fn+'[')
    c.SaveAs(pdf_fn)
c.SaveAs(pdf_fn+']')

os.system('cat {0}'.format(txt_fn))
os.system('evince %s' %pdf_fn)
