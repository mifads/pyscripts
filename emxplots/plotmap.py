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
  plt.imshow(x,origin='lower',cmap='jet_r') # jet_r to match Hudman
  plt.colorbar()
  plt.title(txt)
  if plotfile is None:
    plt.show()
  else:
    plt.savefig(plotfile)
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


