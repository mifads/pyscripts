#!/usr/bin/env python3
import os
import pandas as pd
import sys

if len(sys.argv) != 3:
  print('Usage: mkSitesSplit.py  ifile   odir')
else:
  ifile=sys.argv[1]
  odir=sys.argv[2]
os.makedirs(odir,exist_ok=True)

# 108 sites needs 112 skip?
#ifile='/nobackup/forsk/sm_davsi/2023TESTS/rv5_series/CAMS01_rv5_0tstDS_C01yEmDef.2018/sites_2018.csv'
siteinfo=dict()
nlines=0
with open(ifile,'r') as f:
  for line in f.readlines():
    fields = line.split(maxsplit=2)
    nlines += 1

    if 'sites in domain' in line:
      nsites=int(fields[0])
      print('NSITES ', nsites)
    #elif 'Hours betweeen' in line:
    elif 'ztopo' in line:
      header=line
      continue
    elif 'Hours betweeen' in line:
      nvars=int(fields[0])
      print('NSITES ', nsites, 'NVARS', nvars)
    elif 'site,date' in line:
      break
    else:
      siteinfo[fields[0]] = line # replace('\n','')

# 
ds=pd.read_csv(ifile,skiprows=nlines-1) # 112)
sites=ds.site.unique

for site in sites():
  f=open(odir+'/SITES_%s.csv' % site, 'w' )
  f.write('#'+header)
  f.write('#'+siteinfo[site])
  fds=ds[ds.site==site]
  fds.to_csv(f,index=False)
  print('Completed: ', site)
  #sys.exit()
