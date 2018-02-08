from JMTROOTTools import *
from JMTTools import *
import os, sys

## This is used for plotting noise/threshold from
## scurve run also have same style as BPix plot.
## $python totalOneDimensional.py 185 scurve Noise&


set_style()

run = int(sys.argv[1])
calibration = sys.argv[2]
plotType = sys.argv[3]

run_dir = run_dir(run)
in_fn = glob(os.path.join(run_dir, 'total.root'))
inf = in_fn[0]

f = ROOT.TFile(inf)

dirs = dirs = ['FPix/FPix_%(hc)s/FPix_%(hc)s_D%(dsk)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i' % locals() for hc in ['BmI', 'BmO', 'BpI', 'BpO'] for dsk in range(1,4) for bld in range(1,18) for pnl in range(1,3) for rng in range(1,3)]


c = ROOT.TCanvas('c','',500,500)

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

        val = [obj.GetBinContent(i+1, j+1) for i in range(col) for j in range(row)]
        datapool[rocKey] = val

hDatapool = []

for rocKey in datapool.keys():
    hDatapool += datapool[rocKey]

print len(hDatapool)

# Stat box: Number of entries; mean; rms.
# Value only, no error
ROOT.gStyle.SetOptStat(1110)
ROOT.gStyle.SetPadTickX(0) # No ticks on topmost
ROOT.gStyle.SetPadTickY(0) # No ticks on rightmost

title = "{0} distribution of FPix Pixels".format(plotType)
if plotType == "Noise":
    h = ROOT.TH1F(title,"",100,0,600)
if plotType == "Threshold":
    h = ROOT.TH1F(title,"",300,1000,4200)
for entry in hDatapool:
    h.Fill(entry*50) # 50e/vcal

# To draw under/overflow bin
nx = h.GetNbinsX() + 1
x1 = h.GetBinLowEdge(1)
bw = h.GetBinWidth(nx)
x2 = h.GetBinLowEdge(nx) + bw
r = ROOT.TH1F(title, "", nx, x1, x2)
for i in range(1, nx+1):
    r.Fill(h.GetBinCenter(i), h.GetBinContent(i))
r.Fill(x1-1, h.GetBinContent(0))
r.SetEntries(h.GetEntries())
r.SetFillColor(ROOT.kAzure+4) # Set fill color
#r.GetYaxis().SetTitleOffset(1.4)
r.GetXaxis().SetLabelSize(0.03) # Set tick label font size
r.GetYaxis().SetLabelSize(0.03)
#r.GetYaxis().SetRangeUser(1,1000000)
c.cd()
c.cd().SetGrid()
c.cd().SetLogy()
r.Draw()
c.Update()

# Y axis title, - pavebox
yTitle = "No. of Entries"
## BottomleftX, bottomleftY, toprightX, toprightY
## 0-0.1, 0-0.9: canvas edge to graph edge;
## 0.1-.09: graph
yt = ROOT.TPaveText(0.031,0.3,0.058,0.66,"NDC")
# rotate pavebox by 90 degree anti-clockwise
ytt = yt.AddText(yTitle)
yt.SetTextAlign(21)
ytt.SetTextAngle(90)
yt.SetFillColor(0)
yt.SetTextSize(0.035)
yt.SetTextFont(42)
yt.SetBorderSize(0)
yt.Draw()

ht = ROOT.TPaveText(0.1, 0.902, 0.6, 0.95, "NDC" )
ht.AddText(title)
ht.SetTextAlign(12)
ht.SetTextFont(42)
ht.SetFillColor(0)
ht.SetTextSize(0.034)
ht.SetBorderSize(0)
ht.Draw()
c.Update()

def write(font, x, y, text):
    ## draw TLatex object
    w = ROOT.TLatex()
    w.SetNDC()
    w.SetTextSize(0.035)
    w.SetTextFont(font)
    w.DrawLatex(x,y,text)
    return w

cms = write(61, 0.64,0.63,'CMS')
pre = write(52, 0.72,0.63,'preliminary')

xTitle = plotType+" (e^{-})"
xat = write(42, 0.45,0.038,xTitle)


ROOT.gPad.Update()

## Set statbox size, location & fontsize
st = r.FindObject("stats")
st.SetX1NDC(0.66)
st.SetY1NDC(0.69)
st.SetX2NDC(0.87)
st.SetY2NDC(0.87)
st.SetTextSize(0.02)
c.Update()


c.SaveAs(os.path.join(run_dir, "{0}.pdf".format('-'.join(["FFPix", plotType,str(run),"1d"]))))
