#!/usr/bin/env python
# From: http://badc.nerc.ac.uk/help/coordinates/cell-surf-area.html
from __future__ import print_function
from numpy import pi,sin

R = 6371.0  #! km
R2 = R*R
deg2Rad = pi/180.0

##def AreaLonLatCell(lon1,lon2,lat1,lat2):

def AreaLonLatCell(clat,dll): # centres
#  #R = 6371.0  ! km
  #dLon = (lon2-lon1)*deg2Rad
  drLon = dll*deg2Rad
  rLat1 = (clat-0.5*dll)*deg2Rad
  rLat2 = (clat+0.5*dll)*deg2Rad
  S = R*R*drLon*(sin(rLat2)-sin(rLat1))
  #print rLat1, rLat2, S 
  return S
#
if __name__ == '__main__' :
  print("Area XX Oslo, 1deg" , AreaLonLatCell(60.0,1.0))
  print("Area  Oslo, 0.5" , AreaLonLatCell(60.0,0.5))
  print("Area  SPole, 1deg" , AreaLonLatCell(-89.0,1.0))
  print("Area  Sahara, 15deg" , AreaLonLatCell(20.0,15.0))
#fails  lats = [  10.0, 30.0, 85.0 ]
#  print("Area  SPole, 1deg" , AreaLonLatCell(lats,1.0))
