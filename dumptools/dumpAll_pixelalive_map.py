#!/bin/python

import sys, os
from GetOpsPaths import *

run = run_from_argv()
run_dir = run_dir_from_argv()

f = ROOT.TFile(fetch_root(run_dir, run, ToFetch='total.root', PixelAlive_flag=True))

out_dir = outdir_from_argv()
if out_dir is not None:
    out_dir = os.path.join(out_dir, 'dump_pixelalive')
else:
    out_dir = os.path.join(run_dir, 'dump_pixelalive')
print "Generating output in:", out_dir

if not os.path.isdir(out_dir):
    os.system('mkdir -p -m 777 %s' % out_dir)

pdf_fn = os.path.join(out_dir,'all_map.pdf')
#  pdf_fn = os.path.join(out_dir,'all_map3-6-1-2.pdf')
deadpixels_fn = os.path.join(out_dir,'dead_pixels.txt')
hotpixels_fn = os.path.join(out_dir,'hot_pixels.txt')

for fn in [deadpixels_fn,hotpixels_fn]:
    if os.path.isfile(fn):
        cmd = 'mv %s %s' %(fn,fn+'.old')
        os.system(cmd)

#Replaced by definition of Global Variable
#dirs = ['BPix/BPix_%(hc)s/BPix_%(hc)s_SEC%(sec)i/BPix_%(hc)s_SEC%(sec)i_LYR%(lyr)i/BPix_%(hc)s_SEC%(sec)i_LYR%(lyr)i_LDR%(ldr)iF/BPix_%(hc)s_SEC%(sec)i_LYR%(lyr)i_LDR%(ldr)iF_MOD%(mod)i' % locals() for hc in ['BmI', 'BmO', 'BpI', 'BpO'] for sec in range(1,9) for lyr in range(1,5) for ldr in range(1,21) for mod in range(1,5)]

def mkHistList(f,d):
    hs = []
    for key in f.Get(d).GetListOfKeys():
        hs.append(key.ReadObj())
    
    if "LYR1" in d:
        d=d.replace("F","H")
        for key in f.Get(d).GetListOfKeys():
            hs.append(key.ReadObj())
    #assert(len(hs)==16)
    ordered = []
    for o in range(0,16):
        rocname = 'ROC'+str(o)
        for t in hs:
            if rocname in t.GetName()[-len(rocname):]:
                ordered.append(t)
    hs = ordered
    return [f.Get(d).GetName(), hs]

def countFromHist(h,downThr,upThr):
    NDead = 0
    NHot = 0
    deadList = []
    hotList = []
    for x in xrange(1,h.GetNbinsX()):
        for y in xrange(1,h.GetNbinsY()):
            val = h.GetBinContent(x,y)
            #if val>0:print val
            if val < downThr:
                NDead += 1
                deadList.append((x,y))
            if val > upThr:
                NHot += 1
                hotList.append((x,y))
    return [(NDead,str(deadList)), (NHot,str(hotList))]

c=None
downThr = 100. #define maxmum value as 100, adjust if hot pixels exist.
upThr = 0.01 #define  minimum value to detect hot pixels.

for d in dirs:
    if not f.Get(d):
        continue
    ns = mkHistList(f,d)
    badPixelList = [countFromHist(x,downThr,upThr)[0] for x in ns[1]]
    with open(deadpixels_fn,'a+') as output:
        for i,x in enumerate(badPixelList):
            assert(x[0]>=0),"Number of pixels cannot be negative!"
            ROCname = ns[0]+'{0}{1}'.format('_ROC',i)
            outline = '{0:35}: {1:4} :  {2}\n'.format(ROCname,str(x[0]),x[1])
            output.write(outline)
    hotPixelList = [countFromHist(x,downThr,upThr)[1] for x in ns[1]]
    with open(hotpixels_fn,'a+') as output:
        for i,x in enumerate(hotPixelList):
            assert(x[0]>=0),"Number of pixels cannot be negative!"
            ROCname = ns[0]+'{0}{1}'.format('_ROC',i)
            outline = '{0:35}: {1:4} :  {2}\n'.format(ROCname,str(x[0]),x[1])
            if x[0]>0:
               output.write(outline)
    h,fc,pt = fnal_pixel_plot(ns[1],ns[0].split('/')[-1],ns[0].split('/')[-1],None,existing_c=c)
    if c is None:
        c=fc
        c.SaveAs(pdf_fn+'[')
    c.SaveAs(pdf_fn)
c.SaveAs(pdf_fn+']')

#print '-'*80
#print "<dead_pixels.txt>"
#os.system('cat {0}'.format(deadpixels_fn))
print '-'*80
print "<hot_pixels.txt>"
os.system('cat {0}'.format(hotpixels_fn))
print '-'*80
os.system('evince %s' %pdf_fn)
