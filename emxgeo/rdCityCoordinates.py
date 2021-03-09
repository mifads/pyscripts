#!/usr/bin/env python3
import numpy as np
import sys

"""
#https://www.infoplease.com/world/geography/major-cities-latitude-longitude-and-corresponding-time-zones
Aberdeen, Scotland	57	9 N	2	9 W	5:00 p.m.
Adelaide, Australia	34	55 S	138	36 E	2:30 a.m.1
Algiers, Algeria	36	50 N	3	0 E	6:00 p.m.
"""

def getCityCoords(cityWanted=None,countryWanted=None):

  city=dict()
  nmatches = 0

  with open('/home/davids/Data/GEODATA/major-cities-lat-lon-tz.txt','r') as f:
   for line in f:
    if line.startswith('#'): continue
    fields = line.split('\t')
    city, land = fields[0].split(',',maxsplit=1)

    if city.lower() != cityWanted.lower(): continue

    minN, sign  = fields[2].split()
    degN = int(fields[1]) + int(minN)/60.0
    if sign == 'S': degN = -degN

    minE, sign  = fields[4].split()
    degE = int(fields[3]) + int(minE)/60.0
    if sign == 'W': degE = -degE
    print(city, land, degN, degE)
    nmatches  += 1
    if nmatches > 1:
      sys.exit('2nd match found!' + line)
    print(line)
   if nmatches ==0: print("Not found: ",cityWanted)
   return degN, degE
 
  #sys.exit()
def coords2global05ij(n,e):
  i = int( (e+180)/0.5)
  j = int( (n+ 90)/0.5)
  return i, j

if __name__ == '__main__':

  n,e = getCityCoords("Oslo",countryWanted=None)
  n,e = getCityCoords("Calgary",countryWanted=None)
  print('Found  Oslo at ', n, e)
  #n,e =  getCityCoords("Bamako",countryWanted=None) # Mali Sahel
  print( coords2global05ij(12.34,-7.55) )
  #n,e =  getCityCoords("Kartoum",countryWanted=None) # Sudan Sahel
  print( coords2global05ij(15.31,32.35) )
