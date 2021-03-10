#!/usr/bin/env python3
""" Reads in file and variable and returns global sum. Developed for CAMS
 emissions so far, but will expand as needed
 Usage:
   mkGlobalSums.py ifile var_wanted 
"""
import numpy as np
import emxgeo.arealonlatcell as cell
import numpy as np
import sys
import xarray as xr

def areaSum(ifile,var,dbg=False):

  ds=xr.open_dataset(ifile)
  #emis=ds[var] #.Emis
  if dbg:
     print('FILE ', ifile)
     print('VAR  ', var)
     print('SHAPE ', np.shape(ds[var].data), ds[var].data.ndim)
  if ds[var].data.ndim==2:
    vals=ds[var].data[:,:]
  else:
    nt, nj, ni = np.shape(ds[var].data)
    assert nt==1, \
      'Problem: cannot do time-dim yet; shape= %d %d %d' % ( nt, nj, ni)
    vals=ds[var].data[0,:,:]

  units=ds[var].units
  lats=ds[var].lat.data
  lons=ds[var].lon.data
  dLat= lats[1] - lats[0]
  dLon= lons[1] - lons[0]
  assert abs(dLat-dLon) < 1.0e-3, 'Problem: cannot do unequal dLat, dLon yet'
  if dbg: print('max ', np.max(vals), units, 'dLat', dLat)

  g2Tg  = 1.0e-12
  
  # cell area is in km2 = 1.0e6 m2. 
  if units in [ 'ng(N)/m2/s', 'ngN/m2/s' ]:
    ng2Tg = 1.0e-12 * 1.0e-9
    yr = 365.25*24*3600
    unit2Tg = 1.0e6 * yr * ng2Tg
  else:
    sys.exit('Units not recognized: %s'% units)

  sumNew=0.0
  for j, lat in enumerate(lats):
    km2  = cell.AreaLonLatCell(lat,dLat)
    for i, lon in enumerate(lons):
      sumNew += (vals[j,i] * km2)

  sumNew *=  unit2Tg # 1.0e9  # kg -> Tg?
  return sumNew


if __name__ == '__main__':

  if len(sys.argv) == 3:
    ifile=sys.argv[1]
    var = sys.argv[2]
  else:
    ifile='./FertEmis_Mar2021/annual_FertEmis_GLOBAL05_2005_Mar2021.nc'
    var = 'Emis'

  Tg= areaSum(ifile,var)
  print('Global sum:', Tg, 'Tg') #, np.sum(vals))


