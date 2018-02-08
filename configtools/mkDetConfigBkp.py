import os,sys
from cablemap import *
from optparse import OptionParser

class MyParser(OptionParser):
    def format_epilog(self, formatter):
        return self.epilog
epi = '''
EXAMPLE:
    > python mkDetConfig.py --hc='BmO' --fed='1287 1289 1293'
    > python mkDetConfig.py --hc='BmO' --prt='1TA 1BD 2TB' (use --prt='1Ta 1BDd 2Tb' for BmO and BpI)
    > python mkDetConfig.py --hc='BmO' --dsk='1 3'
    > python mkDetConfig.py --hc='BmO' --exclude='FPix_BmO_D1_BLD6_PNL2_RNG1 FPix_BmO_D1_BLD7_PNL1_RNG1'
    > python mkDetConfig.py --hc='BmO' --fed='1290 1291' --prt='1BD 3TA' --exclude='FPix_BmO_D1_BLD6_PNL2_RNG1' # if both fed and prt arguements are provided, the logic is 'AND'.
'''

parser = MyParser(epilog=epi)
parser.add_option('','--hc',dest='hcs',help='Input which HC.')
parser.add_option('','--fed',dest='feds',help='Input fed list as string.')
parser.add_option('','--prt',dest='prts',help='Input portcard list as string.')
parser.add_option('','--dsk',dest='dsks',help='Input disk list as string')
parser.add_option('','--exclude',dest='ex',help='Input name list of module to be excluded as string')
parser.add_option('','--include',dest='icld',help='Input name list of module to be included as string')

(opts, args) = parser.parse_args()


def list2dat(lstall,fn,exlist=None):
    with open(fn, 'w') as output:
        output.write('Rocs:\n')
        for element in lstall:
            if exlist != None:
                if element not in exlist:
                    for x in xrange(16):
                        line = '{0}_ROC{1}\n'.format(element, str(x))
                        output.write(line)
                else:
                    for x in xrange(16):
                        # line = element+'_ROC%s'%str(x)+' '+'noAnalogSignal'+'\n'
                        line = "{0:35}{1}\n".format('{0}_ROC{1}'.format(element, str(x)),
                                                   'noAnalogSignal')
                        output.write(line)
            else:
                for x in xrange(16):
                    line = '{0}_ROC{1}\n'.format(element, str(x))
                    output.write(line)

def mkNewConfigVersion(configName):
    configBaseDir = os.environ['PIXELCONFIGURATIONBASE']
    os.chdir(os.path.join(configBaseDir, configName))
    subdirs = [int(x) for x in os.walk('.').next()[1]]
    subdirs.sort()
    lastVersion = subdirs[-1]
    #print "Last %s version: "%configName, lastVersion
    newVersion = subdirs[-1]+1
    os.system('mkdir -m 777  %d'%newVersion)
    os.chdir('%d'%newVersion)
    print "New %s version: "%configName, newVersion
    return newVersion

def setAsDefault(configName, version):
    cdb = "{0}/pixel/PixelConfigDBInterface/test/bin/linux/x86_64_slc6/PixelConfigDBCmd.exe".format(os.environ['BUILD_HOME'])
    args = " --insertVersionAlias "+configName+" "+str(version)+" Default"
    print cdb+args
    os.system(cdb+args)



def main():
    if not opts.hcs:
       print "please input a hc name this way: --hc='BmO' (for example)"
       sys.exit(1)
    # configBaseDir = os.environ['PIXELCONFIGURATIONBASE']
    # if opts.hcs not in configBaseDir: print "your hc name doesn't match what's in PIXELCONFIGURATIONBASE, did you resource startanalysistab.sh to switch to another hc?"

    # hcname = opts.hcs[0].upper()+opts.hcs[1].lower()+opts.hcs[-1].upper()
    hcnames = [x[0].upper()+x[1].lower()+x[2].upper() for x in opts.hcs.split(' ')]
    cableMap_Fn='cablingmap_FPix.csv'
    #cableMap_Fn='cablingmap_fpixphase1_BpO.csv'
    dictionary = getdict(filename='csv/'+cableMap_Fn)

    moduleListByFed = []
    moduleListByPrt = []
    moduleListByDsk = []
    includelist = []

    config = 'detconfig'
    newVersion = mkNewConfigVersion(config)

    if opts.feds:
         fedlist = opts.feds.split(' ')
         moduleListByFed=[item['Official name of position'] for item in dictionary if item['FED ID'] in fedlist]
    if opts.prts:
        prtlist = opts.prts.split(' ')
        prtlist = [x[0]+x[1].upper()+x[2].lower() for x in prtlist]
        moduleListByPrt=[item['Official name of position'] for item in dictionary if item['PC position phi'] in prtlist]
    if opts.dsks:
        dsklist = opts.dsks.split(' ')
        moduleListByDsk=[item['Official name of position'] for item in dictionary if len(item['Official name of position'].split('_'))>3 and item['Official name of position'].split('_')[2][-1] in dsklist]

    if opts.icld:
        includelist = opts.icld.split(' ')

    if len(moduleListByPrt)>0 and len(moduleListByFed)>0:
        moduleList = [m for m in moduleListByPrt if m in moduleListByFed]
        moduleList = moduleList + moduleListByDsk + includelist
    else:
        moduleList = moduleListByFed + moduleListByPrt + moduleListByDsk + includelist
    moduleList = sorted(set(moduleList))

    if opts.ex:
        exlist = opts.ex.split(' ')
        if opts.feds or opts.prts or opts.dsks or opts.icld:
            moduleList = [module for module in moduleList if module not in exlist]
            moduleList = [md for md in moduleList if md.split('_')[1] in hcnames]
            list2dat(moduleList, 'detectconfig.dat')
        else:
            moduleList = sorted([item['Official name of position'] for item in dictionary])
            moduleList = [md for md in moduleList if md.split('_')[1] in hcnames]
            list2dat(moduleList, 'detectconfig.dat', exlist)
    else:
        moduleList = [md for md in moduleList if md.split('_')[1] in hcnames]
        list2dat(moduleList, 'detectconfig.dat')


    save = raw_input("Do you want to set new version <%s/%d> as default? (y/N)?\n"%(config,newVersion))

    if save.lower() in ['n','no']:
        save = False
    elif save.lower() in ['y','yes']:
        save = True

    if save:
        setAsDefault(config, newVersion)

if __name__ == "__main__":
    main()
