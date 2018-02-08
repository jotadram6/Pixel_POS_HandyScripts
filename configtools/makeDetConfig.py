import os,sys,csv
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
    Every option is AND besides --include or --exclude
'''

parser = MyParser(epilog=epi)
parser.add_option('','--hc',dest='hcs',help='Input which HC.')
parser.add_option('','--fed',dest='feds',help='Input fed list as string.')
parser.add_option('','--fedTB',dest='fedsTB',help='t for FED top connector, b for FED bottom connector.')
parser.add_option('','--fiber',dest='fibers',help='FED fiber.')
parser.add_option('','--prt',dest='prts',help='Input portcard list as string.')
parser.add_option('','--dsk',dest='dsks',help='Input disk list as string')
parser.add_option('','--dskIO',dest='dsksIO',help='1 for inner disk, 2 for outer disk')
parser.add_option('','--ccu',dest='ccus',help='Input ccu list as string - as 0xAB')
parser.add_option('','--lv',dest='lvs',help='Input LV group, parse as ABCD (A=disk=1-3, B=portcard position=1-4,C=top/bottom=T-B, D=LV group=1,2 (1=odd ports, 2=even ports))')
parser.add_option('','--hv',dest='hvs',help='Input HV group, parse as ABC (A=1-3, B=1-4,C=1,2)')
parser.add_option('','--fec',dest='fecs',help='Input FEC ID')
parser.add_option('','--mfec',dest='mfecs',help='Input mfec - need to be together with FEC ID')
parser.add_option('','--cooling',dest='coolings',help='Input cooling loop as aB (a=+/-z=p-m, B=loopID per side=A-D)')
parser.add_option('','--exclude',dest='ex',help='Input name list of module to be excluded as string')
parser.add_option('','--include',dest='icld',help='Input name list of module to be included as string')

(opts, args) = parser.parse_args()

def getdict(filename='csv/cablingmap_fpixphase1_BpI.csv'):
    rows = []
    with open(filename, mode='r') as infile:
         reader = csv.DictReader(infile)
         for row in reader:  
             rows.append(row)
    return rows


def list2dat(lst,fn):
    with open(fn, 'w') as output:
        output.write('Rocs:\n')
        for element in lst:
            for x in range(16):
                line = element+'_ROC%s'%str(x)+'\n'
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
    cdb = "~tif/TriDAS/pixel/PixelConfigDBInterface/test/bin/linux/x86_64_slc6/PixelConfigDBCmd.exe "
    args = "--insertVersionAlias "+configName+" "+str(version)+" Default"
    print cdb+args
    os.system(cdb+args)



def main():
    configBaseDir = os.environ['PIXELCONFIGURATIONBASE']

    cableMap_Fn='csv/cablingmap_FPix.csv'
    dictionary = getdict(filename=''+cableMap_Fn)
    
    includelist = []
    moduleList1 = []
    moduleList2 = []
    
    if opts.feds:
        list1 = opts.feds.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if item['FED ID'] in list1]
    if opts.fedsTB:
        list2 = opts.fedsTB.split(' ')
        moduleList2=[item['Official name of position'] for item in dictionary if item['FED receiver'] in list2]

    if len(moduleList1)>0 and len(moduleList2)>0:
        moduleList = [m for m in moduleList1 if m in moduleList2]
    else:
        moduleList = moduleList1 + moduleList2

    if opts.fibers:
        list1 = opts.fibers.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if item['FED Fiber'] in list1]
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.prts:
        list1 = opts.prts.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if item['PC position phi'] in list1]
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.dsks:
        list1 = opts.dsks.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if len(item['Official name of position'].split('_'))>3 and item['Official name of position'].split('_')[2][-1] in list1]
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.dsksIO:
        list1 = opts.dsksIO.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if len(item['Official name of position'].split('_'))>3 and item['Official name of position'].split('_')[5][-1] in list1]
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.ccus:
        list1 = opts.ccus.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if item['CCU'] in list1]
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.lvs:
        list1 = opts.lvs.split(' ')
        moduleList1 = []
        for item in dictionary:
            if len(item['Filterboard module power ID'].split('_'))>1:
                for element in list1:
                    if element[0] != item['Filterboard module power ID'].split('_')[0][-1]:
                        continue
                    if element[1] != item['Filterboard module power ID'].split('_')[1][-1]:
                        continue
                    if element[2] != item['PC position phi'][1]:
                        continue
                    if int(element[3])%2 != int(item['PC port'])%2:
                        continue
                    moduleList1.append(item['Official name of position'])
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.hvs:
        list1 = opts.hvs.split(' ')
        moduleList1 = []
        for item in dictionary:
            if len(item['HV group'].split('-'))>2:
                for element in list1:
                    if element[0] != item['HV group'].split('-')[0][-1]:
                        continue
                    if element[1] != item['HV group'].split('-')[1][-1]:
                        continue
                    if element[2] != item['HV group'].split('-')[2][-1]:
                        continue
                    moduleList1.append(item['Official name of position'])
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.fecs:
        list1 = opts.fecs.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if item['FEC ID'] in list1]
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.mfecs:
        list1 = opts.mfecs.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if item['mfec'] in list1]
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.coolings:
        list1 = opts.coolings.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if item['Cooling loop'] in list1]
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList

    if opts.hcs:
        list1 = opts.hcs.split(' ')
        moduleList1=[item['Official name of position'] for item in dictionary if len(item['Official name of position'].split('_'))>1 and item['Official name of position'].split('_')[1] in list1]
    if len(moduleList1)>0 and len(moduleList)>0:
        moduleList = [m for m in moduleList1 if m in moduleList]
    else:
        moduleList = moduleList1 + moduleList
    
    if opts.icld:
        includelist = opts.icld.split(' ')
    moduleList = moduleList + includelist

    moduleList = sorted(set(moduleList))

    if opts.ex:
        exlist = opts.ex.split(' ')
        moduleList = [module for module in moduleList if module not in exlist]
    
    config = 'detconfig'
    #print len(moduleList),moduleList
    newVersion = mkNewConfigVersion(config)
    
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
