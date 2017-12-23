#!/usr/bin/env python3
import numpy as np
from collections import OrderedDict as odict

def obsmodstats (x,y,ymin=0.0,dcLimit=75,dbg=False):
  """
    Calculate stats, with the usual case that x is
    obsverations and may have missing values, and y
    is model results which are complete
  """

  stats=odict()
  stats['dc'] = 0.0
  stats['meanx'] = np.nan
  stats['meany'] = np.nan
  stats['bias']  = np.nan
  stats['R']     = np.nan

  x = np.array(x)
  y = np.array(y)

  for n, yy in enumerate(x):
    if yy < 0.0:
      x[n] = np.nan

  f=np.isfinite(x)
  stats['dc'] = int( 0.5 +  sum(f)/(0.01*len(x)) ) # Data capture in %
  if stats['dc'] < dcLimit:
    print('Data capture fail: ', stats['dc'], ' vs ', dcLimit)
    return stats

  meanx = np.mean(x[f])
  meany = np.mean(y[f])
  if dbg: print('MEANS ', meanx, meany )
  stats['bias'] = int(  0.5+  100*(meany - meanx)/meanx )
  stats['R']    = np.corrcoef(x[f],y[f])[0,1]
  stats['meanx'] = meanx
  stats['meany'] = meany
  if dbg:
    for k, v in stats.items():
       print('STATS %-10s %8.3f'% (k, v) )
  return stats

if __name__ == '__main__':

  jdays = list(range(1,366))
  x = 30.0 +50* np.sin(jdays)
  y = 40.0 +50* np.sin(jdays)

  x[40:60] = np.nan
  t1= obsmodstats (x,y,dcLimit=75)
  print(t1)
  t2= obsmodstats (x,y,dcLimit=50)
  print(t2)
