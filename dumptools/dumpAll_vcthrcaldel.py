#!/bin/python

import sys, os
from pprint import pprint
from GetOpsPaths import *
set_style()

run = run_from_argv()
run_dir = run_dir(args.run)

#Replaced by the line below
#in_fn = glob(os.path.join(run_dir, 'VcThrCalDel_total.root'))
#if not in_fn:
#    in_fn = glob(os.path.join(run_dir, 'VcThrCalDel_*.root'))
#    if len(in_fn) == 1:
#        in_fn = in_fn[0]
#    else:
#        os.system('hadd -v 0 {0}/VcThrCalDel_total.root {0}/VcThrCalDel*.root'.format(run_dir))
#        in_fn = os.path.join(run_dir, 'VcThrCalDel_total.root')
#else:
#    in_fn = in_fn[0]
#    
#if not os.path.isfile(in_fn):
#    raise RuntimeError('no file at %s' % in_fn)
#f = ROOT.TFile(in_fn)

f = ROOT.TFile(fetch_root(run_dir, run, ToFetch='VcThrCalDel_total.root', VcThrCalDel_flag=True))


out_dir = outdir_from_argv()
if out_dir is not None:
    out_dir = os.path.join(out_dir, 'dump_vcthrcaldel')
else:
    out_dir = os.path.join(run_dir, 'dump_vcthrcaldel')
print "Generating output in:", out_dir
os.system('mkdir -p %s' % out_dir)

by_ntrigs = []
first = True

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
            if rocname in t.GetName().replace('_Canvas', '')[-len(rocname):]:
                ordered.append(t)
    hs = ordered
    return [f.Get(d).GetName(), hs]


c.Print(pdf_fn + '[')

for d in dirs:
    if not f.Get(d):
        continue
    name,objects = mkHistList(f,d)

    for canvas in objects:
#    for ikey, key in enumerate(f.Get(d).GetListOfKeys()):
#        canvas = obj.ReadObj()
        name = canvas.GetName().replace(' (inv)', '').replace('_Canvas', '')
        obj = canvas.FindObject(name)
        #lines = [x for x in canvas.GetListOfPrimitives() if x.Class().GetName() == "TLine"]
        rest, roc = name.split('ROC')
        iroc = int(roc)
        if int(roc) < 10:
            name = rest + 'ROC0' + roc
        ntrigs = int(obj.Integral())
        by_ntrigs.append((ntrigs, name))
        c.cd(iroc+1)
        obj.Draw('colz')
        if 1:
            for x in canvas.GetListOfPrimitives():
                if x.GetName() == 'TLine':
                    x.SetLineWidth(1)
                    x.Draw()
    c.cd(0)
    c.SaveAs(os.path.join(out_dir, d.split('/')[-1]) + '.png')
    #c.SaveAs(os.path.join(out_dir, d.split('/')[-1]) + '.root')
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

