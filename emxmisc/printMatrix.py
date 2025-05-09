#!/usr/bin/env python3
import numpy as np
import emxgeo.check_coord_deltas as cc

""" with nj=2 print_xymatrix prints out 5x5 matrix of points surrounding
     xp,yp. Usually used for map plots. Assues z[y,x] order """

#-----------------------------------------------------------------------------
def find_index(crds,crd):
  dc=cc.check_coord_deltas(crds)
  crd0= crds[0]-0.5*dc
  return int( (crd-crd0)/dc )

#-----------------------------------------------------------------------------
def print_xymatrix(txt,xp,yp,x,y,z,nj=2,dbg=False):

  dx=cc.check_coord_deltas(x)
  dy=cc.check_coord_deltas(y)
  print(f'GRID-{txt}: {dx:.3f}x{dy:.3f} max={np.max(z)}  IJ{z[7,13]}')
  i=find_index(x,xp)
  j=find_index(y,yp)
  print('XP,YP', xp,yp,i,j, 'Zp=', z[j,i])
  if dbg:
    print('XMAT', x)
    print('YMAT', y)
  i1 = max(i-2, 0)
  i2 = min(i+2, len(x))
  j1 = max(j-nj,0)
  j2 = min(j+nj+1,len(y))
  print(f'{txt:10s}',end='')
  for ix in range(i1,i2):
    print(f'{x[ix]:10.2f}',end='')
  print()
  for iy in range(j1,j2):
    print(f'{y[iy]:10.2f}',end='')
    for ix in range(i1,i2):
      print(f'{z[iy,ix]:10.2f}',end='')
    print()

if __name__ == '__main__':
  import numpy as np

  lons=np.linspace(10.0,30.0,21)
  lats=np.linspace(45.0,65.0,21)
  z=np.ones([len(lats),len(lons)])
  xlat = 52.0; xlon=23.0
  ix=find_index(lons,xlon)
  iy=find_index(lats,xlat)
  z[iy,ix] = 88.0
  print(f'Input: IX {ix} IY {iy}   {lons[ix]} {lats[iy]} {z[iy,ix]}')

  print_xymatrix('Test88',xlon,xlat,lons,lats,z,nj=2)
  

