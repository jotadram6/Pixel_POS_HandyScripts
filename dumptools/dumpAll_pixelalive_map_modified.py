#!/bin/python

import sys, os
import commands as cmd
PWD = cmd.getoutput('pwd')
sys.path.append(os.path.join(PWD,"common/"))
from JMTTools import *
from JMTROOTTools import *

run_dir = run_dir_from_argv()

in_fn = glob(os.path.join(run_dir, 'PixelAlive_Fed*.root'))
if not in_fn:
    raise RuntimeError('Generate root file first!')
if len(in_fn)>1:
    raise RuntimeError('too many root files, check please!')
in_fn = in_fn[0]
f = ROOT.TFile(in_fn)

out_dir = outdir_from_argv()
if out_dir is not None:
    out_dir = os.path.join(out_dir, 'dump_pixelalive')
else:
    out_dir = os.path.join(run_dir, 'dump_pixelalive')
print "Generating output in:", out_dir
if not os.path.isdir(out_dir):
    os.system('mkdir -p -m 777 %s' % out_dir)

pdf_fn = os.path.join(out_dir,'all_map.pdf')
txt_fn = os.path.join(out_dir,'dead_pixels.txt')

if os.path.isfile(txt_fn):
    cmd = 'mv %s %s' %(txt_fn,txt_fn+'.old')
    os.system(cmd)

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
