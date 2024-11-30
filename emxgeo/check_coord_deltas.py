#!/usr/bin/env python3
import numpy as np
""" checks for uniform coord deltas """

def check_coord_deltas(coords,stop_if_variable=True):
  dc = [ coords[n] - coords[n-1] for n in range(1,len(coords)) ]
  maxdc = max(dc)
  mindc = min(dc)
  ok = 0.9999 <  maxdc/mindc < 1.0001
  assert ok,f'VARIABLE coords! {maxdc} {mindc}'
  return np.mean(dc) #, mindc, maxdc

