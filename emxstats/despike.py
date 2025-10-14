#!/usr/bin/env python3
import bottleneck as bn
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import timeit as ti
"""
  Removes spikes from data-series
  Tried various systems, but  the check4spikes_bn seemed to work best
"""


def check4spikes_bn(b):
  """ we wrap a little first, so that spikes on 1st and last
      entries can be handled
      examples for b = [ 0, 1, 10, 2, 3 ]
  """
  b3 = np.append([ b[-1] ],b)   # =>  [ 3, 0, 1, 10, 2, 3 ]
  b3 = np.append(b3, b[0] )     # =>  [ 3, 0, 1, 10, 2, 3, 0 ]
  b3 = np.append(b3, b[1] )     # =>  [ 3, 0, 1, 10, 2, 3, 0, 1 ]
  b=bn.move_median(b3,window=3,min_count=3)  # [nan, nan,  1.,  1., 2., 3., 2.,  1.]
  #print('B3ut', b[:6], b3[:5] )
  return b[2:-1]                # => [1., 1., 2., 3., 2.]

def check4spikes_pd(x):
  x3 = np.append([ x[-1] ],x) 
  x3 = np.append(x3, x[0] ) 
  df=pd.DataFrame(x3)
  z=df.rolling(window=3,center=True,).median().values[:,0]
  return z[1:-1]

# OLDER:
#https://gist.github.com/w121211/fbd35d1a8776402ac9fe24654ca8044f
def relative_madness( x ):
    return abs( x[1] - np.median(x) ) - np.median( abs( x - np.median(x) ) )

def check_ratio(x):
  neighbours = 0.5*(x[0]+x[2])
  medn1   = np.median(x) # = 0.5*(x[0]+x[2])
  medn2   = np.median([x[0],x[2]])
  r1  = abs( (x[1] - neighbours)/neighbours )
  r2  = abs( x[1] - np.median(x) )/medn2 # ian(x)
  print('R', x, neighbours, medn1, medn2,   r1, r2) #  y[n] )
  return r1, r2

def fix_ends(p,q):
  """ p is the original array, q is the array after smoothing, with nan at ends
      If p0 or p-1 is a spike, we really don't want to copy. So, to be safe:
  """
  if p[0]>2*q[1]:
    q[0] = q[1]
  else:
    q[0] = p[0]
  if p[-1]>2*q[-2]:
    q[-1] = q[-2]
  else:
    q[-1] = p[-1]
  return q

if __name__ == '__main__':
  #xx=np.loadtxt('spikes.txt')
  #x=xx[:,1]
  x=np.array([
    0.000028, 0.000025, 0.000006, 0.000130, 0.000003,
    0.000006, 0.000000, 0.000009, 0.000019, 0.000025,
    0.000037, 0.000043, 0.000046, 0.000049, 0.000059,
    0.000071, 0.000077, 0.000000, 0.000090, 0.000096,
    0.000105, 0.000111, 0.000120, 0.000120, 0.000117,
    0.000117, 0.000111, 0.000099, 0.000090, 0.000080,
    0.000068, 0.000056, 0.000040, 0.000031, 0.000022,
    0.00012 ])

  """ We tried extend the array to allow moving averages to cover all of x, but
     spikes at points 0 and -1 cause problems - we don't want to copy these
  """
  nx=len(x)
  
  """ OLDER
  #df['Madness'] = pd.rolling_apply( df.Data, 3, relative_madness, center=True )
  #df.boxplot(column=['Madness'],by='Spike')
  y=x.copy()
  for n in range(1,nx-1):
    #y[n] =  relative_madness(x[n-1:n+2])
    #m,r  =  relative_madness(x[n-1:n+2])
    r1,r2  =  check_ratio(x[n-1:n+2])
    if r2>0.5: y[n] = 0.5*(x[n-1]+x[n+1])
    #print('X',n, x[n-1:n+2], m, r) #  y[n] )
  """
  
  t0=ti.default_timer()
  p = check4spikes_pd(x)
  t1=ti.default_timer()
  print(f'P  {t1-t0:12.8f}')
  
  # Fastest, by fac 10 about.
  t0=ti.default_timer()
  b = check4spikes_bn(x)
  t1=ti.default_timer()
  print(f'B  {t1-t0:12.8f}')
  
  #sys.exit()
  dy=0.000001
  plt.plot(x,label='In')
  plt.plot(p-dy,label='PD')
  plt.plot(b+dy,label='BN')
  plt.legend()
  plt.show()
  plt.clf()
  
