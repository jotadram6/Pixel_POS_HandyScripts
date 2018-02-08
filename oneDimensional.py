from JMTROOTTools import *
from JMTTools import *
import os, sys
set_style()

run = int(sys.argv[1])
calibration = sys.argv[2]
plotType = sys.argv[3]

run_dir = run_dir(run)
in_fn = glob(os.path.join(run_dir, 'total.root'))
inf = in_fn[0]

f = ROOT.TFile(inf)

dirs = dirs = ['FPix/FPix_%(hc)s/FPix_%(hc)s_D%(dsk)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i' % locals() for hc in ['BmI', 'BmO', 'BpI', 'BpO'] for dsk in range(1,4) for bld in range(1,18) for pnl in range(1,3) for rng in range(1,3)]


c = ROOT.TCanvas('c','',4000,2000)
c.Divide(4,2)

c.cd(0)
hcCode = {'BmI':1, 'BmO':2, 'BpI':3, 'BpO':4}
datapool = {}

for d in dirs:
    if not f.Get(d):
        continue
    for key in f.Get(d).GetListOfKeys():
        obj = key.ReadObj()
        name = obj.GetName()
        if name.split('_')[-1] != plotType+"2D":
            continue # we are looking for "FPix_BpI_D1_BLD1_PNL1_RNG1_ROC0_Threshold2D"
        HC = hcCode[name.split('_')[1]]
        DSK = int(name.split('_')[2][1:])
        BLD = int(name.split('_')[3][3:])
        PNL = int(name.split('_')[4][3:])
        RNG = int(name.split('_')[5][3:])
        ROC = int(name.split('_')[6][3:])

        rocKey = (HC, DSK, BLD, PNL, RNG, ROC)
        row = obj.GetNbinsY() #80
        col = obj.GetNbinsX() #52

        val = [obj.GetBinContent(i+1, j+1) for j in range(row) for i in range(col)]
        datapool[rocKey] = val
        #if obj.Integral() / (row*col) == 0:
        #    datapool[rocKey] = [-1] *4160 # Complete empty roc, filled with '-1'
        #print len(val)

hDatapool = {}
for x in range(8):
    hDatapool[x] = []

for rocKey in datapool.keys():
    hc, dsk, bld, pnl, rng, roc = rocKey
    for x in range(4):
        if x+1 == hc:
            hDatapool[x] += datapool[rocKey]
    for d in range(3):
        if d+1 == dsk:
            hDatapool[d+4] += datapool[rocKey]
    hDatapool[7] += datapool[rocKey]

print len(hDatapool)
for x in range(8):
    print len(hDatapool[x])

subjectList = ["BmI", "BmO", "BpI", "BpO", "Disk1", "Disk2", "Disk3", "Total"]
ROOT.gStyle.SetOptStat()#(000001110)
hs = []
for ih in range(8):
    title = "{0} {1} distribution of FPix {2} modules".format(calibration, plotType, subjectList[ih])
    if plotType == "Threshold":
        h = ROOT.TH1F(title,"",350,0,700)
    if plotType == "Noise":
        h = ROOT.TH1F(title,"",120,0,60)
    for entry in hDatapool[ih]:
        h.Fill(entry)
    if ih in range(4):
        h.SetFillColor(ROOT.kOrange-3)
    if ih in range(4,7):
        h.SetFillColor(ROOT.kSpring-7)
    if ih == 7:
        h.SetFillColor(ROOT.kAzure+4)
    h.SetTitle(title)
    h.GetXaxis().SetTitle("{0}(e)".format(plotType))
    h.GetYaxis().SetTitle("No. of Entries")
    hs.append(h)
for ih, h in enumerate(hs):
    c.cd(ih+1)
    c.cd(ih+1).SetLogy()
    c.cd(ih+1).SetGrid()
    h.Draw()
    c.Update()

c.SaveAs(os.path.join(run_dir, "{0}.pdf".format('-'.join([calibration, plotType,str(run),"1d"]))))
