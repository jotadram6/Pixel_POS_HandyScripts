#!/bin/python

import sys, os
from pprint import pprint
from GetOpsPaths import *
set_style()

run = run_from_argv()
run_dir = run_dir(args.run)

in_fn = os.path.join(run_dir, 'delay25_1.root')
if not os.path.isfile(in_fn):
    raise IOError('no root file %s' % in_fn)
f = ROOT.TFile(in_fn)

out_dir = outdir_from_argv()
if out_dir is not None:
    out_dir = os.path.join(out_dir, 'dump_delay25')
else:
    out_dir = os.path.join(run_dir, 'dump_delay25')
print "Generating output in:", out_dir
os.system('mkdir -p %s' % out_dir)

c = ROOT.TCanvas('c', '', 3500, 1000)
c.Divide(7,2)
c.cd(0)
pdf_fn = os.path.join(out_dir, 'all-12.pdf')
c.Print(pdf_fn + '[')

for d in dirs_short:
    hs={}
    if not f.Get(d):
        continue
    for ikey, key in enumerate(f.Get(d).GetListOfKeys()):
        obj = key.ReadObj()
        name = obj.GetName().replace(';1', '')
        md = name.split(' ')[8]
        if 'command' in md or not md.startswith("FPix"):
            continue
        pc = name.split(' ')[5]
        if pc not in hs.keys():
            hs[pc]=[obj]
        else:
            hs[pc].append(obj)

    prts = sorted(hs.keys())
    for p in prts:
        for i, m in enumerate(hs[p]):
            c.cd(i+1)
            for x in m.GetListOfPrimitives():
                x.Draw()
        c.cd(0)
        c.Print(pdf_fn)

c.Print(pdf_fn + ']')

os.system('evince %s' %pdf_fn)
