#!/usr/bin/env python
# To and from EMEP 50 km grid coords (new=official)
# 
# Older coords were x_old = x_official + 35
# Older coords were y_old = y_official + 11
# # earth radius is 6370/50=127.4
#proj +ellps=sphere +a=127.4 +e=0 +proj=stere +lat_0=90 +lon_0=-32 +lat_ts=60 +x_0=8 +y_0=110 
from pyproj import Proj

p=Proj( ellps='sphere', a=127.4, e=0, proj='stere', lat_0=90, lon_0=-32, lat_ts=60, x_0=8, y_0=110 )

def lonlat2xy(lon,lat):
 """ Convert lon, lat to EMEP 50km x, y (official) coords """
 return p(lon,lat)

def xy2lonlat(x,y):
 """ Convert EMEP 50km x, y (official) coords to lon, lat """
 return p(x,y,inverse=True)

if __name__ == '__main__':

  x, y = lonlat2xy(11.0,57.0)
  print " lon = 11.0, lat=57.0 =",  x, y
  x, y = lonlat2xy(-178.0,87.0)
  print " lon = -178.0, lat=87.0 =", x, y
  lon, lat = xy2lonlat(0.0,0.0)
  print "Inv   0,   0 ", lon, lat 
  lon, lat = xy2lonlat(-35.0,-11.0)
  print "Inv -35, -11  ", lon, lat 
