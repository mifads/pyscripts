#!/usr/bin/env python3
""" collection of methods to get grid coords. Ranges from simple
    use of np-linspace to reading from a file.
"""
import numpy as np

def getCamsGlobal05coords(dbg=False):
  dtxt='camsCoor:'
  lons=np.linspace(-179.75,179.75,720)
  lats=np.linspace(-89.75,89.75,360)
  if dbg: print(dtxt+'Lats ', lats[0], lats[-1], len(lats))
  if dbg: print(dtxt+'Lons ', lons[0], lons[-1], len(lons))
  return lats, lons

def getEmepGlobal05coords(dbg=False):
  dtxt='emepCoor:'
  lons=np.linspace(-179.25,180.25,720)
  lats=np.linspace(-89.75,89.75,360)
  if dbg: print(dtxt+'Lats ', lats[0], lats[-1], len(lats))
  if dbg: print(dtxt+'Lons ', lons[0], lons[-1], len(lons))
  return lats, lons

def getemepgrid(emepfile):
  """  get EMEP coords for masking and return dict. Note:
       emep lons: -179.25 .. 180.25  URGH
       emep lats: -89.75 .. 89.75
  """

  grid=netCDF4.Dataset(emepfile)
  lats=grid.variables['lat'][:]
  lons=grid.variables['lon'][:]
  grid.close()
  return getGridInfo(lats,lons)


def getGridInfo(lats,lons):
  """  get grid edges and dimensions from uniform lat, lon arrays """

  ny=len(lats); nx=len(lons)
  dlon=lons[1]-lons[0]; dlat=lats[1]-lats[0]
  lon0edge=lons[0]-0.5*dlon; lat0edge=lats[0]-0.5*dlat  # left/bottom edge 

  gridout = dict( lats=lats, lons = lons, nx=nx, ny=ny,
      dlon=dlon, dlat=dlat, lon0edge=lon0edge, lat0edge = lat0edge )
  return gridout


if __name__ == '__main__':
  xlats, xlons = getCamsGlobal05coords(dbg=True)
  xlats, xlons = getEmepGlobal05coords(dbg=True)
  grid=getGridInfo(xlats, xlons)
  print(grid)
