from JMTTools import *

downstairs = translation_dat('/home/tif/FPix/FPix_all/nametranslation/0/translation.dat')
cleanroom = translation_dat('/home/tif/FPix/Config_BmI/nametranslation/3/translation.dat')

badmods = []

for i in downstairs.l:    
    for j in cleanroom.l:
        if not i.hubid == j.hubid and i.module == j.module:
            if i.module not in badmods:
                badmods.append(i.module)

if len(badmods) == 0:
    print 'hub IDs okay!'
else:
    for m in badmods:
        print m
