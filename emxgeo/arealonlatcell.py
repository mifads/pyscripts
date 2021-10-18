#!/usr/bin/env python3
# From: http://badc.nerc.ac.uk/help/coordinates/cell-surf-area.html
#See also (for polygon areas)
#https://stackoverflow.com/questions/4681737/how-to-calculate-the-area-of-a-polygon-on-the-earths-surface-using-python
# Note, earlier version used simpler R=6371, later uses 
import math
from math import pi, log, sqrt,atanh
from numpy import pi,sin, sqrt

R         = 6371.0       #! km
EARTH_RAD = 6378.1370    # earth equatorial radius, =a, WGS-84
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
  S = RAD2*drLon*(sin(rLat2)-sin(rLat1))  # ie uses WGS-84
  return S

def areaLatCell(clat,dll): 
  """ area matches calculation based on spherical cap, e.g.
      http://mathforum.org/library/drmath/view/63767.html
      Also uses WGS-84 R """

  assert clat> -90.0 and clat<90,'emxgeo: Impossible lat %f' % clat
  drLon = dll*deg2Rad
  rLat1 = (clat-0.5*dll)*deg2Rad
  rLat2 = (clat+0.5*dll)*deg2Rad
  S = RAD2*drLon*(sin(rLat2)-sin(rLat1))  # ie uses WGS-84
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

# And from https://gis.stackexchange.com/questions/127165/more-accurate-way-to-calculate-area-of-rasters
def area_of_pixel(center_lat, pixel_size): #DS re-ordered, center_lat):
    """Calculate m^2 area of a wgs84 square pixel.

    Adapted from: https://gis.stackexchange.com/a/127327/2397

    Parameters:
        pixel_size (float): length of side of pixel in degrees.
        center_lat (float): latitude of the center of the pixel. Note this
            value +/- half the `pixel-size` must not exceed 90/-90 degrees
            latitude or an invalid area will be calculated.

    Returns:
        Area of square pixel of side length `pixel_size` centered at
        `center_lat` in m^2.

    """
    a = 6378137  # meters
    b = 6356752.3142  # meters
    e = math.sqrt(1 - (b/a)**2)
    area_list = []
    for f in [center_lat+pixel_size/2, center_lat-pixel_size/2]:
        zm = 1 - e*math.sin(math.radians(f))
        zp = 1 + e*math.sin(math.radians(f))
        area_list.append(
            math.pi * b**2 * (
                math.log(zp/zm) / (2*e) +
                math.sin(math.radians(f)) / (zp*zm)))
    return 1.0e-6 * pixel_size / 360. * (area_list[0] - area_list[1]) #DS now km2

def area_of_pixel2(center_lat, pixel_size): #DS re-ordered, center_lat):
    """Calculate m^2 area of a wgs84 square pixel. with atanh idea

    Adapted from: https://gis.stackexchange.com/a/127327/2397

    Parameters:
        pixel_size (float): length of side of pixel in degrees.
        center_lat (float): latitude of the center of the pixel. Note this
            value +/- half the `pixel-size` must not exceed 90/-90 degrees
            latitude or an invalid area will be calculated.

    Returns:
        Area of square pixel of side length `pixel_size` centered at
        `center_lat` in m^2.

    """
    a = 6378137  # meters
    b = 6356752.3142  # meters
    e = math.sqrt(1 - (b/a)**2)
    area_list = []
    for f in [center_lat+pixel_size/2, center_lat-pixel_size/2]:
        zm = 1 - e*math.sin(math.radians(f))
        zp = 1 + e*math.sin(math.radians(f))
        area_list.append(
            math.pi * b**2 * (
                2*atanh(e*sin(math.radians(f)))  / (2*e) +
                #math.log(zp/zm) / (2*e) +
                math.sin(math.radians(f)) / (zp*zm)))
    return 1.0e-6 * pixel_size / 360. * (area_list[0] - area_list[1]) #DS now km2

# from same site:
def areaf(f):
  """ area between equator and latitude f """
  a = 6378137.0 #  meters,
  b = 6356752.3142
  e= sqrt(1-(b/a)**2)  # eccentricity
  zm= 1 - e*sin(f)
  zp= 1 + e*sin(f)
  return pi*b**2 * ( log(zp/zm) / (2*e) + sun(f)/(zp*zm) )

#def area_of_pixel2(pixel_size,center_lat):
#  q=1.0/360  # where pixel_size in degrees

def globArea_km2():

  dll=0.5
  dLon = dLat = dll
  lats=[ -89.75 + i*dll for i in range(360) ] # do 0.5 deg 
  globArea=dict( areaLatCell=0.0, area_of_pixel2=0.0  )
  for clat in lats:
     globArea['areaLatCell'] += areaLatCell(clat,dll)
     globArea['area_of_pixel2'] += area_of_pixel2(clat,dll)
  for key, val in globArea.items():
    val *= 720 # 720 lon cells
    print("Glob area,%15s, %15.7e km2, %15.7e m2" % (  key, val, 1.0e6*val ))
  print("cf: http://www.jpz.se/Html_filer/wgs_84.html:", 510065621.724 )

if __name__ == '__main__' :
  dll = 1.0
  print("Area XX Oslo,%f deg"%dll , AreaLonLatCell(60.0,1.0))
  print("Len-km  XX Oslo, %f deg"%dll , sqrt(AreaLonLatCell(60.0,dll)) )
  print("AreaLonLatCell  Oslo,  %f"%dll , AreaLonLatCell(60.0,dll))
  print("areaLonLatCell  Oslo,  %f"%dll , areaLonLatCell(60.0,dll,dll))
  print("AreaLonLatCellX Oslo,  %f"%dll , areaLonLatCellX(60.0,dll,dll))
  print("Area  SPole, %f deg"%dll , AreaLonLatCell(-89.0,dll))
  print("Area  Sahara, 15degN res %f deg"%dll , AreaLonLatCell(15.0,dll))
  print("area  Sahara, 15degN res %f deg"%dll , areaLonLatCell(15.0,dll,dll))
  print("area  SaharaX, 15degN res %f deg"%dll , areaLonLatCellX(15.0,dll,dll))
#fails  lats = [  10.0, 30.0, 85.0 ]
#  print("Area  SPole, 1deg" , AreaLonLatCell(lats,1.0))

# Borrowing ideas from 
# https://stackoverflow.com/questions/28372223/python-call-function-from-string#28372280
# and *val from https://note.nkmk.me/en/python-argument-expand/

clat=60.0; dLat=dLon=dll=1.0
clat=60.0; dLat=dLon=dll= 30.0/60
functions = dict( areaLonLatCell=(clat,dLat,dLon), areaLatCell=(clat,dll), 
                  areaLonLatCellX=(clat,dLat,dLon), AreaLonLatCell=(clat,dll),
                  area_of_pixel=(clat,dll),  area_of_pixel2=(clat,dll) )
for key, args in functions.items():
  print( 'AREA FUNC %15s %12.3e km2 ' % ( key,  locals()[key](*args) ) )

x=globArea_km2()

