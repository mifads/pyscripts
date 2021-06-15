#!/usr/bin/env python3
# from ancient Work/RESULTS/VERIFICATION/scripts_stallo/scanWdc.py

from glob import glob
import numpy as np
import pandas as pd  # june 2021. started move to pd
import sys

print_lines = True  # gives ------ lines between sites. 
runs=sys.argv[1:]
if sys.argv[1] == '-b':
  print_lines = False
  runs=sys.argv[2:]

#sites='Alert Mace_Head'.split()
#sites=np.genfromtxt('LIST.sites',dtype=None)
# Use 1st file for site names
p=pd.read_csv(runs[0],header=0,delim_whitespace=True,skiprows=[1])
sites = p.Site.values

npolls='SURF_ppb_MAXO3;SURF_ppb_CO'.split(';')

for nsite, site in enumerate(sites):  #  'Ozone_daily_max ppb;Ozone_daily_mean ppb'.split(';'):
  if nsite==0:
    header='Run                  Site                 Country                LatN    LonE   Alt  DC%     Obs     Mod  Bias%  Corr'
    lenRow = len(header)
    print(header )
    if(print_lines): print('-'*lenRow )

  for run in runs:
    tst=run.split('_')[-2]   # LOG_SURF_MAXO3_2982bLowGL_2012.txt
    Ns = '-' 
    bias = '-' 
    r2 = '-' 

    with open(run,'r') as f:
      t = f.read()    #  print "FFF? ", len(t)
      tt=t.split('\n')
      f.close()
       #try:  # species may not always exist in file
           #FAILED row = tt[tt.index(p)]
    #print(tt[4])
    site_used=False
    for row in tt:
        #print('LEN ', len(row) )
        if len(row)< 33:
          continue

        if row.split()[0] == site:
            #print 'ROW', p, row
            alt=int( row.split()[4] )
            if alt>500: continue
            site_used=True
            #print('%-20s'%tst, row[20:]) # skips site name
            print('%-20s'%tst, row)
           #ioa = row.split()[-1]

  if site_used and print_lines : print( '-'*lenRow )

#    la, lo, he = map(float, l.split("\n")[2].split(","))
#    print la, lo, he


