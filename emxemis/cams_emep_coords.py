#!/usr/bin/env python3
""" collection of methods to get grid coords. Ranges from simple
    use of np-linspace to reading from a file.
    Also has rolls to convert EMEP to CAMS or vice-vers

     def getCamsGlobal05coords(dbg=False):
     def getEmepGlobal05coords(dbg=False):
     def getemepgrid(emepfile):
     def getGridInfo(lats,lons):
     def getEmepGlobal05grid():
     def getCamsGlobal05grid():
     def rollRight3D(camsstyle,dbg=False):
     def rollLeft3D(emepstyle,dbg=False):
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
  import netCDF4
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

def getEmepGlobal05grid():
  xlats, xlons = getEmepGlobal05coords(dbg=True)
  return getGridInfo(xlats, xlons)

def getCamsGlobal05grid():
  xlats, xlons = getCamsGlobal05coords(dbg=True)
  return getGridInfo(xlats, xlons)

def rollRight2D(camsstyle,dbg=False):
   """ converts EMEP-style (-179.25) to CAMS-style (-179.75)"""
   c=camsstyle.copy()  # emepstyle
   return np.roll(c,+1,axis=1)

def rollRight3D(camsstyle,dbg=False):
   """ converts EMEP-style (-179.25) to CAMS-style (-179.75)"""
   c=camsstyle.copy()  # emepstyle
   return np.roll(c,+1,axis=2)

def rollLeft3D(emepstyle,dbg=False):
   """ converts CAMS-style (-179.75) to EMEP-style (-179.25)"""
   c=emepstyle.copy()  # camsstyle
   return np.roll(c,-1,axis=2)
  
if __name__ == '__main__':

  xlats, xlons = getCamsGlobal05coords(dbg=True)
  grid=getGridInfo(xlats, xlons)
  print('CAMS GRID', grid['lons'][0] )
  xlats, xlons = getEmepGlobal05coords(dbg=True)
  grid=getGridInfo(xlats, xlons)
  print('EMEP GRID', grid['lons'][0] )

  e=np.ones([12,4,10]) # fake emep lat,lon
  f=np.ones([4,10]) # fake emep lat,lon
  mm=2
  e[:,2,1]  = 111 # need to shift longitude right
  e[:,2,-1] = 999 # need to shift longitude right
  f[2,1]  = 111 # need to shift longitude right
  f[2,-1] = 999 # need to shift longitude right
  print('RROLL pre ', e[mm,2,0], e[mm,2,1], e[mm,2,2], '..', e[mm,2,-2], e[mm,2,-1] )
  e = rollRight3D(e)
  print('RROLL pos ', e[mm,2,0], e[mm,2,1], e[mm,2,2], '..', e[mm,2,-2], e[mm,2,-1] )
  e = rollLeft3D(e)
  print('LROLL pos ', e[mm,2,0], e[mm,2,1], e[mm,2,2], '..', e[mm,2,-2], e[mm,2,-1] )
  print('RROLL 2D pre ', f[2,0], f[2,1], f[2,2], '..', f[2,-2], f[2,-1] )
  f = rollRight2D(f)
  print('RROLL 2D pos ', f[2,0], f[2,1], f[2,2], '..', f[2,-2], f[2,-1] )
