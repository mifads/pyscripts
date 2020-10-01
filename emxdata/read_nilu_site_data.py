#!/usr/bin/env python3
"""
   Code    Station name                               latitude   longitude     alt
   ------- ---------------------------------------- ---------- ----------- -------
   AM0001R Amberd                                   40°23'04"N 044°15'38"E 2080.0m
   AT0002R Illmitz                                  47°46'00"N 016°46'00"E  117.0m
   AT0033R Stolzalpe bei Murau                      47°07'45"N 014°12'14"E 1302.0m
"""
import os
import re
import pandas as pd
import sys

def process_nilu_table(ifile='',ofile=None,decimalDegrees=False):

  print('IN', ifile)
  print('EXISTS', os.path.exists(ifile))
  sites=[]
  assert os.path.exists(ifile),'Missing input file:'+ifile 
  if ofile is not None:
    print('OPENS ', ofile)
    ofile=open(ofile,'w')
  
  with open(ifile,'r') as f:
    for row in f:
      if row.startswith('Code'): continue
      if row.startswith('--'): continue
      fields = row.split()
      code=fields[0] 
      alt =fields[-1]
      degreesE =fields[-2]
      degreesN =fields[-3]
      if decimalDegrees:
        dN = float(degreesN)
        dE = float(degreesE)
      else:
        delims='°|\'|"'    #  characters from re.split('\d+')
        degN, minN, secN, ns = re.split(delims,degreesN)
        degE, minE, secE, ew = re.split(delims,degreesE)
        dN = int(degN) + int(minN)/60.0 + int(secN)/3600.0
        dE = int(degE) + int(minE)/60.0 + int(secE)/3600.0
        if ns=='S': dN = -dN
        if ew=='W': dE = -dE
  
      if len(fields)==5:
        name = fields[1]
      else:
        name = '_'.join(fields[1:-3])  # -> e.g. Mace_Head
      print(code, name, dN, dE) #, east, dE, ht)
      
      if 'Non' in alt: alt=0.0
      else: alt = alt.replace('m','')
      alt = int(float(alt))
      
     # name = name.replace(' ','')

      if ofile is not None:
        ofile.write('%s_%-55s   %8.3f  %8.3f  20  ! %s %s %6d\n' % ( code, name, dN, dE, degreesN, degreesE, alt))

      sites.append(dict(code=code,name=name,degN=dN, degE=dE,alt=alt))
  return sites

if __name__ == '__main__':

  # We have a test table in the git system:
  scriptDir= os.path.dirname( os.path.realpath(__file__)) # location of this script
  ifile= scriptDir + '/stations_jun2020.txt'
  sites = process_nilu_table(ifile, ofile='emepLL_stations_jun2020.txt')
  
