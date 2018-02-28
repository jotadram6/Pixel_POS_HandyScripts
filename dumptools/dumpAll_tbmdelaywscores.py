#!/bin/python

import sys, os
import commands as cmd
PWD = cmd.getoutput('pwd')
from pprint import pprint
sys.path.append(os.path.join(PWD,"common/"))
from JMTTools import *
from JMTROOTTools import *
set_style()

run = run_from_argv()
run_dir = run_dir(run)
in_fn = os.path.join(run_dir, 'TBMDelay.root')
if not os.path.isfile(in_fn):
    raise RuntimeError('no file at %s' % in_fn)
f = ROOT.TFile(in_fn)

out_dir = outdir_from_argv()
if out_dir is not None:
    out_dir = os.path.join(out_dir, 'dump_tbmdelaywscores')
else:
    out_dir = os.path.join(run_dir, 'dump_tbmdelaywscores')
print "Generating output in:", out_dir
os.system('mkdir -p %s' % out_dir)

# JMT need ROOT os.walk...
all_graphs = defaultdict(dict)

c = ROOT.TCanvas('c', '', 1300, 1000)
c.Divide(3,3)
c.cd(0)
pdf_fn = os.path.join(out_dir, 'all.pdf')
c.Print(pdf_fn + '[')

for ikey, key in enumerate(f.GetListOfKeys()):
    obj = key.ReadObj()
    c.cd(ikey % 9 + 1)
    obj.Draw()
    c.Update()
    if ikey % 9 == 8:
        c.cd(0)
        c.Print(pdf_fn)
c.cd(0)
c.Print(pdf_fn + ']')

os.system('evince %s' %pdf_fn)
