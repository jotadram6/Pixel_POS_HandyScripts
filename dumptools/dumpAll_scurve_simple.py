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

pdf_fn = os.path.join(out_dir, 'SCurve_simple.pdf')

c = ROOT.TCanvas('c', '', 1920, 1000)
c.Divide(4,2)

hists = [x.strip() for x in '''
MeanThreshold
MeanNoise
MeanChisquare
MeanProbability
RmsThreshold
RmsNoise
ThresholdOfAllPixels
NoiseOfAllPixels
'''.split('\n') if x.strip()]

for i,hn in enumerate(hists):
    h = f.Get('Summaries/%s' % hn)
    c.cd(i+1).SetLogy()
    h.Draw()
c.cd(0)
c.SaveAs(pdf_fn)

os.system('evince %s'%pdf_fn)

#if 'scp' in sys.argv:
#    remote_dir = 'public_html/qwer/dump_scurve_simple/%i' % run
#    cmd = 'ssh jmt46@lnx201.lns.cornell.edu "mkdir -p %s"' % remote_dir
#    print cmd
#    os.system(cmd)
#    cmd = 'scp -r %s/scurve_simple.pdf jmt46@lnx201.lns.cornell.edu:%s' % (run_dir, remote_dir)
#    print cmd
#    os.system(cmd)
