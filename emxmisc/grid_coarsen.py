#!/usr/bin/env python3
import dask.array as da
import xarray as xr
import numpy as np
import sys


def coarsen(x,dx=2,dy=2,f=np.nanmean,trim_excess=False):
  """ Uses dask coarsen method to extract coarser grid
      CONSIDER trim_excess=True as default, but not sure of
      implications yet """
  xx = da.array.array(x)
  if xx.ndim == 3: # assumed t,j,i
    cx = da.coarsen(f,xx,{0:1,1:dy,2:dx},trim_excess=trim_excess)
  elif xx.ndim == 2: # assumed e.g. j,i,
    cx = da.coarsen(f,xx,{0:dy,1:dx},trim_excess=trim_excess)
  elif xx.ndim == 1: # assumed e.g. lons
    cx = da.coarsen(f,xx,{0:dx},trim_excess=trim_excess)
  return cx.compute()

