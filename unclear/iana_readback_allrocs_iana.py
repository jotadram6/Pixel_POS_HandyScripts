import argparse
from JMTTools import *

parser = argparse.ArgumentParser()

parser.add_argument('--dat-fn',
                    help='path to Readbacker.dat (default: taken from run dir)')
parser.add_argument('--old-dac-key',
                    help='the old dac key (default: taken from run dir PixelConfigurationKey.txt)')
parser.add_argument('--new-dac-key',
                    help='the new dac key (default: first available one generated)')
parser.add_argument('--pdf-fn',
                    help='the pdf fn (default in run dir)')
parser.add_argument('--insert-as', default='Default',
                    help='the new dac alias (default %(default)s)')
parser.add_argument('run', nargs=1, help='The run number.')
options = parser.parse_args()

options.run = int(options.run[0])
if options.run is None and (options.dat_fn is None or options.old_dac_key is None):
        raise ValueError('if run number, not in argv must supply --dat-fn and --old-dac-key')

if options.dat_fn is None:
    options.dat_fn = os.path.join(run_dir(options.run), 'Readbacker.dat')
if options.old_dac_key is None:
    options.old_dac_key = int(configurations_txt().from_run(options.run)['dac'])
if options.new_dac_key is None:
    options.new_dac_key, _ = new_config_key('dac')
if options.pdf_fn is None:
    options.pdf_fn = os.path.join(run_dir(options.run), 'iana_readback_allrocs_iana.pdf')

print 'run:', options.run
print 'dac keys:', options.old_dac_key, '->', options.new_dac_key
print 'output in', options.pdf_fn

################################################################################

from JMTROOTTools import *
from iana_readback_base import iana_adc_to_mA

def fit_iana_vs_vana(roc, vanas, ianas, eianas=None, target=24., fcn=None, fit_range=(25., 150.), draw=True, old_vana=None):
    '''Fit the curve using the calibration function for iana adc -> mA
    and extract the vana for which iana = target. If ianas is already
    floats, the calibration is already assumed done. The default fit
    fcn if not specified is a pol1 over a limited range. If draw is
    True, the fit etc. are drawn into the current pad. The return
    value includes the target vana, the graph, fit fcn and result, and
    graphics stuff. (The graphics stuff is returned so that it doesn't
    die before you canvas.SaveAs.)
    '''

    n = len(vanas)
    assert n == len(ianas)
    vanas = array('d', vanas)
    evanas = array('d', [0]*n)
    if all(type(x) == int for x in ianas):
        if eianas is None:
            eianas = array('d', [65./255]*n)
        ianas = array('d', [iana_adc_to_mA(x) for x in ianas])
    else:
        assert eianas is not None

    ret = {}
    g = ret['graph'] = ROOT.TGraphErrors(n, vanas, ianas, evanas, eianas)
    g.SetTitle('%s;Vana;Iana (mA)' % roc)
    g.SetMarkerStyle(20)
    g.SetMarkerSize(0.001)
    if draw:
        g.Draw('AP')

    if fcn is None:
        fcn = ROOT.TF1('fcn', 'pol1', *fit_range)
    fcn.SetLineWidth(1)
    fcn.SetLineColor(ROOT.kRed)
    ret['fcn'] = fcn
    fit_opt = 'RQS'
    if not draw:
        fit_opt += '0'
    ret['fit_result'] = g.Fit(fcn, fit_opt)

    ret['target'] = target
    vana = ret['vana'] = int(round(fcn.GetX(target)))
    if old_vana:
        old_iana = ret['old_iana'] = fcn.Eval(old_vana)
    if draw:
        new_ls = [ROOT.TLine(vana, 0, vana, target),  ROOT.TLine(0, target, vana, target)]
        old_ls = []
        if old_vana:
            old_ls = [ROOT.TLine(old_vana, 0, old_vana, old_iana),  ROOT.TLine(0, old_iana, old_vana, old_iana)]
        for c, ls in ((ROOT.kBlue, new_ls), (ROOT.kGreen+2, old_ls)):
            for l in ls:
                l.SetLineColor(c)
                l.Draw()

        t = ROOT.TLatex()
        t.SetTextSize(0.05)
        t.SetTextColor(ROOT.kBlue)
        t.DrawLatex(10, 56, 'Vana @ %i mA: %i' % (target, vana))
        t.SetTextColor(ROOT.kGreen+2)
        t.DrawLatex(10, 52, '@ Vana = %i,' % old_vana)
        t.DrawLatex(13, 48, 'Old Iana: %.1f mA' % old_iana)

        ROOT.gPad.Update()
        st = g.FindObject('stats')
        st.SetLineColor(ROOT.kRed)
        st.SetTextColor(ROOT.kRed)
        st.SetX1NDC(0.450)
        st.SetY1NDC(0.140)
        st.SetX2NDC(0.852)
        st.SetY2NDC(0.365)

        ret['graphics'] = new_ls + old_ls # don't need the ts

    return ret

####

import pickle

set_style()

dacs = dac_dats(options.old_dac_key)

rb = readbacker_dat_allrocs(options.dat_fn)

modules = rb.results_scan.keys()
modules.sort(key=name_sort_key)

c = ROOT.TCanvas('c', '', 1700, 1000)
c.Divide(5,4)

c.cd(0)
c.SaveAs(options.pdf_fn + '[')

module_results = defaultdict(dict)

h_delta_vana = ROOT.TH1F('h_delta_vana', ';#Delta Vana;rocs/1',  100, -50, 50)
h_delta_iana = ROOT.TH1F('h_delta_iana', ';#Delta Iana (mA);rocs/mA', 100, -50, 50)
h_fit_prob = ROOT.TH1F('h_fit_prob', ';fit prob;rocs/0.02', 50, 0, 1)

h_delta_vana_total = ROOT.TH1F('h_delta_vana_total', ';#Delta Vana;rocs/1',  100, -50, 50)
h_delta_iana_total = ROOT.TH1F('h_delta_iana_total', ';#Delta Iana (mA);rocs/mA', 100, -50, 50)
h_fit_prob_total = ROOT.TH1F('h_fit_prob_total', ';fit prob;rocs/0.02', 50, 0, 1)
h_iana_zerovana = ROOT.TH1F('h_iana_zerovana', ';iana at zero vana;rocs/0.2 mA', 50, 0, 10)

for i, module in enumerate(modules):
    for roc_i in sorted(rb.results_scan[module].keys()):
        roc_i = int(roc_i)
        
        roc_row = roc_i / 4
        roc_col = roc_i % 4
        c.cd(1 + roc_row * 5 + roc_col)
    
        vanas, ianas = [], []
        for vana in sorted(rb.results_scan[module][roc_i].keys()):
            vanas.append(vana)
	    ianas.append(rb.results_scan[module][roc_i][vana][roc_i].iana)
    
        old_vana = dacs[module]['%s_ROC%i' % (module, roc_i)]['Vana']
        ret = module_results[module][roc_i] = fit_iana_vs_vana('%s_ROC%i' % (module, roc_i), vanas, ianas, old_vana=old_vana)
    
        h_delta_vana.Fill(ret['vana'] - old_vana)
        h_delta_iana.Fill(ret['target'] - ret['old_iana'])
        h_fit_prob.Fill(ret['fit_result'].Prob())
    
	h_delta_vana_total.Fill(ret['vana'] - old_vana)
	h_delta_iana_total.Fill(ret['target'] - ret['old_iana'])
	h_fit_prob_total.Fill(ret['fit_result'].Prob())
	h_iana_zerovana.Fill(iana_adc_to_mA(ianas[0]))

        dacs[module]['%s_ROC%i' % (module, roc_i)]['Vana'] = ret['vana']

        if roc_i == len(rb.results_scan[module].keys()) - 1:
            for ih, h in enumerate((h_delta_vana, h_delta_iana, h_fit_prob)):
                pad = c.cd(5*(ih+1))
                h.SetTitle(module)
                h.Draw()
                pad.Update()
                st = h.FindObject('stats')
                st.SetOptStat(111110)
                st.SetY1NDC(0.6)

            c.cd(0)
            c.SaveAs(options.pdf_fn)
            for h in (h_delta_vana, h_delta_iana, h_fit_prob):
                h.Reset()
ROOT.gStyle.SetOptStat(111110)
h_delta_vana_total.Draw()
c.SaveAs(options.pdf_fn)
h_delta_iana_total.Draw()
c.SaveAs(options.pdf_fn)
h_fit_prob_total.Draw()
c.SaveAs(options.pdf_fn)
c.SaveAs(options.pdf_fn + ']')

c.Close()

c = ROOT.TCanvas('c', '', 800, 600)
h_iana_zerovana.Draw()
c.SaveAs(os.path.join(run_dir(options.run), 'h_iana_zerovana.png'))

#dacs.write(options.new_dac_key)

#cmd = '$BUILD_HOME/pixel/bin/PixelConfigDBCmd.exe --insertVersionAlias dac %i %s' % (options.new_dac_key, options.insert_as)
#print cmd
#os.system(cmd)

################################################################################

module_vana_dict = defaultdict(dict)
for module in module_results:
	for roc in module_results[module]:
		module_vana_dict['%s_ROC%i' % (module, roc)]['newvana'] = module_results[module][roc]['vana']
		module_vana_dict['%s_ROC%i' % (module, roc)]['oldvana'] = dacs[module]['%s_ROC%i' % (module, roc)]['Vana']
		module_vana_dict['%s_ROC%i' % (module, roc)]['oldiana'] = module_results[module][roc]['old_iana']

with open(os.path.join(run_dir(options.run), 'readback_iana.p'), 'wb') as handle:
    pickle.dump(module_vana_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
