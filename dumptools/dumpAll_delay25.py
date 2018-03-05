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

c = ROOT.TCanvas('c', '', 1300, 1000)
c.Divide(3,2)
c.cd(0)
pdf_fn = os.path.join(out_dir, 'all.pdf')
c.Print(pdf_fn + '[')

for d in dirs_short:
    if not f.Get(d):
        continue
    for ikey, key in enumerate(f.Get(d).GetListOfKeys()):
        obj = key.ReadObj()#.GetListOfPrimitives()[0]
        name = obj.GetName().replace(';1', '')
        pc = name.split(' ')[5]
        md = name.split(' ')[8]
        num = 0
        if 'command' in md:
            num = int(md.split('command')[-1])
        c.cd(num+1)
        canvas = obj.GetListOfPrimitives()[0]
        canvas.Draw()
        if len(obj.GetListOfPrimitives()) > 1:
            for x in obj.GetListOfPrimitives()[1:]:
                x.Draw()
        if num == 5:
            c.cd(0)
            c.Print(pdf_fn)
c.Print(pdf_fn + ']')

os.system('evince %s' %pdf_fn)
