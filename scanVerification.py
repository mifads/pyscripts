#!/usr/bin/env python

from glob import glob
import sys
import re

#for arg in sys.argv: print(arg)

runs=sys.argv[1:]

yearly =3 # offsets from poll name
yearday=4

# SPACES are important - will search for whole string!
xpolls='''
SO4_aerosol  ugS/m3
XSO4_aerosol  ugS/m3
NO2_air  ugN/m3
HNO3+NO3_air+aerosol  ugN/m3
NH3+NH4_air+aerosol  ugN/m3
'''.strip().split('\n')

polls='''
Ozone_daily_max ppb
Ozone_daily_mean ppb
SO2_in_Air ugS/m3
Sulfate_in_Air ugS/m3
NO_in_Air ugN/m3
NO2_in_Air ugN/m3
HNO3_in_Air ugN/m3
NO3-_in_Air ugN/m3
Sum_of_HNO3,_NO3-_in_air ugN/m3
NH4+_in_Air ug/m3
NH3+NH4+_in_Air ugN/m3
Ammonia_in_Air ugN/m3
NO3_coarse ug/m3
PM10 ug/m3
PM25 ug/m3
Na+_in_air ug/m3
SO4_wet_dep. mgS/m2
Nitrate_wet_dep. mgN/m
Ammonium_wet_dep. mgN/m2
Nitric_acid_wet_dep. mgN/m2
SO4_conc._in_precip. mgS/l
Nitrate_conc._in_precip. mgN/l
Ammonium_conc._in_precip. mgN/l
Precipitation mm
'''.strip().split('\n')

npolls='Ozone_daily_max ppb;Ozone_daily_mean ppb'.split(';')
fmt='%-40.36s %4s' + '%8s'*5
fmt='%-50.46s %4s' + '%8s'*5
line = '-' * (40+5+8*5)

for p in polls:  #  'Ozone_daily_max ppb;Ozone_daily_mean ppb'.split(';'):
  print(fmt % ( p, 'Ns', 'bias', 'r-Y', 'r-YD', 'ioa-Y', 'ioa-YD' ) )
  print( line )

  for run in runs:
    #QQ  if ( 'BM_' in tst0 ): tst = '%s-EmChem09soa' % tst0
    try:
      tst=run.split('.')[-3]   # "%s/Res.%s.%s.%s" % ( idir, tst, grid, year)
    except:
      #tst=run.split('_')[1]   # Res_%s-xx.%s" % ( idir, tst, grid, year)
      r=re.search('Res_(\w+)', run ) # Stops at '-' in e.g h500-outluers_condays
      tst=r.groups()[0]
      #print( "XRUN :", run, tst)
    tst=run.replace('Res_','').replace('-outliers_comday','')  # A2019 FIX!!

    #print("TST ", tst, ":", run)
    Ns = '-' 
    bias = '-' 
    r2 = '-' 
    ioa= '-' 
    dr2 = '-' 
    dioa= '-' 

    try:
       f = open(run)
       t = f.read()
       tt=t.split('\n')
       f.close()
       #print('FPP', p, tt.index(p))
      
       try:  # species may not always exist in file
           row = tt[yearly + tt.index(p)]
           #print('ROW', row)
           #sys.exit()
           ioa = row.split()[-1]
           r2  = row.split()[-2]
           bias = row.split()[-4]
           Ns   = row.split()[-10]
#TMPpy           row = tt[yearday + tt.index(p)]
           dioa = row.split()[-1]
           dr2  = row.split()[-2]
       except:
           pass
    except:
       pass

    print(fmt % ( tst, Ns,  bias, r2, dr2, ioa, dioa ) )

  print( line )

#    la, lo, he = map(float, l.split("\n")[2].split(","))
#    print la, lo, he


