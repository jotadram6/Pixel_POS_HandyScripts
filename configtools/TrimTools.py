import sys, os, cPickle
from array import array
from glob import glob
from collections import defaultdict
from pprint import pprint
from itertools import izip

BUILD_HOME = os.environ['BUILD_HOME']
POS_OUTPUT_DIRS = os.environ['POS_OUTPUT_DIRS']
PIXELCONFIGURATIONBASE = os.environ['PIXELCONFIGURATIONBASE']

class trimdat:
    def __init__(self,fn):
        self.fn = fn
        self.basefn = os.path.basename(fn)
        self.trims_by_roc = {}
        this_roc = None
        these_trims = {}
        def add():
            global these_trims, this_roc
        for line in open(fn):
            if line.startswith('ROC:'):
                if these_trims:
                    assert this_roc is not None
                    assert len(these_trims) == 52
                    self.trims_by_roc[this_roc] = these_trims
                this_roc = line.split()[-1]
                assert '_ROC' in this_roc
                these_trims = {}
                #print this_roc
            else:
                colname, trimvalues = line.split()
                assert colname.endswith(':')
                colname = colname.replace(':', '')
                column = int(colname.replace('col',''))
                these_trims[column] = trimvalues
                #print column, trimvalues                  
        assert this_roc is not None
        assert len(these_trims) == 52
        #assert set(these_trim.keys()) == set(self.DACS)
        self.trims_by_roc[this_roc] = these_trims
        #print len(self.trims_by_roc)
        assert len(self.trims_by_roc) == 16

    def write(self, f):
        if type(f) == str:
            fn = f
            f = open(fn, 'wt')
        elif type(f) == int:
            fn = os.path.join(PIXELCONFIGURATIONBASE, 'trim/' + str(f) + '/' + self.basefn)
            f = open(fn, 'wt')
        elif not hasattr(f, 'write'):
            raise TypeError("can't handle f %r" % f)

        rocs = self.trims_by_roc.keys()
        rocs.sort(key=lambda x: int(x.split('_ROC')[1]))
        for roc in rocs:
            f.write('ROC:     %s\n' % roc)
            trims = self.trims_by_roc[roc]
            for col in range(0,52):
                #print col,trims[col]
                if col < 10:
                    f.write(('col0'+str(col)+':').ljust(9))
                else:
                    f.write(('col'+str(col)+':').ljust(9))
                f.write('%s\n' % trims[col])
