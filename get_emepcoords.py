#!/usr/bin/env python3
"""
    Coordinate conversions from lon,lat to EMEP XY as needed
    Tries first proj4, but if not available has own routines
    For proj4:
    earth radius is 6370/50=127.4
    proj +ellps=sphere +a=127.4 +e=0 +proj=stere +lat_0=90 +lon_0=-32 +lat_ts=60 +x_0=8 +y_0=110 
"""
import numpy as np

# Preferred:
def LonLat2emepXy(lon,lat,dbg=False):
  """
    Usage:  x, y = LongLat2emepXy 
    returns EMEP 50km PS model's  x and y coordinates
  """
  try:
    from pyproj import Proj
    p = Proj( ellps='sphere', a=127.4, e=0, proj='stere', lat_0=90, \
                 lon_0=-32, lat_ts=60, x_0=8, y_0=110 )
    x, y = p(lon,lat)
    if dbg : print(' Used proj4 ') 
  except:
    if dbg : print(' Used home-grown equatations ') 
    x, y = EmepLonLat2Xy50(lon,lat)
  return x, y

# Convert array of lat/long to EMEP 50 i,j
# From ExJobb work of Emma and Jakob, 2013
# Extended with __main__ by Dave, Feb 2015
# latlon_convij.py
#
# Extended Jan 2016 to cope with scalar or vector inputs using ideas from
# From http://stackoverflow.com/questions/12653120/how-can-i-make-a-numpy-function-that-accepts-a-numpy-array-an-iterable-or-a-sc...

def EmepLonLat2Xy50(lon,lat):
  # Conversion clculations
  xpol=8.0
  ypol=110.0
  d=50.0# km
  lat_0=np.pi/3.0
  R=6370.0 # km
  M=(R/d)*(1.0+np.sin(lat_0))  #DS query interger math?
  lon_0=-32.0*np.pi/180.0

  dimtest=np.asarray( lat )
  nlen=dimtest.size  # 1 for scalars or 1-element arrays

  print("DIMTEST ",  nlen)

  la=np.multiply(lat,np.pi/180.0) # OK for scalars or vectors
  lo=np.multiply(lon,np.pi/180.0)

  if nlen > 1: 
    x=[]; y=[]
    #print "SIZE lat la  ", np.size(lat), np.size(la), la[1]
    #print "SIZE long lo AAA ", np.size(lon), np.size(lo), lo[1]
    for k in range(0,np.size(lat)):  # diff np.size, len??
      x.append( xpol+M*np.tan(np.pi/4.0-la[k]/2.0)*np.sin(lo[k]-lon_0) )
      y.append( ypol-M*np.tan(np.pi/4.0-la[k]/2.0)*np.cos(lo[k]-lon_0))
          #print "KKKK ", k, lon[k], lat[k], x[k], y[k]  
  else:
     x= xpol+M*np.tan(np.pi/4.0-la/2.0)*np.sin(lo-lon_0)
     y= ypol-M*np.tan(np.pi/4.0-la/2.0)*np.cos(lo-lon_0)

  return x , y

def EmepLonLat2Ij50(lon,lat):
  x=[]; y=[]; i=[]; j=[]
  #(x, y ) = EmepLonLat2Xy50(lon,lat)
  x, y =  LonLat2emepXy(lon,lat)
  for k in range(0,np.size(lat)):
     i.append( int(x[k] + 0.5 ) )
     j.append( int(y[k] + 0.5 ) )
  return i, j


if ( __name__ == "__main__" ):

  # 1) Test arrays

  lat = ( 61.0, 70., 80.0, 53.3 )  # Last is Mace Head
  lon = ( 11.0, 11., 11.0, -9.89 )
  ii=[]; jj=[]
  xx=[]; yy=[]
  xx, yy =  EmepLonLat2Xy50(lon,lat)
  ii, jj =  EmepLonLat2Ij50(lon,lat )
  xxp, yyp =  LonLat2emepXy(lon,lat,dbg=True)

  print('TESTING EMEP conversions for 4 locations')
  for k in range(0,len(lat)):
     print('site %2d Lon %7.2f Lat %7.2f => XY %7.2f %7.2f or IJ %5d%d ' % \
        ( k, lon[k], lat[k], xx[k], yy[k]  , ii[k], jj[k] ))
     print('site %2d Lon %7.2f Lat %7.2f => XY %7.2f %7.2f or IJ %5d%d ' % \
        ( k, lon[k], lat[k], xxp[k], yyp[k]  , ii[k], jj[k] ))

  # 2) Test scalars

  lat, lon = 53.3, -9.89  # MH
  xx, yy =  EmepLonLat2Xy50(lon,lat)
  print('SCALAR ', k, lon, lat, xx, yy) 
  xx, yy =  LonLat2emepXy(lon,lat,dbg=True)
  print('PSCALAR ', k, lon, lat, xx, yy) 

  # 3) Test 1-element array

  lat, lon = [53.3], [-9.89]  # MH
  xx, yy =  EmepLonLat2Xy50(lon,lat)
  print('1pt array ', k, lon, lat, xx, yy) 

  xx, yy =  LonLat2emepXy(lon,lat,dbg=True)
  print('1pt array ', k, lon, lat, xx, yy) 
