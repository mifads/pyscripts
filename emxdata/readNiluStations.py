#!/usr/bin/env python3
"""
  Reads stations list produced in June 2020, which starts 

   Code    StationName   ..       latitude   longitude   alt
   AM0001R Amberd        ..       40°23'04"N 044°15'38"E 2080.0m
   ..
  (stored in this directory) and returns dict of sites data """
import os.path as op
import sys

def read_nilu_sites():

  sites=dict()

  scriptDir= op.dirname( op.realpath(__file__)) # location of this script
  f = open( scriptDir + '/stations_jun2020.txt', 'r')

  lines=f.readlines()
  f.close()
  for n, line in enumerate(lines):
   if n==0: continue
   code=line[:3] + line[5:6]
   station = line[8:49]
   station=station.replace(' ','')
   alt     = line[72:78]
   if 'Non' in alt: alt = 0.0
   #print(code, station,alt)
  
   if code not in sites.keys():
     sites[code]=dict()
     sites[code]['name']= station
     sites[code]['alt']= float(alt)
  return sites

if __name__ == '__main__':

  sites = read_nilu_sites()
  print('sites["NO01"]: ', sites['NO01'])
  
