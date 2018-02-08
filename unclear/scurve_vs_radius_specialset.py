#
# be careful about the run directory setings
#

from JMTTools import *
from JMTROOTTools import *
import collections
set_style(True)

#run = run_from_argv()
#run_dir = run_dir(run)
#run_dir="/data/tif/Run_BmO/Run_1898/"
run_dir = "/pixel/data1/FPix/Runs/Run_0/Run_{0}".format(sys.argv[1])
print run_dir
in_fn = glob(os.path.join(run_dir, 'total.root'))
if not in_fn:
    root_flist = glob(os.path.join(run_dir,'SCurve_Fed_*_Run_%s.root'%run)) 
    if not root_flist:
        raise RuntimeError('need to run analysis first!')
    out_root = os.path.join(run_dir,'total.root')
    args = ' '.join(root_flist)
    cmd = 'hadd %s %s' %(out_root, args)
    os.system(cmd)
in_fn = glob(os.path.join(run_dir, 'total.root'))
in_fn = in_fn[0]
out_dir = os.path.join(run_dir,'dump_scurve')
if not os.path.isdir(out_dir):
    os.system('mkdir -p -m 766 %s' %out_dir)

pdf_fn = os.path.join(out_dir, 'SCurve_simple-D1.pdf')

f = ROOT.TFile(in_fn)

#dirs = ['FPix/FPix_%(hc)s/FPix_%(hc)s_D%(dsk)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i/FPix_%(hc)s_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i' % locals() for hc in ['BmI', 'BmO', 'BpI', 'BpO'] for dsk in range(1,2) for bld in range(1,18) for pnl in range(1,3) for rng in range(1,3)]
dirs = []

myset = '''FPix_BpI_D1_BLD1_PNL1_RNG1
FPix_BpI_D1_BLD1_PNL1_RNG2
FPix_BpI_D1_BLD1_PNL2_RNG1
FPix_BpI_D1_BLD1_PNL2_RNG2
FPix_BpI_D1_BLD2_PNL1_RNG1
FPix_BpI_D1_BLD2_PNL1_RNG2
FPix_BpI_D1_BLD2_PNL2_RNG1
FPix_BpI_D1_BLD2_PNL2_RNG2
FPix_BpI_D1_BLD3_PNL1_RNG1
FPix_BpI_D1_BLD3_PNL1_RNG2
FPix_BpI_D1_BLD3_PNL2_RNG1
FPix_BpI_D1_BLD3_PNL2_RNG2
FPix_BpI_D1_BLD4_PNL1_RNG2
FPix_BpI_D1_BLD4_PNL2_RNG2'''
for x in myset.split():
    x = x.split('_')
    dirs.append('{0}/{1}/{2}/{3}/{4}/{5}'.format(x[0], '_'.join(x[:2]), '_'.join(x[:3]), '_'.join(x[:4]), '_'.join(x[:5]), '_'.join(x)))

#c = ROOT.TCanvas('c', '', 500, 500)
#c.Divide(2,1)

h1s = collections.defaultdict(list)
for d in dirs:
    if not f.Get(d): continue
    for key in f.Get(d).GetListOfKeys():
        obj = key.ReadObj()
        if not obj.GetName().endswith("Threshold1D"): continue
        #h1s.append(obj)
        h1s[obj.GetName().split('_ROC')[0]].append(obj.GetMean())

for k in h1s.keys():
    print "{1}".format(k, float(sum(h1s[k]))/len(h1s[k]))
    #print "{0}\t{1}".format(k, float(sum(h1s[k]))/len(h1s[k]))


#print "We have {0:d} ROCs.".format(len(h1s))
#
#if not len(h1s):
#    sys.exit("There is no ROCs in root file, exiting...")
#
#hROC_rng1 = collections.defaultdict(list)
#hROC_rng2 = collections.defaultdict(list)
#for h in h1s:
#    rocid = int(h.GetName().split('ROC')[1].split('_')[0])
#    if 'RNG1' in h.GetName():
#        hROC_rng1[rocid*(15-rocid)].append(h.GetMean())
#    elif 'RNG2' in h.GetName():
#        hROC_rng2[rocid*(15-rocid)].append(h.GetMean())
#
#print "==>RNG1"
#for index, _ in enumerate(sorted(hROC_rng1.keys(), reverse=True)):
#    print "{2}".format(index, _, float(sum(hROC_rng1[_]))/len(hROC_rng1[_]))
#print "==>RNG2"
#for index, _ in enumerate(sorted(hROC_rng2.keys(), reverse=True)):
#    print "{2}".format(index, _, float(sum(hROC_rng2[_]))/len(hROC_rng2[_]))


#if 'scp' in sys.argv:
#    remote_dir = 'public_html/qwer/dump_scurve_simple/%i' % run
#    cmd = 'ssh jmt46@lnx201.lns.cornell.edu "mkdir -p %s"' % remote_dir
#    print cmd
#    os.system(cmd)
#    cmd = 'scp -r %s/scurve_simple.pdf jmt46@lnx201.lns.cornell.edu:%s' % (run_dir, remote_dir)
#    print cmd
#    os.system(cmd)
