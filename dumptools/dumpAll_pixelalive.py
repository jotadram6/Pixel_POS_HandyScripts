#!/bin/python

import sys, os
import commands as cmd
PWD = cmd.getoutput('pwd')
from pprint import pprint
sys.path.append(os.path.join(PWD,"/common/"))
#sys.path.append("../common/")
from JMTTools import *
from JMTROOTTools import *
set_style()

dynrng = False #'nodynrng' not in sys.argv

run = run_from_argv()
run_dir = run_dir(run)
out_dir = outdir_from_argv()
if out_dir is not None:
    out_dir = os.path.join(out_dir, 'dump_pixelalive')
else:
    out_dir = os.path.join(run_dir, 'dump_pixelalive')
print "Generating output in:", out_dir
os.system('mkdir -p %s' % out_dir)

f = ROOT.TFile(fetch_root(run_dir, run, ToFetch='total.root', PixelAlive_flag=True))

by_ntrigs = []
first = True

c = ROOT.TCanvas('c', '', 1300, 1000)
c.Divide(4,4)
c.cd(0)
pdf_fn = os.path.join(out_dir, 'all.pdf')
c.Print(pdf_fn + '[')

num_dead = defaultdict(int)
eff_thresh = 100.

for d in dirs:
    if not f.Get(d):
        continue
    for ikey, key in enumerate(f.Get(d).GetListOfKeys()):
        obj = key.ReadObj()
        name = obj.GetName().replace(' (inv)', '')
        rest, roc = name.split('ROC')
        iroc = int(roc)
        if int(roc) < 10:
            name = rest + 'ROC0' + roc
        mineff, maxeff = 100., 0.
        ntrigs = int(obj.Integral())
        by_ntrigs.append((ntrigs, name))
        for x in xrange(1, obj.GetNbinsX()+1):
            for y in xrange(1, obj.GetNbinsY()+1):
                eff = obj.GetBinContent(x,y)
                mineff = min(eff, mineff)
                maxeff = max(eff, maxeff)
                if obj.GetBinContent(x,y) < eff_thresh:
                    num_dead[name] += 1
        c.cd(iroc+1)
        if dynrng:
            if maxeff - mineff < 1:
                maxeff += 1
            obj.SetMinimum(mineff)
            obj.SetMaximum(maxeff)
        obj.Draw('colz')
    c.cd(0)
    c.SaveAs(os.path.join(out_dir, d.split('/')[-1]) + '.png')
    c.Print(pdf_fn)
c.Print(pdf_fn + ']')

by_ntrigs.sort(key=lambda x: x[1])
by_ntrigs.sort(key=lambda x: x[0], reverse=True)
pprint(by_ntrigs)

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

print '# dead pixels (eff lower than %f):' % eff_thresh
for roc in sorted(num_dead.keys()):
    if num_dead[roc]:
        print '%s %10i' % (roc.ljust(35), num_dead[roc])


if 'scp' in sys.argv:
    remote_dir = 'public_html/qwer/dump_pixelalive/%i' % run
    cmd = 'ssh jmt46@lnx201.lns.cornell.edu "mkdir -p %s"' % remote_dir
    print cmd
    os.system(cmd)
    cmd = 'scp -r %s/* jmt46@lnx201.lns.cornell.edu:%s' % (out_dir, remote_dir)
    print cmd
    os.system(cmd)
