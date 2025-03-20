#!/usr/bin/env python3
import numpy as np
""" checks for uniform coord deltas """

def check_coord_deltas(coords,stop_if_variable=True,tol=0.0001):
  dc = [ coords[n] - coords[n-1] for n in range(1,len(coords)) ]
  maxdc = max(dc)
  mindc = min(dc)
  #ok = 0.9999 <  maxdc/mindc < 1.0001
  ok = 1-tol <  maxdc/mindc <  1+tol
  assert ok,f'VARIABLE coords! {maxdc} {mindc}'
  return np.mean(dc) #, mindc, maxdc

def coords_equal(dx,dy,tol=0.0001):
  return np.abs(dx-dy) < tol 
