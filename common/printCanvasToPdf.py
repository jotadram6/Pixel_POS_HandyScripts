#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python printCanvasToPdf.py <INPUT> <OUTPUT>

import sys
sys.argv.append('-b')
import ROOT; ROOT.TCanvas
sys.argv.remove('-b')
oldval = ROOT.gErrorIgnoreLevel
ROOT.gErrorIgnoreLevel = 3000

infName = sys.argv[1]
inf = ROOT.TFile.Open(infName)
outpdf_fn = sys.argv[2]

c = ROOT.TCanvas('c', '', 4320, 1350)
c.Print(outpdf_fn + '[')
for key in inf.GetListOfKeys():
    c = key.ReadObj()
    c.Print(outpdf_fn)
c.Print(outpdf_fn+']')
del c
ROOT.gErrorIgnoreLevel = oldval
