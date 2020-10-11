#!/usr/bin/env python3
# Used tips from https://realpython.com/pandas-dataframe/
import numpy as np
import pandas as pd
import sys
""" 
  Reads fies starting (nl added):
     1	 41  sites in domain   1 132   1 111 InpCoords: LatLong
     2	  1 Hours between outputs
     3	                                              name,   lon,   lat,     z, zgrid
     4	NOTEST1_Birkenes_m                                ,    51,    59,    20,    20
     5	NOTEST1_Birkenes_0                                ,    51,    59,    20,    20
    ....
    45	140 Variables units: ppb
    46	site,date,hh,RO2POOL,CH3CO3,NMVOC,O3,NO,NO2,NO3,N2O5,H2,H2O2,HONO,HNO3,HO2NO2,
    47	NOTEST1_Birkenes_m, 01/01/2015,01:00, 5.555E-03, 4.793E-05, 0.000E+00, 4.000E+
    48	NOTEST1_Birkenes_0, 01/01/2015,01:00, 5.555E-03, 4.793E-05, 0.000E+00, 4.000E+
"""

def read_sites(ifile,wanted_poll='O3',wanted_sites=[],dbg=False):

  ns=0
  sites=[]
  vals = dict()

  with open(ifile,'r') as f:
    nsites, txt =f.readline().split(maxsplit=1)
    nhours, txt =f.readline().split(maxsplit=1)
    siteheaders =f.readline().split(sep=',')
  #  row1=f.readline()
    #print(p)#row1)
    for row in f:
      if dbg: print(row)
      site, txt =row.split(maxsplit=1)
      if 'Variables' in row:  break
      sites.append(site)
  f.close()
  n = int(nsites) + 4
  if dbg: print('read_sites N=', n)
      
  df=pd.read_csv(ifile,skiprows=n) #,header=n-1)
  #print(df.keys())
  #print(df.head(1))
  if len(wanted_sites)>0:
    sites = wanted_sites
  for site in sites:
    filter_ = df['site'] == site # 'NOTEST1_Birkenes_m'
    vals[site] =df[filter_][wanted_poll].values
    if dbg: print('SiteVals', site, np.max( vals[site] ))
  return vals


if __name__ == '__main__':

  ifile='sites_1000.csv'
  poll='POM_f_wood'
  vals =  read_sites(ifile,wanted_poll=poll,dbg=True) # ,wanted_sites=[ 'NOTEST1_Birkenes_m', ])
  site='NOTEST1_Birkenes_0'
  vals =  read_sites(ifile,wanted_poll=poll,wanted_sites=[site],dbg=True) # ,wanted_sites=[ 'NOTEST1_Birkenes_m', ])
  vals =  read_sites(ifile,wanted_poll=poll,dbg=True) # ,wanted_sites=[ 'NOTEST1_Birkenes_m', ])

