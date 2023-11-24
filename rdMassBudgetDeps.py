#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
"""
 # Mass Budget. Units are kg with MW used here. ADJUST! if needed
 #n          Spec        usedMW        emis        ddep        wdep        init    sum_mass     fluxout      fluxin   frac_mass
  1 RO2POOL                64.0  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  3.4556E+07  1.3829E+07  0.0000E+00  2.1897E+07
  2 CH3CO3                 75.0  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  1.2705E+06  5.1095E+05  0.0000E+00  6.8797E+05
  3 NMVOC                  36.8  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00

In a perfect system:
   init + emis + fluxin - ddep - wdep -fluxout = sum_mass

Usage:

  rdMassBudget.py MassBudgetSummary_2015.txt
"""
#assert len(sys.argv)>1,'Need input file!'
#f=pd.read_table(sys.argv[1],delim_whitespace=True,header=1)
ifile='/home/davids/MDISKS/Nebula/work/GLOBAL05/rv4_test_eclv2p3.2015/MassBudgetSummary.txt'
f=pd.read_table(ifile,delim_whitespace=True,header=1)

sumProd = sumLoss = sumInit = sumMass = 0.0

def printterms(r,f):
    print('M %-10s %10.3e %10.3e %10.3e' % ( r.Spec, f*r.emis, f*r.ddep, f*r.wdep ) )

for row in f.iterrows():
  r=row[1] # pandas index of row (weird?)

  if r.Spec=='NH3':
    f=14.0/17.0                       # get N fraction for NH3
  elif  r.Spec=='NH4_f':
    f = 14.0/18.0 # N frac for NH4
  elif r.Spec=='NO':
    f=14.0/30.0                       # get N fraction for NH3
  elif r.Spec=='NO2':
    f=14.0/46.0                       # get N fraction for NH3
  else:
    continue
  printterms(r,f)

