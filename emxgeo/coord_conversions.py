#!/usr/bin/env python3
#NB  pp.__version__ : '3.6.1'
import numpy as np
import pyproj as pp
import sys

# https://pyproj4.github.io/pyproj/stable/examples.html
# https://pyproj4.github.io/pyproj/stable/gotchas.html#upgrading-to-pyproj-2-from-pyproj-1
#https://stackoverflow.com/questions/26452972/coordinates-conversion-with-pyproj
#P2 from pyproj import CRS
# Plate Carree - +proj=eqc +ellps=WGS84   EPSG 32662 (WGS84 Plate Carrée):
# WGS84  wgs84=pyproj.Proj("+init=EPSG:4326") 

"""
CONTAINS:
 efi2wgs
 lonlat_toPlateCarree(lons,lats,dbg=False):
 plateCarree_tolonlat(x,y):
 lonlat2xy(lon,lat,ptest='ps50'):
 xy2lonlat(x,y,ptest='ps50'):
"""

# ------------------------------------------------------------------------------
def efi2wgs84lonlat(x,y,epsg=3035):
 """ Used for converting e.g. EU-Forest ETRS89-LAEA data to lon, lat """
 efi   = pp.Transformer.from_crs(f'EPSG:{epsg}','EPSG:4326',always_xy=True)
 lon, lat = efi.transform(x,y)
 return lon, lat 


# ------------------------------------------------------------------------------
def lonlat_toPlateCarree(lons,lats,dbg=False):

  transformer2pc = pp.Transformer.from_crs("EPSG:4326", "EPSG:32662",always_xy=True)
  x, y = transformer2pc.transform(lons,lats)

  if dbg:
    transformer2ll = pp.Transformer.from_crs("EPSG:32662","EPSG:4326",always_xy=True)
    xlon, xlat = transformer2ll.transform(x,y)
    n=0
    for lon, lat in zip(lons,lats):
      XX, YY = transformer2pc.transform(lon,lat)
      II, JJ = transformer2ll.transform(XX,YY)
      print(f'P2:{n} {lon:.4f} {lat:.4f} {II:.4f} {JJ:.4f} {xlon[n]:.4f} {xlat[n]:.4f}')
#    print(f'P2:{n} {lon:.4f} {lat:.4f} {xlon[n]:.4f} {xlat[n]:.4f}')
      n += 1
  return x, y
# ------------------------------------------------------------------------------

def plateCarree_tolonlat(x,y):
  transformer2pc = pp.Transformer.from_crs("EPSG:32662","EPSG:4326",always_xy=True)
  lons, lats = transformer2pc.transform(x,y)
  return lons, lats

# ------------------------------------------------------------------------------
"""
# To and from EMEP 50 km grid coords (new=official)
# earth radius is 6370/50=127.4
"""
from pyproj import Proj
polar=dict()
polar[50]=Proj( ellps='sphere', R=127.4, proj='stere', lat_0=90, lon_0=-32, lat_ts=60, x_0=8., y_0=110.)
polar[5]=Proj( ellps='sphere', R=127.4, proj='stere', lat_0=90, lon_0=-32, lat_ts=60, x_0=75.5, y_0=1095.5)

#try2 used k=0.933013 instead of lat_0. This number comes from ncdump on test .nc file
#try2=Proj( ellps='sphere', R=127.4, proj='stere', k=0.933013, lat_0=90, lon_0=-32, x_0=8., y_0=110.)


# ------------------------------------------------------------------------------
def lonlat2xy(lon,lat,pstere=50):
 """ Convert lon, lat to EMEP 50km x, y (official) coords """
 if  pstere==50: return polar[50](lon,lat)
 elif pstere==5: return polar[5](lon,lat)
 else: sys.exit(f"{polar} projection not code")

# ------------------------------------------------------------------------------
def xy2lonlat(x,y,pstere=50):
 """ Convert EMEP 50km x, y (official) coords to lon, lat """
 if  pstere==50: return polar[50](x,y,inverse=True)
 elif pstere==5: return polar[5](x,y,inverse=True)
 else: sys.exit(f"{polar} projection not code")

# ------------------------------------------------------------------------------
if __name__ == '__main__':
  lats = [-72.9, -71.9, -74.9, -74.3, -77.5, -77.4, -71.7, -65.9, -65.7,
          -66.6, -66.9, -69.8, -70.0, -71.0, -77.3, -77.9, -74.7]
  lons = [-74, -102, -102, -131, -163, 163, 172, 140, 113,
          88, 59, 25, -4, -14, -33, -46, -74]

  x1,y1 = lonlat_toPlateCarree(lons,lats,dbg=True)
  lon1,lat1 = plateCarree_tolonlat(x1,y1)
  n = 0
  for lon, lat in zip(lons,lats):
    print(f'P1:{n} {lon:.4f} {lat:.4f} {x1[n]:.4f} {y1[n]:.4f} {lon1[n]:.4f} {lat1[n]:.4f}')
    n += 1

  pstest = None
  pstest = 5
  if pstest:
    # Test 50km PS file:
    import os
    import xarray as xr
    tdir='/lustre/storeB/users/davids/Data_Geo'
    if not os.path.exists(tdir):
      tdir= '/home/davids/Work/LANDUSE'
    idir=f'{tdir}/EMEP_files'

    if pstest==50:
      ifile = f'{idir}/AnnualNdep_PS50x_EECCA2005_2009.nc'
      i=59; j=12               # PS coords, location in Spain    
    else:
      i=589; j=126             # PS coords, also Spain    
      ifile = f'{idir}/Landuse_PS_5km_LC.nc'

    print(f'POLAR STEREO {pstest}km:')
    ps=xr.open_dataset(ifile)
    lon2d=ps.lon.values      # from 2-D lon/lat arrays in nc
    lat2d=ps.lat.values

    lon,lat = xy2lonlat(i,j,pstest)

    ii,jj = lonlat2xy(lon,lat,pstest)
    print(f"{i} {j} PS{pstest}km {lon2d[j-1,i-1]:.3f} {lat2d[j-1,i-1]:.3f} TOLL: {lon:.3f} {lat:.3f} FROM LL: {ii} {jj}" )




""" OLD:
def proj1_toPlateCarree(lons,lats):
  pc=pp.Proj('+proj=eqc')  # EPSG 32662  WGS84 Plate Carree
  ll=pp.Proj('+proj=latlon')
  x, y =pp.transform(ll,pc,lons,lats)
  return x, y
def proj1_fromPlateCarree(x,y):
  pc=pp.Proj('+proj=eqc')  # EPSG 32662  WGS84 Plate Carree
  ll=pp.Proj('+proj=latlon')
  lons, lats =pp.transform(pc,ll,x,y)
  return lons, lats

#pc=pp.Proj('+proj=eqc')  # EPSG 32662  WGS84 Plate Carree
#ll=pp.Proj('+proj=latlon')
#x, y =pp.transform(ll,pc,lons,lats)
#transformer=pp.transformer.TransformerFromCRS('EPSG:4326','EPSG:32662')
#new2=pp.transformer.transform(-74.0,-74.7)
#print( new[0][-1], new[1][-1], new2)
#pc=pp.Proj('+proj=eqc')  # EPSG 32662  WGS84 Plate Carree
#ll=pp.Proj('+proj=latlon')
#crsLL= CRS.from_proj4('+proj=latlon')
#crsPC= CRS.from_proj4('+proj=eqc')
"""


