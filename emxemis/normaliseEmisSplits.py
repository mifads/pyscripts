#!/usr/bin/env python3
import numpy as np

def normedVals(varray, txt='',dbg=False):
  """ gets normalised PM fractions for aggregate of input arrays
     Usually used to combine A1+A2=A, F1+F2+F3+F4=F
  """
  nvals = np.zeros(len(varray[0])) # default
  dtxt='norming:'
  if dbg: print(dtxt+'NARRAY: ', np.shape(varray))
  for nv, v in enumerate(varray): # Coping with empty dicts
    if isinstance(v,dict):
        varray[nv] = nvals
        if dbg: print(dtxt+'VSET0 ',nv, varray[nv] )
  vv = np.sum(varray,axis=0)  # length 7 returns
  if np.sum(varray) > 0.0:
    nvals = vv/np.sum(varray)
  if dbg: print(dtxt+'VVLENs:', txt, nvals, np.sum(nvals) )
  return nvals

if __name__ == '__main__':
  f1 = np.array([ 1.0, 2.0, 3.0 ])
  f2 = np.array([ 2.0, 2.0, 4.0 ])
  x= normedVals( [ f1, f2], dbg=True)
  f3 = np.array([ 0.2, 0.7, 0.1 ])
  y= normedVals( [ f3], dbg=True)
