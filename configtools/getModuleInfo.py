import os,sys,csv
from optparse import OptionParser

class MyParser(OptionParser):
    def format_epilog(self, formatter):
        return self.epilog
epi = '''
EXAMPLE:
    > python getModuleInfo.py --fed='1300' --fedch='6'
    > python getModuleInfo.py --fed='1300' --fiber='20'
    > python getModuleInfo.py --fed='1300 1296' --fiber='20 2'
    > python getModuleInfo.py --module='FPix_BmO_D1_BLD6_PNL2_RNG1 FPix_BmO_D1_BLD7_PNL1_RNG1'
      If multiple arguments are given, an OR is used.
      You can parse either fed + fedch, fed+fiber, or module
'''

parser = MyParser(epilog=epi)
parser.add_option('','--fed',dest='feds',help='Input fed as string.')
parser.add_option('','--fiber',dest='fibers',help='Input fiber as string.')
parser.add_option('','--fedch',dest='fedchs',help='Input fedch as string')
parser.add_option('','--module',dest='modules',help='Input name module as string')

(opts, args) = parser.parse_args()

def getdict(filename='csv/cablingmap_fpixphase1_BpI.csv'):
    rows = []
    with open(filename, mode='r') as infile:
         reader = csv.DictReader(infile)
         for row in reader:  
             rows.append(row)
    return rows


def main():
    
    cableMap_Fn='csv/cablingmap_FPix.csv'
    dictionary = getdict(filename=''+cableMap_Fn)
     
    moduleListByFed = []
    moduleListByFedCh = []
    moduleListByFiber = []
    moduleListModule = []

    if not opts.modules and not opts.feds:
        print "either give module as input or FED + fiber/FEDchannel"
        sys.exit(1)
    if opts.modules and opts.feds:
        print "give only module as input OR FED + fiber/FEDchannel, but not both"
        sys.exit(1)
    if opts.feds and opts.fedchs and opts.fibers:
        print "enter only fed channel or fiber number"
        sys.exit(1)
    if opts.feds and not opts.fedchs and not opts.fibers:
        print "enter fed channel or fiber number"
        sys.exit(1)
    if opts.feds:
         fedlist = opts.feds.split(' ')
         moduleListByFed=[item['Official name of position'] for item in dictionary if item['FED ID'] in fedlist]
    if opts.fedchs:
        fedchslist = opts.fedchs.split(' ')
        moduleListByFedCh=[item['Official name of position'] for item in dictionary for element in item['FED channel'].split('/') if element in fedchslist]
    if opts.fibers:
        fiberlist = opts.fibers.split(' ')
        for item in dictionary:
            for element in item['FED channel'].split('/'):
                try:
                    int(element)
                    if int(element)%2==0:
                        fiber = str(int(element)/2)
                        if fiber in fiberlist:
                            moduleListByFiber.append(item['Official name of position'])
                except ValueError:
                    continue

    if opts.modules:
        moduleListModule = opts.modules.split(' ')

    if len(moduleListByFedCh)>0 and len(moduleListByFed)>0:
        moduleList = [m for m in moduleListByFedCh if m in moduleListByFed]
    elif len(moduleListByFiber)>0 and len(moduleListByFed)>0:
        moduleList = [m for m in moduleListByFiber if m in moduleListByFed]
    else:
        moduleList = moduleListModule
    moduleList = sorted(set(moduleList))

    for item in dictionary:
        if item['Official name of position'] in moduleList:
            print "Module ",item['Official name of position']," FED",item['FED ID'],"FEDch",item['FED channel']," FEC",item['FEC ID'],"mfec",item['mfec'],"mfecch",item['mfecchannel']," PC",item['PC position phi'],"port",item['PC port'],"hub",item['HubID']," ccu",item['CCU'],item['CCU channel'],"dcdc",item['DCDC J11/J12']


if __name__ == "__main__":
    main()
