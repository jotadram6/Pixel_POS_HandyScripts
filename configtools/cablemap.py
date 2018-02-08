# list of keys
# {'DOH A/B': '', '': '', 'POH SN': '', 'mfecchannel': '', 'CCU': '03 (v1)', 'PC position Mirror': '', 'internal disk name': '', 'POH fiber color': '', 'FEC position': '', 'PP0 Adapter/FED': 'CCU+tFEC', 'DCDC channel': '', 'flex cable': '', 'PP0 Adapter/FEC': '-z up left 1', 'PC position phi': '', 'POH board': '', 'PC port': '', 'internal POH no': '', 'FED receiver': '', 'FED position': '', 'FED channel': '', 'channel': '', 'internal naming per Disk': '', 'DCDC name': '', 'POH Bundle': '', 'DCDC J11/J12': '', 'PC name': '', 'Official name of position': '', 'FEC ID': '', 'DOH bundle': '17', 'FED ID': '', 'Filterboard DCS': '', 'Filterboard module power': 'CI-B 008', 'DCDC': '', 'PP0 Ad.Slot/FEC': '1', 'PP0 Ad.Slot/FED': '', 'PC identifier': '', 'Module': '', 'HubID': '', 'mfec': '', 'FEC/FED crate': '', 'DOH QR': '30201210004685'}

import csv
import math
import os
from itertools import islice

def getdict(filename='csv/cablingmap_FPix.csv'):
    rows = []
    with open(filename, mode='r') as infile:
         reader = csv.DictReader(infile)
         for row in reader:  
             rows.append(row)
    return rows

def printnametranslation(xmlfilename):
    dictionary = getdict(xmlfilename)
    nametranslationfile = open("ConfigDat/translation.dat","w")
    nametranslationfile.write("#name                              A/B   FEC       mfec      mfecch    hubid     port      rocid     FEDid     FEDch     roc# \n")
  
    for row in dictionary:
        fedch=''
        fedchs=row['FED channel'].split('/')
        if len(fedchs)<2:continue
        for x in range(16):
            tbmcore = 'A'
            rocn=0
            if x < 8:
               tbmcore= 'A'
               fedch=fedchs[0]
               rocn=x
            else:
               tbmcore= 'B'
               fedch=fedchs[1]
               rocn=x-8
            
            i,d = math.modf(float(x)/4.0)
            towrite=row['Official name of position']+'_ROC%s'%str(x)+'         '+tbmcore +'        '+row['FEC position']+'      '+row['mfec']+'     '+row['mfecchannel'] +'     '+row['HubID']+'      '+ '%i'%d +'      '+ str(x) + '      '+row['FED ID']+'       '+ fedch+'     '+str(rocn)+'\n'
            nametranslationfile.write(towrite)

#def printportcardmap(xmlfilename):
#    dictionary = getdict(xmlfilename)
#    portcardmapfile=open("ConfigDat/portcardmap.dat","w")
#    portcardmapfile.write("# Portcard             Module                     AOH channel") 
#
#    for row in dictionary:
#        fedch=''
#        fedchs=row['FED channel'].split('/')
#        if len(fedchs)<2:continue
#        portcard=list(row['PC position Mirror'])[-1]
#        print portcard
#        towrite='FPix_BmO_D1_PRT'+'           '+row['Official name of position']  

def printPortcardMap(csv='csv/cablingmap_fpixphase1_BpI.csv'):
    dictionary = getdict(csv)
    pcList = ['FPix_BpI_D%(dsk)d_PRT%(prt)d' %locals() for dsk in range(2,4) for prt in range(1,5)]
    with open('ConfigDat/portcardmap.dat','w') as output:
        output.write('# Portcard             Module                     AOH channel\n')
        for x in pcList:
            d = x.split('_')[2][-1]
            p = x.split('_')[3][-1]
            p = chr(int(p)+96)
            moduleList = [(m['Official name of position'],m['PC position phi'][1],m['PC port']) for m in dictionary if m['PC position phi'][0]==d and m['PC position phi'][-1]==p]
            for m in moduleList:
                if m[1]=='T':
                    ch = int(m[2])+7
                elif m[1]=='B':
                    ch = int(m[2])
                line1 = '{0:23}{1:27}{2:>3}{3:8d}\n'.format(x,m[0],'A',ch)
                line2 = '{0:23}{1:27}{2:>3}{3:8d}\n'.format(x,m[0],'B',ch)
                output.write(line1)
                output.write(line2)


def mapfedidPOHbundle(bundlenumber):
    dictionary = getdict('csv/cablingmap_fpixphase1_BmO.csv')
    for row in dictionary:
        if len(row['POH SN'].split('/'))<2:continue
        if bundlenumber is int(row['POH SN'].split('/')[1].strip("0")):
           print 'bundlenumber:'+str(bundlenumber)+ ':FED position:'+row['FED position']+':FED receiver:'+row['FED receiver']
           break
        else:
           print 'test'
           break

def mapDOHbundle(bundlenumber):
    dictionary = getdict('csv/cablingmap_fpixphase1_BmO.csv')
    for row in dictionary:
        if len(row['POH SN'].split('/'))<2:continue
        if bundlenumber is int(row['POH SN'].split('/')[1].strip("0")):
           print 'bundlenumber:'+str(bundlenumber)+ ':FED position:'+row['FED position']+':FED receiver:'+row['FED receiver']
           break

def printfecconfig(xmlfilename):
    dictionary = getdict(xmlfilename)
    portcardmapfile=open("ConfigDat/fecconfig.dat","w")
    portcardmapfile.write("#FEC number    crate     vme base address     type    URI")
    portcardmapfile.write('\n')
    portcardmapfile.write("1               1         0x60000000           CTA     chtcp-2.0://cmsuppixch:10203?target=devpxfec:50001")
    
def printdetconfig(xmlfilename):
    dictionary =  getdict(xmlfilename)
    detconfigfile=open("ConfigDat/detconfig.dat","w")
    for row in dictionary:
        if row['Official name of position']=='':
            break;
        for x in range(16):
            towrite=row['Official name of position']+'_ROC%s'%str(x)+'\n'
            detconfigfile.write(towrite)
    
def printfedconfig(xmlfilename):
    dictionary =  getdict(xmlfilename)
    fedconfigfile=open("ConfigDat/fedconfig.dat","w")
    fedconfigfile.write("#FED number     crate     vme base address     type    URI")
    fedconfigfile.write('\n')
    elements_fedID=[]
    for row in dictionary:
        if(row['FED ID'] not in elements_fedID):
            elements_fedID.append(row['FED ID'])
    host=raw_input("Please input host computer in format 'localhost:10203'for FED:")
    target=raw_input("Please input target fed in format 'fed' (assuming port is 50001 for debug info):") 
    for x in elements_fedID:
        if x=='':
            continue;    
        towrite=str(x)+'     '+row['FEC/FED crate']+'     '+str(x)+'     '+'CTA'+'chtcp-2.0://'+host+'?target='+target+str(x)+':50001'+'\n'
        fedconfigfile.write(towrite)

def printBmIdcdc():
    for x in range(3):
       for y in range(4):
           dcdcconfigfilename='ConfigDat/dcdc/dcdc_FPix_BmI_D%s'%str(x+1)+"_PRT%s"%str(y+1)+".dat"
           dcdcconfigfile=open(dcdcconfigfilename,"w")
           dcdcconfigfile.write("Enabled: no"+"\n"+"CCUAddressEnable: 0x7e"+"\n"+"CCUAddressPgood: 0x7d"+"\n"+"PIAChannelAddress: 0x30"+"\n"+"PortNumber: 2"+'\n')

def printtbm(xmlfilename):
    dictionary =  getdict(xmlfilename)
    elements_tbmdelay=[]
    for row in dictionary:
        tbm_row=row['Official name of position']
        if tbm_row=='':
            continue;
        FPix, B_PorM_IorO, Disk,BLD,PNL, Ring=tbm_row.split('_')
        tbm_related=B_PorM_IorO+'_'+Disk+'_'+BLD+'_'+PNL
        if tbm_related not in elements_tbmdelay:
            elements_tbmdelay.append(tbm_related)

    for x in elements_tbmdelay:
        if x=='':
            continue;
        tbmfilename='ConfigDat/tbm/TBM_module_Pilt_'+str(x)+'.dat'
        tbmfile=open (tbmfilename,"w")
        towrite='Pilt'+'_'+B_PorM_IorO+'_'+Disk+'_'+BLD+'_'+PNL+'_'+'ROC0'+'\n'+\
        "TBMABase0: 0\n"+\
        "TBMBBase0: 0\n"+\
        "TBMAAutoReset: 0\n"+\
        "TBMBAutoReset: 0\n"+\
        "TBMANoTokenPass: 0\n"+\
        "TBMBNoTokenPass: 0\n"+\
        "TBMADisablePKAMCounter: 0\n"+\
        "TBMBDisablePKAMCounter: 0\n"+\
"TBMAPKAMCount: 5\n"+\
"TBMBPKAMCount: 5\n"+\
        "TBMPLLDelay: 132\n"+\
        "TBMADelay: 73\n"+\
        "TBMBDelay: 73"
        tbmfile.write(towrite)

def findmodule(fed,fedch):
    dictionary = getdict(filename='csv/cablingmap_FPix.csv')
    modulename = ''
    newfed=int(fed)-26
    
    for item in dictionary:
        if fed in item['FED ID'].split('/') and fedch in item['FED channel'].split('/'):
            modulename = item['Official name of position']
            break
    return modulename

def getTBMDelayParam(filename='/home/tif/POSout/Run_0/Run_279/TBM_module_FPix_BmI_D1_BLD11_PNL1_RNG2.dat'):
    tbmdelay = {'pll':-1,'tbma':-1,'tbmb':-1}
    try:
       tbmfile = open(filename,'r')    
       for line in tbmfile:
           if line.startswith('TBMPLLDelay'):
              tbmdelay['pll'] = int(line.strip().split(':')[1])
           if line.startswith('TBMADelay'):
              tbmdelay['tbma'] = int(line.strip().split(':')[1])
           if line.startswith('TBMBDelay'):
              tbmdelay['tbmb'] = int(line.strip().split(':')[1])
       return tbmdelay
    except IOError:
       print "Could not open file! tbm file doesn't exist"

def findkey(run_dir='/home/tif/POSout/Run_0/Run_275/'):
    key = 0
    try: 
       keyfile = open(run_dir+'/PixelConfigurationKey.txt')
       for line in keyfile:
           if 'Global' in line.strip() and line:
               key = line.strip().split()[-1]
               break
       return key
    except IOError:
       print "Could not open file! config key file doesn't exist"

def findconfigversions(key=15781):
    PIXELCONFIGURATIONBASE = os.environ['PIXELCONFIGURATIONBASE']
    configs = { 'key':1, 'nametranslation':1,'detconfig':1,'fedcard':0,'dac':1,'lowvoltagemap':0, 'mask':1, 'trim':1,'tbm':1,'dcdc':1,'portcard': 1,'portcardmap': 1,'fedconfig' : 0,'fecconfig' :  0,'tkfecconfig' :  0,'ttcciconfig' :  0,'ltcconfig' :  0,'calib' :  7} 
    configlist = [] 
    try:
       with open(PIXELCONFIGURATIONBASE+'/configurations.txt') as f:
           for line in f:
               if 'key' in line:
                   if str(key) in line.strip().split(' ')[-1]:
                      for i in range(18):
                          configlist.append(next(f).strip().split(' '))
       for k in configs.keys():
           for item in configlist[0:-1]:
               if item[0] in k:
                  configs[k] = item[-1]
       return configs       
    except IOError:
        print "Could not open file! config key file doesn't exist" 
def main():
   #printnametranslation('cablingmap_fpixphase1_BmI.csv')
   #printnametranslation('csv/cablingmap_fpixphase1_BmO.csv')
   #printportcardmap('csv/cablingmap_fpixphase1_BmO.csv')
   #printfecconfig('csv/cablingmap_fpixphase1_BmO.csv')
   #printtbm('csv/cablingmap_fpixphase1_BmO.csv')
   #print tbmdelays()
   #print findconfigversions()
   #print findmodule('1299','9')
   printPortcardMap()

if __name__ == "__main__":
    main()
