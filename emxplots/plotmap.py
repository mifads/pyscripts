#!/usr/bin/env python3
"""
   Very simple map plotting, using imshow.
   or for simple points on nice background map.
   For more advanced, use plotCdfMap.py
"""
import matplotlib.pyplot as plt
import numpy as np
import netCDF4
import os
import sys

def plotmap(x,txt,plotfile=None):
  """ simplest imshow map """
  plt.imshow(x,origin='lower',cmap='jet_r') # jet_r to match Hudman
  plt.colorbar()
  plt.title(txt)
  if plotfile is None:
    plt.show()
  else:
    plt.savefig(plotfile)
  plt.clf()

def plotlonlatmap(lons,lats,vals,levels,
        cmap='YlOrRd',img_bounds= [-30.0, 55.0, 30.0, 65.0 ],
        cbar_shrink=0.5,idbg=None,jdbg=None,ofile=None
    ):
  """ maps with cartopy world also """
  import cartopy.crs as ccrs
  from matplotlib.colors import ListedColormap, BoundaryNorm # for hetero, from Zhuyun/NMR
  nmrcolors = ['#CCDEEB', '#96CCEB', '#66B7F3', '#62C298', '#76E854','#EAEB30',
     '#E4CC2F', '#EA952A','#F74B37', '#C52C2C']
 
  cm = plt.colormaps[cmap]
  cm = ListedColormap(nmrcolors)
  cm.set_under('0.75')
  cm.set_over('0.25')
  norm = BoundaryNorm(levels, ncolors=cm.N, clip=False)
  proj = ccrs.PlateCarree()
  fig = plt.figure(figsize=(10, 4))
  f, ax1 = plt.subplots(1, 1, subplot_kw=dict(projection=proj))
  ax1.set_extent(img_bounds,crs=ccrs.PlateCarree())
  ax1.coastlines(resolution='10m') # 10, 50, 110
  ax1.gridlines()
  #cmap = ListedColormap(nmrcolors)
  p=ax1.pcolormesh(lons,lats,vals,cmap=cm,norm=norm,transform=ccrs.PlateCarree())
  #cbar=plt.colorbar(hhh,cax=ax_cb,ticks=v,extend='both')
  #cbar=plt.colorbar(p,ticks=levels,extend='both')
  cbar=plt.colorbar(p,extend='both',shrink=cbar_shrink)
 
  if idbg is not None:
    print(f'DBGplotlonlatmap: {lons[idbg]:.3f}E {lats[jdbg]:.3f}N  VALS{vals[jdbg,idbg]} {cm.N}')
  if ofile is None:
    plt.show()
  else:
    plt.savefig(ofile)
  plt.clf()

def plot_map_pts(x,y,z,col='r',title='',ofile=None):

  import cartopy.crs as ccrs

  fig = plt.figure(figsize=(10, 4))
  ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

  # make the map global rather than have it zoom in to
  # the extents of any plotted data
  ax.set_global()

  ax.stock_img()
  ax.coastlines()

  ax.scatter(x,y,z,color=col)
  if len(title)>0:
    plt.title(title,fontsize=14)

  plt.tight_layout()
  if ofile is None:
    plt.show()
  else:
    plt.savefig(ofile)
  plt.clf()

if __name__ == '__main__':
  x=np.ones([180,360])  # typical emep domain
  for i in range(360):
      x[:,i] = i

  plotmap(x,'TestX')

  x = np.linspace(-10,40,10)
  y = np.linspace(30,60,10)
  z = np.linspace(0,100,10)
  plot_map_pts(x,y,z,'r')


