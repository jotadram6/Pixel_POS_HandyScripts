#!/bin/python

import sys, os
from pprint import pprint
from GetOpsPaths import *
set_style()

run = run_from_argv()
run_dir = run_dir(run)
in_fn = os.path.join(run_dir, 'POHBias.root')
if not os.path.isfile(in_fn):
    raise RuntimeError('no file at %s' % in_fn)

out_dir = outdir_from_argv()
if out_dir is not None:
    out_dir = os.path.join(out_dir, 'dump_pohbias')
else:
    out_dir = os.path.join(run_dir, 'dump_pohbias')
print "Generating output in:", out_dir
os.system('mkdir -p %s' % out_dir)

f = ROOT.TFile(in_fn)

gains = range(4)
feds = range(1000, 1500) #(1294,1301) for BmI;(1287,1294) for BpO; (1301,1308) for BmO; (1280,1287) for BpI.
fibre = range(25)

dirs = ['gain%(gn)i/FED%(fd)i' % locals() for gn in gains for fd in feds]

c = ROOT.TCanvas('c', '', 1800, 1750)
c.Divide(4,6)
c.cd(0)
pdf_fn = os.path.join(out_dir, 'all.pdf')
c.Print(pdf_fn + '[')

for d in dirs:
    if not f.Get(d):
        continue
    for ikey, key in enumerate(f.Get(d).GetListOfKeys()):
        canvas = key.ReadObj()
        name = canvas.GetName().replace(';1','')
        obj = canvas.FindObject(name)
        rest,fiber = name.split('fiber')
        ifiber = int(fiber)
        c.cd(ifiber)
        obj.Draw('')
        for x in canvas.GetListOfPrimitives():
            if x.GetName() == 'TLine':
                x.SetLineWidth(2)
                x.Draw()
        if key == f.Get(d).GetListOfKeys()[-1]:
            c.Print(pdf_fn)
            c.Close()
            c = ROOT.TCanvas('c', '', 1800, 1750)
            c.Divide(4,6)
            c.cd(0)
    #c.SaveAs(os.path.join(out_dir, d.split('/')[-1]) +'.pdf')
c.cd(0)
c.Print(pdf_fn + ']')

os.system('evince %s' %pdf_fn)

