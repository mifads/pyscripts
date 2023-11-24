#!/usr/bin/env python3
"""
Feb 2023  update:  use argparse to change labels. STILL VERY MESSY; needs clean start
June 2021 update. Res files look like:
SO2_in_Air ugS/m3

  Period CDays   Ns    Np   pc<30% pc<50%        Obs      Mod     Bias  Rmse  Corr   IOA
  YEARLY   274   57    57    (58%)  (86%)       0.30     0.33       8%  0.23  0.64  0.78
  JANFEB    -    60    60    (48%)  (80%)       0.36     0.47      32%  0.40  0.62  0.74
so no need for r-Y,r-YD etc"""

import argparse
from glob import glob
import os
import sys
import re

#------------------ arguments  ----------------------------------------------

#parser=argparse.ArgumentParser(usage=__doc__) also works, but text at start
parser=argparse.ArgumentParser(epilog=__doc__,
   formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-s','--season',help='season (eg JANFEB)',default='YEARLY')
parser.add_argument('-i','--ifiles',help='Input files',nargs='*',required=True)
parser.add_argument('-S','--skiplabels',help='skip labels from name',nargs='*',required=False)
args=parser.parse_args()

if args.season:
  season=args.season

runs=args.ifiles
assert len(runs)>0,'No runs specified!'

#yearly =3 # offsets from poll name
#yearday=4

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
EC_in_PM10 ugC/m3
EC_in_PM2.5 ugC/m3
OC_in_PM10 ugC/m3
OC_in_PM2.5 ugC/m3
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
fmt='%-50.46s %4s' + '%8s'*6   # June 2021
fmt='%-50.46s %-8s %4s' + '%8s'*6  + '     %-20s'  # April 2022, with season
fmt='%-40.46s %-8s %4s' + '%8s'*6  + '     %-20s'  # April 2022, with season
line = '-' * (40+5+8*6)

for np, p in enumerate(polls):  #  'Ozone_daily_max ppb;Ozone_daily_mean ppb'.split(';'):

  for nrun, run in enumerate(runs):

    tst = os.path.basename(run).replace('Res_','')

    Ns = '-' 
    bias = '-' 
    mod  = '-' 
    obs  = '-' 
    r2 = '-' 
    ioa= '-' 

    try:
       f = open(run)
       t = f.read()
       tt=t.split('\n')
       f.close()
      
       try:  # species may not always exist in file
         for ii in range(8):
           row = tt[ii + tt.index(p)]

           if row.split()[0] == season:
             ioa = row.split()[-1]
             r2  = row.split()[-2]
             rmse = row.split()[-3]
             bias = row.split()[-4]
             mod  = row.split()[-5] 
             obs  = row.split()[-6]
             fmod  = float( mod )
             fobs  = float( obs )
             if fmod > 1000. or fobs > 1000.:
               fac = 0.001
               mod = '%.1fe3' % ( fac*fmod)
               obs = '%.1fe3' % ( fac*fobs)
          
             Ns   = row.split()[-10]
             break
       except:
           pass
    except:
       pass

    if nrun==0: # header line
      print(fmt % ( 'Run', season, 'Ns', 'obs', 'mod', 'bias', 'rmse', 'r2', 'ioa', p ) )

    if args.skiplabels:
      for skip in args.skiplabels:
        tst = tst.replace(skip,'')
    print(fmt % ( tst, ':',  Ns, obs, mod, bias, rmse, r2, ioa , p ) )

  print( line )

#    la, lo, he = map(float, l.split("\n")[2].split(","))
#    print la, lo, he


