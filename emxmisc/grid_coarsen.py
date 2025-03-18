#!/usr/bin/env python3
import dask as da
import xarray as xr
import numpy as np
import sys


def coarsen(x,dx=2,dy=2,f=np.nanmean):
  """ Uses dask coarsen method to extract coarser grid """
  xx = da.array.array(x)
  if xx.ndim == 3: # assumed t,j,i
    cx = da.array.coarsen(f,xx,{0:1,1:dy,2:dx}) #.compute()
  elif xx.ndim == 2: # assumed e.g. j,i,
    cx = da.array.coarsen(f,xx,{0:dy,1:dx}) #.compute()
  elif xx.ndim == 1: # assumed e.g. lons
    cx = da.array.coarsen(f,xx,{0:dx}) #.compute()
  return cx.compute()

