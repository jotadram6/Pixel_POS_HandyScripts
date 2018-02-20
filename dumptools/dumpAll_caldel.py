#!/bin/python

import sys, os
from pprint import pprint
sys.path.append("../common/")
from JMTTools import *
from JMTROOTTools import *
set_style()

run = run_from_argv()
run_dir = run_dir(run)

out_dir = outdir_from_argv()
if out_dir is not None:
    out_dir = os.path.join(out_dir, 'dump_caldel')
else:
    out_dir = os.path.join(run_dir, 'dump_caldel')
print "Generating output in:", out_dir
os.system('mkdir -p %s' % out_dir)

in_fn = os.path.join(run_dir, 'CalDel_1.root')
if not os.path.isfile(in_fn):
    raise IOError('no root file %s' % in_fn)
f = ROOT.TFile(in_fn)

c = ROOT.TCanvas('c', '', 1300, 1000)
c.Divide(4,4)
c.cd(0)
pdf_fn = os.path.join(out_dir, 'all.pdf')



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
            if rocname in t.GetName().replace('_c', '')[-len(rocname):]:
                ordered.append(t)
    hs = ordered
    return [f.Get(d).GetName(), hs]



c.Print(pdf_fn + '[')
for d in dirs:
    if not f.Get(d):
        continue
    name,histos = mkHistList(f,d)

    for obj in histos:
#    for ikey, key in enumerate(f.Get(d).GetListOfKeys()):
#        obj = key.ReadObj()
        name = obj.GetName().replace('_c', '')
        rest, roc = name.split('ROC')
        iroc = int(roc)
        if int(roc) < 10:
            name = rest + 'ROC0' + roc
        c.cd(iroc+1)
        canvas = obj.GetListOfPrimitives()[0]
        canvas.Draw('colz')
        if len(obj.GetListOfPrimitives()) > 1:
            for line in obj.GetListOfPrimitives()[1:]:
                line.Draw()
    c.cd(0)
    c.SaveAs(os.path.join(out_dir, d.split('/')[-1]) + '.png')
    c.Print(pdf_fn)
c.Print(pdf_fn + ']')

if 'html' in sys.argv:
    pngs = [f for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir,f)) and f.endswith('png')]
    pngs.sort()

    html_fn = os.path.join(out_dir, 'index.html')
    html = open(html_fn, 'wt')
    html.write('<html><body>\n')

    for item in pngs:
        html.write('<br><h1>%s</h1>\n' %item)
        html.write('<img src="%s">\n' %item)

    html.write('</body></html>\n')
    html.close()
    os.system('firefox %s' %html_fn)
else:
    os.system('evince %s' %pdf_fn)


if 'scp' in sys.argv:
    remote_dir = 'public_html/qwer/dump_caldel/%i' % run
    cmd = 'ssh jmt46@lnx201.lns.cornell.edu "mkdir -p %s"' % remote_dir
    print cmd
    os.system(cmd)
    cmd = 'scp -r %s/* jmt46@lnx201.lns.cornell.edu:%s' % (out_dir, remote_dir)
    print cmd
    os.system(cmd)
