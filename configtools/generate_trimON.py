template = '''ROC:     FPix_BpO_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i_ROC%(roc)i
col00:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col01:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col02:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col03:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col04:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col05:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col06:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col07:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col08:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col09:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col10:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col11:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col12:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col13:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col14:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col15:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col16:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col17:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col18:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col19:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col20:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col21:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col22:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col23:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col24:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col25:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col26:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col27:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col28:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col29:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col30:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col31:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col32:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col33:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col34:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col35:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col36:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col37:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col38:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col39:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col40:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col41:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col42:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col43:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col44:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col45:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col46:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col47:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col48:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col49:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col50:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
col51:   ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
'''

#for bld in (2,3):
#    for pnl in (1,2):
#        f = open('ROC_Trims_module_Pilt_BmI_D3_BLD%(bld)i_PNL%(pnl)i.dat' % locals(), 'wt')
#        for roc in xrange(16):
#            f.write(template % locals())

for dsk in xrange(1,4):
    for pnl in xrange(1,3):
        for rng in xrange(1,3):
            for bld in xrange(1,12) if rng==1 else xrange(1,18):
                f = open('ROC_Trims_module_FPix_BpO_D%(dsk)i_BLD%(bld)i_PNL%(pnl)i_RNG%(rng)i.dat' % locals(), 'wt')
                for roc in xrange(16):
                    f.write(template % locals())
