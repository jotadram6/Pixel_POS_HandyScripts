import os, sys
from cablemap import getdict
from optparse import OptionParser

class MyParser(OptionParser):
    def format_epilog(self, formatter):
        return self.epilog
epi = '''
LOGIC:
    Any combination(0,1,2...) of hc/fed/prt/dsk would be AND.
    If --include present, result = Above OR include.
    If --exclude present with others, result = Above - Above AND exclude,
    Else, result = All - exclude.

EXAMPLE:
    --hc    ='BmO bpi'
    --fed   ='1302 1298'
    --prt   ='1a 3td' ('1a': PC1A, '3td': PC3D top only)
    --dsk   ='1 2'

    --exclude   ='Bmo-1-3-2-2 bpi-2-11-1-2'
    --include   ='BmI-1-5-1-2'

# Upper/Lowercase does not matter
# Module specification: <HC>-<D>-<BLD>-<PNL>-<RNG>
'''

parser = MyParser(epilog=epi)
parser.add_option('','--hc',dest='hcs',help='HC list')
parser.add_option('','--fed',dest='feds',help='FED list as string')
parser.add_option('','--prt',dest='prts',help='Portcard list as string')
parser.add_option('','--dsk',dest='dsks',help='Disk list as string')
parser.add_option('','--exclude',dest='ex',help='Module list to be excluded as string')
parser.add_option('','--include',dest='il',help='Module list to be included as string')
parser.add_option('','--mode', dest='mode', default='ON',help='Selected modules\' action. Can be ON/OFF. Default is ON')
parser.add_option('','--maskWord', dest='mword',default='noInit',help="Choose ROC's mask word. Can be 'noAnalogSignal' or 'noInit'. Default is 'noInit'")

(opts, args) = parser.parse_args()


def hcFormater(l):
    res =[]
    for e in l:
        if e.lower() not in ['bmi','bmo','bpi','bpo']:
            sys.exit("Wrong HC code, check again!")
        res.append(e[0].upper()+e[1].lower()+e[2].upper())
    return res

def prtFormater(l):
    res = []
    for e in l:
        if e[0] not in ['1','2','3'] and\
           e[-1].lower() not in ['a','b','c','d']:
            sys.exit("Portcard format incorrect, check again!")
        if len(e) == 2: # 1a -> 1Ta, 1Ba
            res.append(e[0]+'T'+e[-1].lower())
            res.append(e[0]+'B'+e[-1].lower())
        elif len(e) == 3: # 1ba -> 1Ba
            if e[1].lower() not in ['t','b']:
                sys.exit("Portcard format incorrect, check again!")
            res.append(e[0]+e[1].upper()+e[2].lower())
    return sorted(set(res))

def moduleFormater(l):
    res = []
    for e in l:
        try:
            hc,dsk,bld,pnl,rng = e.split('-')
        except:
            sys.exit("Module input format incorrect, check again!")
        hc = hcFormater([hc])[0]
        res.append('FPix_{0}_D{1}_BLD{2}_PNL{3}_RNG{4}'.format(hc,dsk,bld,pnl,rng)) # FPix_BmO_D3_BLD10_PNL1_RNG2
    return res

def moduel2detConfig(m, status=''):
    res = ''
    for x in xrange(16):
        res += "{0:35}{1}\n".format('{0}_ROC{1}'.format(m,str(x)),
                                    status)
    return res


def mkNewConfigVersion(configName):
    configBaseDir = os.environ['PIXELCONFIGURATIONBASE']
    os.chdir(os.path.join(configBaseDir, configName))
    subdirs = [int(x) for x in os.walk('.').next()[1]]
    subdirs.sort()
    lastVersion = subdirs[-1]
    print "Last %s version: "%configName, lastVersion
    newVersion = subdirs[-1]+1
    os.system('mkdir -m 777  %d'%newVersion)
    os.chdir('%d'%newVersion)
    print "New  %s version: "%configName, newVersion
    return newVersion

def setAsDefault(configName, version):
    cdb = "{0}/pixel/PixelConfigDBInterface/test/bin/linux/x86_64_centos7/PixelConfigDBCmd.exe ".format(os.environ['BUILD_HOME'])
    args = "--insertVersionAlias "+configName+" "+str(version)+" Default"
    print cdb+args
    os.system(cdb+args)



def main():
    if opts.hcs:
        hcList = hcFormater(opts.hcs.split())
    if opts.prts:
        prtList = prtFormater(opts.prts.split())
    if opts.feds:
        fedList = opts.feds.split()
    if opts.dsks:
        dskList = opts.dsks.split()

    if opts.ex:
        exList = moduleFormater(opts.ex.split())
    if opts.il:
        ilList = moduleFormater(opts.il.split())

    if opts.mode:
        if opts.mode.upper() not in ['ON','OFF']:
            sys.exit("Mode can only be ON/OFF. Check again!")
    if opts.mword:
        if opts.mword not in ['noAnalogSignal','noInit']:
            sys.exit("Maskword can only be noAnalogSignal/noInit. Check again!")


    cableMap_Fn='cablingmap_FPix.csv'
    dictionary = getdict(filename='csv/'+cableMap_Fn)
    config = 'detconfig'
    newVersion = mkNewConfigVersion(config)
    msg = "Selected:\n"

    if 'prtList' in locals():
        moduleByPrt=[item['Official name of position'] for item in dictionary\
                  if item['PC position phi'] in prtList]
    if 'fedList' in locals():
        moduleByFed=[item['Official name of position'] for item in dictionary\
                  if item['FED ID'] in fedList]

    moduleSelected = [item['Official name of position'] for item in dictionary]
    if 'moduleByPrt' in locals():
        moduleSelected = [m for m in moduleSelected if m in moduleByPrt]
        msg += "- Modules on {0}. AND\n".format(str(prtList))
    if 'moduleByFed' in locals():
        moduleSelected = [m for m in moduleSelected if m in moduleByFed]
        msg += "- Modules on {0}. AND\n".format(str(fedList))
    if 'dskList' in locals():
        moduleSelected = [m for m in moduleSelected if m.split('_')[2][-1] in dskList]
        msg += "- Modules on {0}. AND\n".format(str(dskList))
    if 'hcList' in locals():
        moduleSelected = [m for m in moduleSelected if m.split('_')[1] in hcList]
        msg += "- Modules on {0}. AND\n".format(str(hcList))

    if any([x in locals() for x in ['hcList','prtList','fedList','dskList']]):
        if 'ilList' in locals():
            moduleSelected = sorted(set(moduleSelected+ilList))
            msg += "With modules {0}\n".format(str(ilList))
        if 'exList' in locals():
            moduleSelected = [m for m in moduleSelected if m not in exList]
            msg += "Without modules {0}\n".format(str(exList))
    else:
        if 'ilList' in locals():
            moduleSelected = ilList
            msg += "With modules {0}\n".format(str(ilList))
            if 'exList' in locals():
                moduleSelected = [m for m in moduleSelected if m not in exList]
                msg += "Without modules {0}\n".format(str(exList))
        elif 'exList' in locals():
            moduleSelected = [m for m in moduleSelected if m not in exList]
            msg += "All without modules {0}\n".format(str(exList))
        else:
            print("No arguments provided, all ROCs are selected.")
            msg += "All\n"

    moduleAll = [item['Official name of position'] for item in dictionary]

    with open('detectconfig.dat','w') as output:
        output.write('Rocs:\n')
        if opts.mode.upper() == 'ON': # Chosen ON mode, default
            for m in moduleAll:
                if m in moduleSelected:
                    output.write(moduel2detConfig(m))
                else:
                    output.write(moduel2detConfig(m, opts.mword))
            msg += "==> Selected are turned ON"
        elif opts.mode.upper() == 'OFF': # Chosen OFF mode
            for m in moduleAll:
                if m in moduleSelected:
                    output.write(moduel2detConfig(m, opts.mword))
                else:
                    output.write(moduel2detConfig(m))
            msg += "==> Selected are turned OFF"

    print '-'*79
    print msg
    print '-'*79

    save = raw_input("Do you want to set new version <%s/%d> as default? (y/N)?\n"%(config,newVersion))

    if save.lower() in ['n','no']:
        save = False
    elif save.lower() in ['y','yes']:
        save = True

    if save:
        setAsDefault(config, newVersion)

if __name__ == "__main__":
    main()
