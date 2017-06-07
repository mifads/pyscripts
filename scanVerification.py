#!/usr/bin/env python

from glob import glob
import sys
import re

#for arg in sys.argv: print(arg)

runs=sys.argv[1:]

yearly =3 # offsets from poll name
yearday=4

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

for p in polls:  #  'Ozone_daily_max ppb;Ozone_daily_mean ppb'.split(';'):
  print("%-32s %4s %10s %10s %10s %10s %10s" % ( p, 'Ns', 'bias', 'r-Y', 'r-YD', 'ioa-Y', 'ioa-YD' ) )
  print( '-'*92 )

  for run in runs:
    #QQ  if ( 'BM_' in tst0 ): tst = '%s-EmChem09soa' % tst0
    #print( "RUN :", run)
    try:
      tst=run.split('.')[-3]   # "%s/Res.%s.%s.%s" % ( idir, tst, grid, year)
    except:
      #tst=run.split('_')[1]   # Res_%s-xx.%s" % ( idir, tst, grid, year)
      r=re.search('Res_(\w+)', run ) # Stops at '-' in e.g h500-outluers_condays
      tst=r.groups()[0]

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
       try:  # species may not always exist in file
           row = tt[yearly + tt.index(p)]
           ioa = row.split()[-1]
           r2  = row.split()[-2]
           bias = row.split()[-4]
           Ns   = row.split()[-10]
           row = tt[yearday + tt.index(p)]
           dioa = row.split()[-1]
           dr2  = row.split()[-2]
       except:
           pass
    except:
       pass

    print("%-32s %4s %10s %10s %10s %10s %10s" % ( tst, Ns,  bias, r2, dr2, ioa, dioa ) )

  print( '-'*92 )

#    la, lo, he = map(float, l.split("\n")[2].split(","))
#    print la, lo, he


