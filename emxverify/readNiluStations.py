#!/usr/bin/env python3
"""
  Reads stations list produced in June 2020, and returns
  dict of sites data """
import pandas as pd
import sys
#AT0030R Pillersdorf bei Retz                     48°43'16"N 015°56'32"E  315.0m

dataDir='/home/davids/Data/NILU/'

def read_nilu_sites():
  sites=dict()
  f=open(dataDir + 'stations_jun2020.txt','r')
  lines=f.readlines()
  f.close()
  for n, line in enumerate(lines):
   if n==0: continue
   code=line[:3] + line[5:6]
   station = line[8:49]
   station=station.replace(' ','')
   alt     = line[73:78]
   if 'Non' in alt: alt = 0.0
   #print(code, station,alt)
  
   if code not in sites.keys():
     sites[code]=dict()
     sites[code]['name']= station
     sites[code]['alt']= float(alt)
  return sites
