#!/usr/bin/env python3
import numpy as np
import sys
from collections import OrderedDict as odict

def obsmodstats (x,y,ymin=0.0,dcLimit=75,dbg=False):
  """
    Calculate stats, with the usual case that x is
    obsverations and may have missing values, and y
    is model results which are complete
    Oct 2021: upadted to cope with missing model values,
    e.g. from partial annual runs.
  """
  dtxt='obsmodstats:'

  stats=odict()
  stats['dc'] = 0.0
  stats['Nvalid']  = 0
  stats['meanx'] = np.nan
  stats['meany'] = np.nan
  stats['bias']  = np.nan
  stats['rbias'] = np.nan # float version
  stats['R']     = np.nan
#FAILED  stats['trend'] = np.nan

  x = np.array(x)
  y = np.array(y)

  for n, xx in enumerate(x): # Obs,  Mod test (maybeonly modelled JJA)
    if np.isnan(xx) or np.isnan(y[n]):
      x[n] = np.nan
      y[n] = np.nan

  f=np.isfinite(x) # grab only real numbers
  stats['Nvalid'] = sum(f)
  stats['dc'] = int( 0.5 +  sum(f)/(0.01*len(x)) ) # Data capture in %
  #print(dtxt+'Data capture test: ', stats['dc'], ' vs ', dcLimit, dbg)
  if stats['dc'] < dcLimit:
    print('Data capture fail: ', stats['dc'], ' vs ', dcLimit)
    return stats

  meanx = np.mean(x[f])
  meany = np.mean(y[f])
  if dbg: print('MEANS ', meanx, meany )
  if ~np.isnan(meanx) and  ~np.isnan(meany): 
    rbias = 100*(meany - meanx)/meanx
    if rbias > 0: 
      stats['bias'] = int(  0.5 + rbias )
    else:
      stats['bias'] = -1 * int(  0.5 - rbias )
    stats['rbias'] = rbias
  stats['R']    = np.corrcoef(x[f],y[f])[0,1]
  stats['meanx'] = meanx
  stats['meany'] = meany
#FAILED  stats['trend'] = np.polyfit(x,y,deg=1)[0]
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
