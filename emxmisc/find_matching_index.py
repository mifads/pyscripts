#!/usr/bin/env python3
import numpy as np
import sys

def find_matching_index(x,y,tol=1.0e-6,dbg=False):
  """ finds index of match f found """
  if x<y[0]: return -888
  if x>=y[-1]: return -777

  for n, yn in enumerate(y):
   dy = np.abs( x-yn )
   if dbg: print(f'TEST {x:6.2f} {n} {yn:6.2f}' , dy < tol )
   if dy < tol:
     if dbg: print(f'FOUND {x:6.2f} {n} {yn:6.2f}' )
     return n
  return -999 # if not found

if __name__ == '__main__':

  y=np.array([ -30., -14., -2., -0.1, 1, 2., 5, 10. ])

  for x in [ -14., -7,  5.  ]:
    print(f'CHECK MATCH: {x} in {y} => ')
    idx=find_matching_index(x,y,dbg=False)
    if idx>=0:
      print(x, idx, y[idx] )
    else:
      print(x, idx, 'FAILED')

