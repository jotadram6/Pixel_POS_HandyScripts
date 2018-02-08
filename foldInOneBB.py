from JMTROOTTools import *
from JMTTools import *
import os, sys
set_style()

PIXEL_NUM_X = 52 # number of pixels along X in a ROC
PIXEL_NUM_Y = 80 # number of pixels along Y in a ROC
ROC_NUM_X = 8*8 # number of ROCs along X in the map
ROC_NUM_Y = 3*(11+17)*2 # number of ROCs along Y in the map

run = int(sys.argv[1])
calibration = sys.argv[2]
plotType = sys.argv[3]

run_dir = run_dir(run)
in_fn = glob(os.path.join(run_dir, 'total.root'))
inf = in_fn[0]

def getRocCoord(rocKey):
    ## Given the rocKey,
    ## Return the ROC coordinate (rx,ry)
    hc, dsk, bld, pnl, rng, roc = rocKey
    if pnl == 1:
        rx = 0 +\
             (hc-1)*8 +\
             ((roc-8) if (roc>7) else (7-roc))
    elif pnl == 2:
        rx = 32 +\
             (4-hc)*8+\
             ((15-roc) if (roc>7) else roc)
    
    if rng == 1:
        ry = (3-dsk)*56 +\
             34+\
             (11-bld)*2 +\
             (0 if (roc>7) else 1)
    elif rng ==2:
        ry = (3-dsk)*56 +\
             0 +\
             (17-bld)*2 +\
             (0 if (roc>7) else 1)
    return (rx, ry)

def SetPixelBinContent(h, rocCoord, val):
    '''
        Given histogram h, rocCoord = (rx, ry),
        and list of val = [a,b...z] #4160 in total, corrected already

        Setting value in the right location
    '''
    for j in range(PIXEL_NUM_Y):
        for i in range(PIXEL_NUM_X):
            rx, ry = rocCoord
            px = rx*PIXEL_NUM_X + i
            py = ry*PIXEL_NUM_Y + j
            pv = val[j*PIXEL_NUM_X+i]
            h.SetBinContent(px+1, py+1, pv)

def getCorrectedPixelVal(rocKey, val):
    '''
        rocKey = (hc,dsk,bld,pnl,rng,roc)
        val    = [a,b...z] #4160 in total, to be corrected
        return [a,b...z] but properly symmtrized
    '''
    hc, dsk, bld, pnl, rng, roc = rocKey
    ## case1, no need to change
    if roc in range(8,16) and pnl == 1:
        return val

    nested = [val[i:i+PIXEL_NUM_X] for i in range(0, len(val), PIXEL_NUM_X)]
    ## case2, horizontal mirror symmetry
    if roc in range(8,16) and pnl == 2:
        #res = [[0]*PIXEL_NUM_X] * PIXEL_NUM_Y
        res = [nested[j][PIXEL_NUM_X-1-i] for j in range(PIXEL_NUM_Y) for i in range(PIXEL_NUM_X)]
        return res
    ## case3, vertical mirror symmetry
    if roc in range(8) and pnl == 2:
        res = [nested[PIXEL_NUM_Y-1-j][i] for j in range(PIXEL_NUM_Y) for i in range(PIXEL_NUM_X)]
        return res
    ## case4, rotated 180 around 1 point
    if roc in range(8) and pnl == 1:
        res = [nested[PIXEL_NUM_Y-1-j][PIXEL_NUM_X-1-i] for j in range(PIXEL_NUM_Y) for i in range(PIXEL_NUM_X)]
        return res
        
def getFit(fitRange):
    fitL, fitH = fitRange
    f = ROOT.TF1('f','gaus',fitL,fitH)
    return f


f = ROOT.TFile(inf)

dirs = dirs = ['FPix/FPix_%(hc)s/FPix_%(hc)s_D%(dsk)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i' % locals() for hc in ['BmI', 'BmO', 'BpI', 'BpO'] for dsk in range(1,4) for bld in range(1,18) for pnl in range(1,3) for rng in range(1,3)]

## ColorScale: 
ncontours = 255
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

################################################
c = ROOT.TCanvas('c','',3000,5300)
ROOT.gPad.SetLeftMargin(0.2)

hcCode = {'BmI':1, 'BmO':2, 'BpI':3, 'BpO':4}
datapool = {} #(rocKey):[pixel value list]

print "Start stuffing..."
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

        val = [obj.GetBinContent(i+1, j+1) for j in xrange(row) for i in xrange(col)] # 50e/vcal
        # Making a copy..
        originalVal = [x for x in val] 
        datapool[rocKey] = originalVal


print "Start fitting..."
for ir, rocKey in enumerate(datapool.keys()):
    originalVal = datapool[rocKey]
    val = [x for x in originalVal]
    tmp0 = [v for v in val if v!=0]
    if len(tmp0)>10:
        val = tmp0
    val.sort()
    rangeh = (val[10], val[-10])
    nbin = int(round( (rangeh[1]-rangeh[0]) * 2))
    h = ROOT.TH1F('Gaussian fit - %s' %str(rocKey),'',nbin, rangeh[0], rangeh[1])
    for v in val:
        h.Fill(v)
    #mostFilled = h.GetBinCenter(h.GetMaximumBin())
    #edgeL = mostFilled-val[10]
    #edgeR = val[-10]-mostFilled
    #if edgeL > edgeR:
    #    fitRange = (mostFilled-edgeR*2., mostFilled+edgeR)
    #else:
    #    fitRange = (mostFilled-edgeL, mostFilled+edgeL*2.)
    #res = h.Fit(getFit(fitRange), 'QRS')
    h.Fit('gaus','Q')
    ff = h.GetFunction('gaus')
    mean = ff.GetParameter(1)
    sigma= ff.GetParameter(2)
    tmp = [abs(v-mean)/sigma if v!=0 else -1 for v in originalVal]
    rescale = []
    for v in tmp:
        if v>=5:
            rescale.append(2)
        if 0<v<5:
            rescale.append(1)
        else:
            rescale.append(0)
    datapool[rocKey] = rescale
    if sum(datapool[rocKey])/len(datapool[rocKey])>1.25:
        print ir, rocKey, mean, sigma 


h = ROOT.TH2F("FPIX PHASE1", '', ROC_NUM_X*PIXEL_NUM_X, 0, ROC_NUM_X*PIXEL_NUM_X,
                                 ROC_NUM_Y*PIXEL_NUM_Y, 0, ROC_NUM_Y*PIXEL_NUM_Y,)
h.SetStats(False) # turn off statbox

## setting threshold
if plotType == "Threshold":
    h.SetMinimum(0)
    h.SetMaximum(2) # 500vcal * 50e/vcal
if plotType == "Noise":
    h.SetMinimum(0)
    h.SetMaximum(200)

for rocKey in datapool.keys():
    rocCoord = getRocCoord(rocKey)
    correctedVal = getCorrectedPixelVal(rocKey, datapool[rocKey])
    SetPixelBinContent(h, rocCoord, correctedVal)

c.cd()
h.Draw("colz a")
c.Update()

## setting palette size, location and fontsize
palette = h.GetListOfFunctions().FindObject("palette")
palette.SetX1NDC(0.94)
palette.SetY1NDC(0.40)
palette.SetX2NDC(0.96)
palette.SetY2NDC(0.60)
palette.SetLabelSize(0.015)
palette.SetLabelFont(42)

## ticks on Y axis
# left
tickLength = 1 * PIXEL_NUM_X
textBoxWidth = 1.6 * PIXEL_NUM_X
axisLabels = [] # storing all axis labels

y_offset = 0
yticks = list(reversed(range(1,12)+range(1,18)))*3

for tick,text in enumerate(yticks):
    text1 = ROOT.TPaveText(-1*(tickLength + textBoxWidth*0.5),
                           y_offset + 0.2*PIXEL_NUM_Y*2,
                           -1*(tickLength - textBoxWidth*0.5),
                           y_offset + 0.8*PIXEL_NUM_Y*2,
                           "NB")
    text1.AddText(str(text))
    text1.SetMargin(0)
    axisLabels.append(text1)
    line1 = ROOT.TLine()
    line1.SetLineWidth(4)
    line1.DrawLine(0,
                   y_offset,
                   -1 * tickLength,
                   y_offset)
    if text == 11 and tick%28>11:
        tickLength2 = 5*tickLength
        textBoxWidth2 = 5*tickLength
        text2 = ROOT.TPaveText(-1*(tickLength2+textBoxWidth2/2.),
                               y_offset + 8.5*tickLength,
                               -1*(tickLength2-textBoxWidth2/2.),
                               y_offset + 13.5*tickLength,
                               "NB")
        text2.AddText("RNG1")
        axisLabels.append(text2)
        text3 = ROOT.TPaveText(-1*(tickLength2+textBoxWidth2/2.),
                               y_offset-19.5*tickLength,
                               -1*(tickLength2-textBoxWidth2/2.),
                               y_offset-14.5*tickLength,
                               "NB")
        text3.AddText("RNG2")
        axisLabels.append(text3)
        line2 = ROOT.TLine()
        line2.SetLineWidth(4)
        line2.DrawLine(0,
                       y_offset,
                       -1 * tickLength2,
                       y_offset)
    if text == 17:
        tickLength3 = 10*tickLength
        textBoxWidth3 = 6*tickLength
        text4 = ROOT.TPaveText(-1*(tickLength3+textBoxWidth3/2.),
                               y_offset+23*tickLength,
                               -1*(tickLength3-textBoxWidth3/2.),
                               y_offset+33*tickLength,
                               "NB")
        text4.AddText("DSK"+str(3-tick/28))
        axisLabels.append(text4)

        line3 = ROOT.TLine()
        line3.SetLineWidth(8)
        line3.DrawLine(0,
                       y_offset,
                       -1 * tickLength3,
                       y_offset)
    y_offset += 2*PIXEL_NUM_Y # move up 2 ROC height each time

# topmost tick
lineTop = ROOT.TLine()
lineTop.SetLineWidth(8)
lineTop.DrawLine(0,ROC_NUM_Y*PIXEL_NUM_Y,-10*tickLength,ROC_NUM_Y*PIXEL_NUM_Y)

# add "BLD" pavebox
textBld = ROOT.TPaveText(-1*(tickLength*3),
                         ROC_NUM_Y*PIXEL_NUM_Y + tickLength*0.2,
                         0,
                         ROC_NUM_Y*PIXEL_NUM_Y + tickLength*4)
textBld.AddText("BLD")
axisLabels.append(textBld)


# right
y_offset = 0
for tick, text in enumerate(yticks):
    text1 = ROOT.TPaveText(ROC_NUM_X*PIXEL_NUM_X + (tickLength - textBoxWidth*0.5),
                           y_offset+0.2*tickLength*2,
                           ROC_NUM_X*PIXEL_NUM_X +(tickLength + textBoxWidth*0.5),
                           y_offset+1.8*tickLength*2,
                           "NB")
    text1.AddText(str(text))
    text1.SetMargin(0)
    axisLabels.append(text1)
    line1 = ROOT.TLine()
    line1.SetLineWidth(4)
    line1.DrawLine(ROC_NUM_X*PIXEL_NUM_X,
                   y_offset,
                   ROC_NUM_X*PIXEL_NUM_X + tickLength,
                   y_offset)
    y_offset += 2*PIXEL_NUM_Y

c.Update()

## ticks on X axis
textBoxWidthX = 0.8*PIXEL_NUM_X
x_offset = 0
xtickHCList = sorted(hcCode, key=lambda k: hcCode[k])
xtickHCList += list(reversed(xtickHCList))
# bottom
xticksBottom = range(8,16)*4 + list(reversed(range(8,16)))*4
for tick, text in enumerate(xticksBottom):
    text1 = ROOT.TPaveText(x_offset+0.1*tickLength,
                           -1*(tickLength+textBoxWidthX/2),
                           x_offset+0.9*tickLength,
                           -1*(tickLength-textBoxWidthX/2),
                           "NB" )
    text1.AddText(str(text))
    axisLabels.append(text1)

    line1 = ROOT.TLine()
    line1.DrawLine(x_offset,
                   0,
                   x_offset,
                   -1*tickLength)
    if tick%8 == 0:
        tickLength2 = 2*tickLength
        textBoxWidthX2 = 4*textBoxWidthX
        line2 = ROOT.TLine()
        line2.DrawLine(x_offset,
                       0,
                       x_offset,
                       -1*tickLength2)
        text2 = ROOT.TPaveText(x_offset+2*PIXEL_NUM_X,
                               -1*(tickLength2 + textBoxWidthX2*0.75),
                               x_offset+6*PIXEL_NUM_X,
                               -1*(tickLength2 - textBoxWidthX2*0.25),
                               "NB")
        text2.AddText(xtickHCList[tick/8])
        axisLabels.append(text2)
    x_offset += 1*PIXEL_NUM_X

# - Add bottom rightmost tick
lineRightB = ROOT.TLine()
lineRightB.SetLineWidth(4)
lineRightB.DrawLine(ROC_NUM_X*PIXEL_NUM_X,0,ROC_NUM_X*PIXEL_NUM_X,-1*tickLength2)


# top ticks
xticksTop = list(reversed(range(8)))*4 + range(8)*4
x_offset = 0
for tick, text in enumerate(xticksTop):
    text1 = ROOT.TPaveText(x_offset+0.1*tickLength,
                           ROC_NUM_Y*PIXEL_NUM_Y + (tickLength-textBoxWidthX/2),
                           x_offset+0.9*tickLength,
                           ROC_NUM_Y*PIXEL_NUM_Y + (tickLength+textBoxWidthX/2),
                           "NB" )
    text1.AddText(str(text))
    axisLabels.append(text1)

    line1 = ROOT.TLine()
    line1.DrawLine(x_offset,
                   ROC_NUM_Y*PIXEL_NUM_Y,
                   x_offset,
                   ROC_NUM_Y*PIXEL_NUM_Y + tickLength)
    if tick%8 == 0:
        tickLength2 = 2*tickLength
        textBoxWidthX2 = 4*textBoxWidthX
        line2 = ROOT.TLine()
        line2.DrawLine(x_offset,
                       ROC_NUM_Y*PIXEL_NUM_Y,
                       x_offset,
                       ROC_NUM_Y*PIXEL_NUM_Y + tickLength2)
        text2 = ROOT.TPaveText(x_offset+2*PIXEL_NUM_X,
                               ROC_NUM_Y*PIXEL_NUM_Y + (tickLength2 - textBoxWidthX2*0.25),
                               x_offset+6*PIXEL_NUM_X,
                               ROC_NUM_Y*PIXEL_NUM_Y + (tickLength2 + textBoxWidthX2*0.75),
                               "NB")
        text2.AddText(xtickHCList[tick/8])
        axisLabels.append(text2)
    x_offset +=1*PIXEL_NUM_X

# - Add top rightmost tick
lineRightT = ROOT.TLine()
lineRightT.SetLineWidth(4)
lineRightT.DrawLine(ROC_NUM_X*PIXEL_NUM_X,
                    ROC_NUM_Y*PIXEL_NUM_Y,
                    ROC_NUM_X*PIXEL_NUM_X,
                    ROC_NUM_Y*PIXEL_NUM_Y + tickLength*2)

c.Update()

## Drawing lines between ROCs
# vertical
for x in range(8*PIXEL_NUM_X,ROC_NUM_X*PIXEL_NUM_X,8*PIXEL_NUM_X):
    lineX = ROOT.TLine()
    lineX.SetLineStyle(1)
    lineX.SetLineWidth(4)
    lineX.SetLineColor(1)
    if x == 32*PIXEL_NUM_X:
        lineX.SetLineWidth(8)
    lineX.DrawLine(x,-2*tickLength,x,ROC_NUM_Y*PIXEL_NUM_Y+tickLength*2)
# horizontal
for y in range(2*PIXEL_NUM_Y,ROC_NUM_Y*PIXEL_NUM_Y,2*PIXEL_NUM_Y):
    lineY = ROOT.TLine()
    lineY.SetLineStyle(1)
    lineY.SetLineWidth(4)
    lineY.SetLineColor(15) # grey-ish
    sep1 = (34, 56, 56+34, 56*2, 56*2+34)
    if y in [item*PIXEL_NUM_Y for item in sep1]:
        lineY.SetLineColor(1)
    if y%(56*PIXEL_NUM_Y)==0:
        lineY.SetLineWidth(8)
    lineY.DrawLine(0,y,ROC_NUM_X*PIXEL_NUM_X,y)

hTitle = ROOT.TPaveText(0,172*PIXEL_NUM_Y,64*PIXEL_NUM_X,185*PIXEL_NUM_Y,"NB")
title = "FPix {0} Distribution - Run_{1}".format("Bad Bumps",str(run))
hTitle.AddText(title)
hTitle.SetTextAlign(22)
hTitle.SetTextFont(62)
hTitle.SetFillColor(0)
hTitle.SetBorderSize(0)
hTitle.Draw()
c.Update()

for label in axisLabels:
    label.SetFillColor(0)
    label.SetTextAlign(22)
    label.SetTextFont(42)
    label.SetBorderSize(0)
    label.Draw()

c.SaveAs(os.path.join(run_dir,"{0}.png".format('-'.join(["FFpix","BB", plotType,str(run)]))))
#c.SaveAs(os.path.join(run_dir,"playground","oone.pdf")) # somehow saving to pdf always fail..
#c.Print(os.path.join(run_dir,"playground","oone.pdf"), "pdf")
