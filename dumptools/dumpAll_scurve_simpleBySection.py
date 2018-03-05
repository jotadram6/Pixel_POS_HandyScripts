#!/bin/python

from GetOpsPaths import *
set_style(True)

run = run_from_argv()
run_dir = run_dir(args.run)
#run_dir="/data/tif/Run_BmO/Run_1898/"

f = ROOT.TFile(fetch_root(run_dir, run, ToFetch='total.root', BB3Simple_flag=True))

out_dir = outdir_from_argv()
if out_dir is not None:
    out_dir = os.path.join(out_dir, 'dump_scurve')
else:
    out_dir = os.path.join(run_dir, 'dump_scurve')
print "Generating output in:", out_dir
if not os.path.isdir(out_dir):
    os.system('mkdir -p -m 766 %s' %out_dir)

pdf_fn = os.path.join(out_dir, 'SCurve_simple-D1.pdf')

c = ROOT.TCanvas('c', '', 1920, 1000)
c.Divide(2,1)

h1s = []
for d in dirs:
    if not f.Get(d): continue
    for key in f.Get(d).GetListOfKeys():
        obj = key.ReadObj()
        if not obj.GetName().endswith("Threshold1D"): continue
        h1s.append(obj)

print "We have {0:d} ROCs.".format(len(h1s))

if not len(h1s):
    sys.exit("There is no ROCs in root file, exiting...")

rocThresH1 = ROOT.TH1F("Mean Threshold of All ROCs - D1R1","",100,0,200)
rocThresH1.SetTitle("Mean Threshold of All ROCs - D1R1")
rocThresH1.GetXaxis().SetTitle("Vcal")
for h in h1s:
    rocThresH1.Fill(h.GetMean())

c.cd(1).SetLogy()
rocThresH1.Draw()

sumH1 = h1s[0].Clone("Threshold of All Pixels - D1R1")
sumH1.SetTitle("Threshold of All Pixels - D1R1")
for h in h1s[1:]:
    sumH1.Add(h)

c.cd(2).SetLogy()
sumH1.Draw()
        
c.SaveAs(pdf_fn)

#for i,hn in enumerate(hists):
#    h = f.Get('Summaries/%s' % hn)
#    c.cd(i+1).SetLogy()
#    h.Draw()
#c.cd(0)
#c.SaveAs(pdf_fn)

os.system('evince %s'%pdf_fn)

#if 'scp' in sys.argv:
#    remote_dir = 'public_html/qwer/dump_scurve_simple/%i' % run
#    cmd = 'ssh jmt46@lnx201.lns.cornell.edu "mkdir -p %s"' % remote_dir
#    print cmd
#    os.system(cmd)
#    cmd = 'scp -r %s/scurve_simple.pdf jmt46@lnx201.lns.cornell.edu:%s' % (run_dir, remote_dir)
#    print cmd
#    os.system(cmd)
