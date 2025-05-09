#!/usr/bin/env python3
import numpy as np
import sys

def find_lower_index(x,yin,dbg=False):
  """ finds lowest index of bracketing pair. Copes with both
   ascending and descending arrays """
  y=yin.copy()
  ascending = (y[-1] > y[0])
  if ascending==False:
    y=yin[::-1] # tmp local reverse
  if x<y[0]: return -888
  if x>=y[-1]: return -999

  for n in range(len(y[:-2])):
   if dbg: print(f'TEST {x:6.2f} {n} {y[n]:6.2f} {y[n+1]:6.2f}', ascending, x<y[n] )
   if x>=y[n] and x< y[n+1]:
     if dbg: print(f'FOUND {x:6.2f} {n} {y[n]:6.2f} {y[n+1]:6.2f}' )
     # index in rev. yin[0] = y[-1], so nrev= -(n+1)
     # but we also need to put "left" another step
     if ascending==False:
       nrev = len(y) - (n+2)
       if dbg: print(f'FinREV {x:6.2f} {nrev} {yin[nrev]:6.2f} {yin[nrev+1]:6.2f}' )
       return nrev
     else:
       return n

if __name__ == '__main__':

  y=np.array([ -30., -14., -2., -0.1, 1, 2., 5, 10. ])

  print('ASCENDING: xxxxxxxxxxxxxxxxxx')
  for x in [ -32, -30, -29, -20, -3, -0.2, 0.0, 3, 10.0, 10.1 ]:
    idx=find_lower_index(x,y,dbg=False)
    if idx>=0:
      print(x, idx, y[idx], y[idx+1] )
    else:
      print(x, idx, 'FAILED')

  print('DESCENDING: xxxxxxxxxxxxxxxxxx')
  print('z:', y[::-1])
  z=y[::-1] # reversed, e.g. 
  for x in [ -32, -30, -29, -20, -3, -0.2, 0.0, 3, 10.0, 10.1 ]:
    idx=find_lower_index(x,z,dbg=True)
    if idx>=0:
      print('REV', x, idx, z[idx], z[idx+1] )
    else:
      print('REV', x, idx, 'FAILED')
