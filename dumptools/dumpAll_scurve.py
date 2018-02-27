#!/bin/python

import commands as cmd
PWD = cmd.getoutput('pwd')
sys.path.append(os.path.join(PWD,"common/"))
sys.path.append(os.path.join(PWD,"configtools/"))
from JMTTools import *
from JMTROOTTools import *
from write_other_hc_configs import cable_map_parser, HC, module_sorter_by_portcard_phi
set_style(light=True)

#if len(sys.argv) < 2:
#    print 'usage: scurve.py in_fn out_fn'
#    sys.exit(1)

run = run_from_argv()
run_dir = run_dir(run)

if len(sys.argv) == 2:
	in_fn = glob(os.path.join(run_dir, 'total.dat'))
	if not in_fn:
	    trim_flist = glob(os.path.join(run_dir,'TrimOutputFile_Fed_*.dat'))
	    if not trim_flist:
	        raise Runtimeerror('Run analysis first!')
	    out_dat = os.path.join(run_dir,'total.dat')
	    args = ' '.join(trim_flist)
	    cmd  = 'cat %s > %s'%(args,out_dat)
	    os.system(cmd)
	
	in_fn = glob(os.path.join(run_dir, 'total.dat'))
        out_dir = outdir_from_argv()
        if out_dir is not None:
                out_dir = os.path.join(out_dir, 'dump_scurve')
        else:
                out_dir = os.path.join(run_dir, 'dump_scurve')
        print "Generating output in:", out_dir
	cable_map = cable_map_parser()
elif len(sys.argv) == 3:
	''' python dumpAll_scurve.py 123 '1333' '''
	fednum = sys.argv[2]
	in_fn = glob(os.path.join(run_dir, 'TrimOutputFile_Fed_{0}.dat'.format(fednum)))
        out_dir = outdir_from_argv()
        if out_dir is not None:
                out_dir = os.path.join(out_dir, 'dump_scurve_FED{0}'.format(fednum))
        else:
                out_dir = os.path.join(run_dir, 'dump_scurve_FED{0}'.format(fednum))
        print "Generating output in:", out_dir
	cable_map = cable_map_parser(-1,int(fednum))
else:
	sys.exit("I dont know what you want. I need either a run number or a run+fed number:\n Examples:\n ./dumpAll_scurve.py 123 \n python dumpAll_scurve.py 123 '1294'")

in_fn = in_fn[0]
if not os.path.isdir(out_dir):
    os.system('mkdir -p -m 766 %s' %out_dir)

#in_fn = sys.argv[1]
#out_fn = sys.argv[2]

td = trim_dat(in_fn)

default_l = [0]*4160
threshold_c, width_c = None, None
#threshold_out_fn = out_fn + '.thresholds.pdf'
#width_out_fn = out_fn + '.widths.pdf'
threshold_out_fn = os.path.join(out_dir,'SCurve_threshold.root')
width_out_fn = os.path.join(out_dir,'SCurve_widths.root')


thresholdsCanvasList = []
widthsCanvasList = []
for module in cable_map.modules_from_rocs(td.ls.keys(), module_sorter_by_portcard_phi):
    print module.name
    thresholdses = []
    widthses = []
    for i in xrange(16):
        roc = '%s_ROC%i' % (module.name, i)
        es = td.ls.get(roc, None)
        if es is None:
            thresholds = default_l
            widths = default_l
        else:
            thresholds, widths = [], []
            for e in es:
                if e == 0:
                    thresholds.append(0)
                    widths.append(0)
                else:
                    thresholds.append(e.th)
                    widths.append(e.sg)
        thresholdses.append(thresholds)
        widthses.append(widths)

    title = module.portcard+' '+module.portcard_phi[1]+' '+str(module.portcard_connection)+'   '+module.name+'   '+module.module+'  '+module.internal_name
    h_thresholdses = flat_to_module('thresholds', module.name, thresholdses)
    h_thresholds, fc, pt = fnal_pixel_plot(h_thresholdses, module.name, title, (20, 50), threshold_c)
    thresholdsCanvasList.append((fc, pt))

    h_widthses = flat_to_module('widths', module.name, widthses)
    h_widths, fc, pt = fnal_pixel_plot(h_widthses, module.name, title, (0, 10), width_c)
    widthsCanvasList.append((fc, pt))

thresholdFile = ROOT.TFile(threshold_out_fn, 'RECREATE')
for x in thresholdsCanvasList:
    x[0].Write()
    x[1].Draw()
thresholdFile.Close()
widthFile = ROOT.TFile(width_out_fn, 'RECREATE')
for x in widthsCanvasList:
    x[0].Write()
    x[1].Draw()
widthFile.Close()
