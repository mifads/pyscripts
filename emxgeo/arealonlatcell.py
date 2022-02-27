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

def km2_areaLonLatCell(clat,dLat,dLon): 
  """ area matches calculation based on spherical cap, e.g.
      http://mathforum.org/library/drmath/view/63767.html
      Also uses WGS-84 R """
  assert clat> -90.0 and clat<90,'emxgeo: Impossible lat %f' % clat
  drLon = dLon*deg2Rad
  rLat1 = (clat-0.5*dLat)*deg2Rad
  rLat2 = (clat+0.5*dLat)*deg2Rad
  S = RAD2*drLon*(sin(rLat2)-sin(rLat1))  # ie uses WGS-84
  return S

def km2_areaLatCell(clat,dll): 
  """ area matches calculation based on spherical cap, e.g.
      http://mathforum.org/library/drmath/view/63767.html
      Also uses WGS-84 R """

  assert clat> -90.0 and clat<90,'emxgeo: Impossible lat %f' % clat
  drLon = dll*deg2Rad
  rLat1 = (clat-0.5*dll)*deg2Rad
  rLat2 = (clat+0.5*dll)*deg2Rad
  S = RAD2*drLon*(sin(rLat2)-sin(rLat1))  # ie uses WGS-84
  return S

def km2_areaLonLatCellX(clat,dLat,dLon): 
  """ area matches calculation based on spherical cap, e.g.
      http://mathforum.org/library/drmath/view/63767.html
      Also uses WGS-84 R """
  drLon = dLon*deg2Rad
  rLat1 = (clat-0.5*dLat)*deg2Rad
  rLat2 = (clat+0.5*dLat)*deg2Rad
  S = R2*drLon*(sin(rLat2)-sin(rLat1))
  return S


def km2_AreaLonLatCell(clat,dll): # centres
#  #R = 6371.0  ! km
  #dLon = (lon2-lon1)*deg2Rad
  drLon = dll*deg2Rad
  rLat1 = (clat-0.5*dll)*deg2Rad
  rLat2 = (clat+0.5*dll)*deg2Rad
  S = R*R*drLon*(sin(rLat2)-sin(rLat1))
  #print rLat1, rLat2, S 
  return S

# And from https://gis.stackexchange.com/questions/127165/more-accurate-way-to-calculate-area-of-rasters
def km2_area_of_wgs84pixel(center_lat, pixel_size): #DS re-ordered, center_lat):
    """Calculate km^2 area of a wgs84 square pixel.

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

def km2_area_wgs84cell(center_lat, pixel_size): #DS re-ordered, center_lat):
    """Calculate km^2 area of a wgs84 square pixel. As with area_of_pixel above
       but with atanh idea from same website

    Adapted from: https://gis.stackexchange.com/a/127327/2397

    Parameters:
        pixel_size (float): length of side of pixel in degrees.
        center_lat (float): latitude of the center of the pixel. Note this
            value +/- half the `pixel-size` must not exceed 90/-90 degrees
            latitude or an invalid area will be calculated.

    Returns:
        Area of square pixel of side length `pixel_size` centered at
        `center_lat` in km^2.

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
     globArea['areaLatCell']    += km2_areaLatCell(clat,dll)
     globArea['area_of_pixel2'] += km2_area_wgs84cell(clat,dll)
  for key, val in globArea.items():
    val *= 720 # 720 lon cells
    print("Glob area,%15s, %15.7e km2, %15.7e m2" % (  key, val, 1.0e6*val ))
  print("cf: http://www.jpz.se/Html_filer/wgs_84.html:", 510065621.724 )

def globArea_comp():
    """ from https://scipython.com/book/chapter-2-the-core-python-language-i/questions/problems/estimating-the-surface-area-of-the-earth/"""
    import math
    a = 6378137.0           # semi-major axis, m
    c = 6356752.314245      # semi-minor axis, m
    e2 = 1 - (c/a)**2
    e = math.sqrt(e2)
    A_WGS84 = 2*math.pi*a**2*(1 + (1-e2)/e * math.atanh(e))
    A_WGS84                 # 510065621724078.94  # fits _pixel v. well!
    r = 6371000.            # mean radius, m
    A_sphere = 4 * math.pi * r**2
    A_sphere                # 510064471909788.25 
    #(A_WGS84 - A_sphere)/A_WGS84 * 100 =  0.00022542477707103626,  ie 0.00023%
    print("Glob area from comp (km2): %15.7e %15.7e" % ( 1.0e-6*A_WGS84, 1.0e-6*A_sphere) ) 

if __name__ == '__main__' :
  dll = 1.0
  print("Area XX Oslo,%f deg"%dll , km2_AreaLonLatCell(60.0,1.0))
  print("Len-km  XX Oslo, %f deg"%dll ,         sqrt(km2_AreaLonLatCell(60.0,dll)) )
  print("AreaLonLatCell  Oslo,  %f"%dll ,       km2_AreaLonLatCell(60.0,dll))
  print("areaLonLatCell  Oslo,  %f"%dll ,       km2_areaLonLatCell(60.0,dll,dll))
  print("AreaLonLatCellX Oslo,  %f"%dll ,       km2_areaLonLatCellX(60.0,dll,dll))
  print("Area  SPole, %f deg"%dll ,             km2_AreaLonLatCell(-89.0,dll))
  print("Area  Sahara, 15degN res %f deg"%dll , km2_AreaLonLatCell(15.0,dll))
  print("area  Sahara, 15degN res %f deg"%dll , km2_areaLonLatCell(15.0,dll,dll))
  print("area  SaharaX, 15degN res %f deg"%dll, km2_areaLonLatCellX(15.0,dll,dll))
#fails  lats = [  10.0, 30.0, 85.0 ]
#  print("Area  SPole, 1deg" , AreaLonLatCell(lats,1.0))

# Borrowing ideas from 
# https://stackoverflow.com/questions/28372223/python-call-function-from-string#28372280
# and *val from https://note.nkmk.me/en/python-argument-expand/

clat=60.0; dLat=dLon=dll= 30.0/60
clat=60.0; dLat=dLon=dll=1.0
functions = dict( km2_areaLonLatCell=(clat,dLat,dLon), km2_areaLatCell=(clat,dll), 
                  km2_areaLonLatCellX=(clat,dLat,dLon), km2_AreaLonLatCell=(clat,dll),
                  km2_area_of_pixel=(clat,dll),  km2_area_wgs84cell=(clat,dll) )
for key, args in functions.items():
  print( 'AREA FUNC %15s %12.3e km2 ' % ( key,  locals()[key](*args) ) )

x=globArea_km2()
globArea_comp()

