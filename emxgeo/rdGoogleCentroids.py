#!/usr/bin/env python3
import numpy as np
import sys
#ISO  ISO3  ISO-Numeric   fips  Country Capital Area(in sq km) Population   Continent    tld   CurrencyCode  CurrencyName  Phone  Postal Code Format   Postal Code Regex    Languages    geonameid    neighbours   EquivalentFipsCode

#print(sys.getdefaultencoding()) # Stupid errors:

def getGoogleCentroids(iso2,dbg=False):

  geo=dict()
  with open('/home/davids/Data/GEODATA/google_centroids.txt',errors='ignore',encoding='utf-8') as f:
    for line in f:
      #print(line.encode('utf-8'))
      #print(line) FAILS
      if line.startswith('#'): continue
      fields = line.split(maxsplit=3)
      if line.startswith(iso2): 
        geo['iso2'] = fields[0]
        geo['lat'] = float(fields[1])
        geo['lon'] = float(fields[2])
        geo['country']  = fields[3].split('\n')[0]
        if dbg: 
          #print(iso2, geo)
          print(fields)
      #if line.startswith('UM'): sys.exit()
  return geo
  

if __name__ == '__main__':
  print(getGoogleCentroids('GB'))
    
