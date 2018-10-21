#!/usr/bin/env python3
"""
 Want to make means over same period, with oo>0 and not NaN
 Had problems with NaNs and array comparison
 eg fmask=np.logical_and(np.isfinite(x), x > 0.0) gave:

/usr/bin/ipython3:1: RuntimeWarning: invalid value encountered in greater
  #! /bin/sh

Solution from https://stackoverflow.com/questions/47340000/how-to-get-rid-of-runtimewarning-invalid-value-encountered-in-greater
"""
import numpy as np

def compare_nan_array(func,a,thresh):
  out = ~np.isnan(a)
  out[out] = func(a[out], thresh)
  return out

if __name__ == '__main__':

  x=np.full(7,np.nan)
  x[1] =  1.0; x[3] =  3.0; x[5] = -5.0
  f= compare_nan_array(np.greater,x,0.0)
  print('Input : ', x)
  print('Filter: ', f)

