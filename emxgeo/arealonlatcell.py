#!/usr/bin/env python3
# From: http://badc.nerc.ac.uk/help/coordinates/cell-surf-area.html
#See also (for polygon areas)
#https://stackoverflow.com/questions/4681737/how-to-calculate-the-area-of-a-polygon-on-the-earths-surface-using-python
# Note, earlier version used simpler R=6371, later uses 
from numpy import pi,sin

R         = 6371.0  #! km
EARTH_RAD = 6378.1370     # earth circumference in meters, WGS-84
R2 = R*R
RAD2= EARTH_RAD*EARTH_RAD
deg2Rad = pi/180.0

##def AreaLonLatCell(lon1,lon2,lat1,lat2):

def areaLonLatCell(clat,dLat,dLon): 
  """ area matches calculation based on spherical cap, e.g.
      http://mathforum.org/library/drmath/view/63767.html
      Also uses WGS-84 R """
  assert clat> -90.0 and clat<90,'emxgeo: Impossible lat %f' % clat
  drLon = dLon*deg2Rad
  rLat1 = (clat-0.5*dLat)*deg2Rad
  rLat2 = (clat+0.5*dLat)*deg2Rad
  S = RAD2*drLon*(sin(rLat2)-sin(rLat1))
  return S

def areaLonLatCellX(clat,dLat,dLon): 
  """ area matches calculation based on spherical cap, e.g.
      http://mathforum.org/library/drmath/view/63767.html
      Also uses WGS-84 R """
  drLon = dLon*deg2Rad
  rLat1 = (clat-0.5*dLat)*deg2Rad
  rLat2 = (clat+0.5*dLat)*deg2Rad
  S = R2*drLon*(sin(rLat2)-sin(rLat1))
  return S

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
  print("area  Oslo, 0.5" , areaLonLatCell(60.0,0.5,0.5))
  print("area  OsloX, 0.5" , areaLonLatCellX(60.0,0.5,0.5))
  print("Area  SPole, 1deg" , AreaLonLatCell(-89.0,1.0))
  print("Area  Sahara, 15deg" , AreaLonLatCell(15.0,1.0))
  print("area  Sahara, 15deg" , areaLonLatCell(15.0,1.0,1.0))
  print("area  SaharaX, 15deg" , areaLonLatCellX(15.0,1.0,1.0))
#fails  lats = [  10.0, 30.0, 85.0 ]
#  print("Area  SPole, 1deg" , AreaLonLatCell(lats,1.0))
