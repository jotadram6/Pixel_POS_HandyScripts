from JMTTools import *
from JMTROOTTools import *
import os
import sys
set_style()

run = int(sys.argv[1])
run_dir = run_dir(run)
in_fn = glob(os.path.join(run_dir, 'total.root'))
inf = in_fn[0]

out_dir = os.path.join(run_dir, 'wsitest')
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)
out_fn = os.path.join(out_dir, 'output.pdf')

###############################################################
f = ROOT.TFile(inf)
moduleDict = {'HC': ['BmI'],
             'DSK': [3],
             'BLD': [11],
             'PNL': [2],
             'RNG': [2]}
moduleList = [(a,b,c,d,e) for a in moduleDict['HC']
                          for b in moduleDict['DSK']
                          for c in moduleDict['BLD']
                          for d in moduleDict['PNL']
                          for e in moduleDict['RNG']]
dirs = []
for hc,dsk,bld,pnl,rng in moduleList:
    dirs.append('FPix/FPix_{0}/FPix_{0}_D{1}/FPix_{0}_D{1}_BLD{2}/FPix_{0}_D{1}_BLD{2}_PNL{3}/FPix_{0}_D{1}_BLD{2}_PNL{3}_RNG{4}'.format(hc,dsk,bld,pnl,rng))

###############################################################
## ColorScale: 
ncontours = 999
stops = [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000]
red   = [242./255., 234./255., 237./255., 230./255., 212./255., 156./255., 99./255., 45./255., 0./255.]
green = [243./255., 238./255., 238./255., 168./255., 101./255.,  45./255.,  0./255.,  0./255., 0./255.]
blue  = [230./255.,  95./255.,  11./255.,   8./255.,   9./255.,   3./255.,  1./255.,  1./255., 0./255.]
s = array('d', stops)
r = array('d', red)
g = array('d', green)
b = array('d', blue)
ROOT.TColor.CreateGradientColorTable(len(s), s, r, g, b, ncontours)
ROOT.gStyle.SetNumberContours(ncontours)
ROOT.gStyle.SetOptStat(1110)

###############################################################
c = ROOT.TCanvas('c', '', 1500, 500)
c.Divide(3,1)
c.cd(0)

orig = []
data = []

for d in dirs:
    if not f.Get(d):
        continue
    for key in f.Get(d).GetListOfKeys():
        obj = key.ReadObj()
        name = obj.GetName()
        if name.split('_')[-1] != "Threshold2D":
            continue
        ROC = int(name.split('_')[6][3:])
        orig.append(obj)
        val = [obj.GetBinContent(i+1, j+1) for j in xrange(80) for i in xrange(52)]
        origVal = [x for x in val] # make a copy
        data.append(origVal)
        val.sort()
        tmp = [x for x in val if x!=0 ]
        if len(tmp)>10:
            val = tmp
                
###############################################################

c.Print(out_fn + '[')
for i in range(len(orig)):
    print
    print "ROC-{0}".format(i+1)
    c.cd(1)
    orig[i].Draw()
    c.cd(2)
    val = [x for x in data[i] if x!=0]
    val.sort()
    rangeh = (val[10], val[-10])
    print "{0:10}{1}".format('hRange:',rangeh)
    nbin = int(round( (rangeh[1]-rangeh[0]) * 2))
    h = ROOT.TH1F('Gaussian fit - ROC%i' %(i+1),'',nbin, rangeh[0], rangeh[1])
    for v in val:
        h.Fill(v)
    #mostFilled = h.GetBinCenter(h.GetMaximumBin())
    h.SetStats(0)
    h.Draw()
    h.Fit('gaus', "Q")
    ff = h.GetFunction("gaus")
    ff.SetLineColor(3)
    mean = ff.GetParameter(1)
    sigma = ff.GetParameter(2)
    print "{0:10}{1}".format('Mean:',mean)
    print "{0:10}{1}".format('Sigma:',sigma)
    tmp = [abs(v-mean)/sigma if v !=0 else -1 for v in data[i] ]
    normVal = [0 if x<5 and x>0 else x for x in tmp]
    print "{0:10}{1}".format('BadBumps:',len([x for x in normVal if x>5]))
    c.cd(3)
    hn = ROOT.TH2F('Nomalized - ROC%i' %(i+1),'',52,0,52,80,0,80)
    for j in range(80):
        for i in range(52):
            hn.SetBinContent(i+1,j+1,normVal[j*52+i])
    hn.SetStats(0)
    hn.SetMaximum(6)
    hn.SetMinimum(-1)
    hn.Draw("colz a")
    c.cd(0)
    c.Print(out_fn)

c.Print(out_fn + ']')
###############################################################
os.system("evince %s&" %out_fn)
