#!/usr/bin/env python3
"""
   Very simple map plotting, using imshow.
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

if __name__ == '__main__':
  x=np.ones([180,360])  # typical emep domain
  for i in range(360):
      x[:,i] = i

  plotmap(x,'TestX')

