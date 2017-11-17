#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
  DailyOzoneMetrics operates on incoming 24 hours of O3 data (assumed
  local time and outputs various metrics for that day. So far
  have coded:

    M7, M12, W126_12h, W126_24h
    EUAOT40
    Daily Max

  Where means, max, etc are given, these are for the non-NaN values.
  The routines also return the percentage of valid hours used in
  these calculations, so that the user may choose whether to use
  them or not.

  Time-zones? These codes assume that the data are in the correct
  time-zone already. If needed, the function tzo3 can make this
  shift, and also just return smaller array if hours limited
  NB:
  EU AOT40 is 08:00 - 19:59 CET ie 09:00-20:59 GMT
    # Data for hh==8 say is from 08:00:00 to 09:00:00
    # and 20 gives up to 20:59 say, all GMT

    Valid data? Any O3 less than zero is set to np.nan
"""
import numpy as np
import sys
from StringFunctions import multiwrite  # my code to format lots of elements

def mean_of_ValidHrs(x):
  x  = np.array(x)             # avoids confusions with list behaviour
  meanX = np.NaN
  pValid = np.sum(~np.isnan(x)) #  count number of valid
  #print('MVH ', len(x), pValid, x )
  if len(x) > 0:
    pValid =  (100.0*pValid)/len(x)
    if pValid>0: meanX = np.nanmean(x)
  return  meanX, pValid

def max_of_ValidHrs(x,dbg=False):
  x = np.array(x)             # avoids confusions with list behaviour
  pValid = np.sum(~np.isnan(x)) #  ( x > -999).sum()  # crude way to count number of valid
  maxX = np.NaN
  #pValid = int( 0.5 + (100.0*pValid)/len(x) )
  pValid =  (100.0*pValid)/len(x)
  if pValid > 0: maxX = np.nanmax(x)
  if dbg: print('DMAXX ', x, pValid, maxX)
  return  maxX, pValid

def sum_of_ValidHrs(x):
  x = np.array(x)             # avoids confusions with list behaviour
  pValid = np.sum(~np.isnan(x)) #  ( x > -999).sum()  # crude way to count number of valid
  pValid =  (100.0*pValid)/len(x)
  mX = np.NaN
  if pValid > 0: mX = np.nansum(x)
  return  mX, pValid

def dmean(o3,dbg=False):
  #print ('InDmean ', o3 )
  #print('InDmean res=',  mean_of_ValidHrs( o3 ) )
  return mean_of_ValidHrs( o3 ) 

def dmax(o3,dbg=False):
  if dbg: print('InDmax  res=',  max_of_ValidHrs( o3 ) )
  return max_of_ValidHrs( o3 ) 

# the following functions should be used with corrections for local time.
# For simplicity, we allow wrap arpound, so that e.g. M7 might sometimes
# include the very end and very start of the day if the input O3 is defined
# as a set of UTC values.
#-----------------------------------------------------------------------------
def tzhrs(hh1,hh2,tz=None):
  """ If time zone present, adds to hh1, hh2. Values can exceed 24 """
  if tz:
    assert type(tz) == int, 'tzhrs: time-zone into m7 needs integer, not %5.1g' % tz
  else:
    tz=0
  hh1=hh1+tz; hh2 =hh2+tz            # 09:00 - 15:59
  return hh1, hh2
#-----------------------------------------------------------------------------
def tzo3(o3,hh1=0,hh2=23,tz=None,dbg=None):
  """ Returns copy of input o3 values, but time-shifted for time-zones if
      needed, and for resricted hours if hh1, hh2 specified. 
      If time zone present, adds to hh1, hh2 and assigns values
      in-between to o3used array. Hours wrap-around at 24 """
 # nb version with o3used = nparray, np.append, 2 x slower
  if tz:
    #print('tz check ', tz, type(tz) )
    #assert type(tz) == int, 'tzo3:time-zone needs integer, not %5.1g' % tz
    # stupid system has trouble with np.int64 vs int :-(
    assert (isinstance(tz,np.integer) or isinstance(tz,int)), 'LLLL'
    #assert isinstance((tz,np.int) == int, 'tzo3:time-zone needs integer, not %5.1g' % tz
  else:
    tz=0
  #BUG hh1=hh1+tz; hh2 =hh2+tz
  hh1=hh1-tz; hh2 =hh2-tz    # Need to have e.g CET h=2 from GMT h=1
  o3used = []
  hnew=0
  for h in range(hh1,hh2+1):
     if h > 23: h = h - 24  # we allow wrap-around
     o3used.append( o3[h] )
     if dbg:
       print( 'tzo3: tz=%d hh1=%d hh2=%d h=%d hnew=%d o3=%7.3f'% (tz,hh1,hh2,h, hnew, o3[h]) )
     hnew += 1
  return o3used
#-----------------------------------------------------------------------------
def m7(o3,dbg=False):
  if dbg: print ('InM7 ', o3 )
  o3used = tzo3(o3,10,16,dbg)          # 09:00 - 15:59
  if dbg:
     print ('InM7 ', o3used )
     print('InM7 res=',  mean_of_ValidHrs( o3used ) )
  return mean_of_ValidHrs( o3used ) 
#-----------------------------------------------------------------------------
def m12(o3,dbg=False):
  o3used = tzo3(o3,9,20)          # 08:00 - 19:59
  return mean_of_ValidHrs( o3used ) 
#-----------------------------------------------------------------------------
def AOT40(o3,dbg=False):
  #o3m = [] for i in range(len(o3)): o3m.append( np.max( o3[i]-40.0, 0.0 ) )
  o3m = [ max( o3[i] - 40.0, 0.0)  for  i in range(len(o3)) ]
  o3used = tzo3(o3m,9,20)          # 08:00 - 19:59
  if dbg: print('AOT40 ', o3used)
  return sum_of_ValidHrs(o3used)
#-----------------------------------------------------------------------------
# SOMO35 is based upon max of 8 hr values. We have 16 8h periods in day.
# MDA8 is the same, but it is useful to keep 2 names
def MDA8(o3,dbg=False):
 # o3used = tzo3(o3,10,16,dbg)          # 09:00 - 15:59
  return SOMOY(o3,Y=0.0)
def SOMO35(o3,dbg=False):
 # o3used = tzo3(o3,10,16,dbg)          # 09:00 - 15:59
  return SOMOY(o3,Y=35.0)
def SOMO0(o3,dbg=False):
 # o3used = tzo3(o3,10,16,dbg)          # 09:00 - 15:59
  return SOMOY(o3,Y=0.0)
# For SOMOY, set Y different to 35

def SOMOY(o3,dbg=False,Y=35.0):
  """ returns max 8-hr average in day, for O3> Y ppb.
   As always, make sure o3 is in local time """
  #o3m = [] for i in range(len(o3)): o3m.append( np.max( o3[i]-40.0, 0.0 ) )
  D8max = -999.0
  n = 0
  nValid8hrs = 0
  for hh1 in range(0,16):
    hh2=hh1+8
    avg8 = np.nansum(o3[hh1:hh1+8])
    nValid=0
    if np.isfinite(avg8):
      #print('AVG8 ', hh1, hh1+8, len(o3) )
      nValid = np.sum(np.isfinite( o3[hh1:hh1+8]))  # count number of non-NaNs
      avg8 = avg8/nValid
      D8max = max( D8max,avg8)
      n += 1
      if dbg: print('SOMO-Y', hh1, hh2, nValid, n, avg8, D8max) 
    if D8max < -900 or nValid < 6 :
      D8max = np.nan
    else:
       D8max = np.max( [D8max- Y, 0.0] )
       nValid8hrs += 1
  if dbg: print('SOMO-Y-FINA', nValid8hrs, n, D8max, Y) 

  return D8max, 100.0*nValid8hrs/16.0
#-----------------------------------------------------------------------------
def EUAOT40(o3,dbg=False):
  """ EUAOT40 does not use time-zones - be careful in use """
  hh1= 9; hh2 =20             # 08:00 - 19:59
  aot=0.0
  pValid = 0
  for h in range(hh1,hh2+1):
    if np.isfinite( o3[h] ):
        #aot += max( [0.0,o3[h]-40.0 ]) # nb simple max returns zero for NaN!
        aot += max( 0.0,o3[h]-40.0 ) # nb simple max returns zero for NaN!
        pValid += 1
    if dbg: print( ' AOT ', h, o3[h], max(0.0,o3[h]-40.0), aot, pValid )
  pValid = (100.0*pValid)/(hh2+1-hh1)
  if pValid  < 1.0 : aot = np.NaN
  #print( ' AOTF ', aot, pValid )
  #aot =np.sum(o3[hh1:hh2])
  return aot, pValid

# Was mich slower;
#def EUAOT40m(o3,dbg=False):
#  hh1= 9; hh2 =20             # 08:00 - 19:59
#  aot = [ np.max([0.0, o3-40.0]) for o3 in o3[hh1:hh2+1]]
#  if dbg: print(( "INPUT  ", o3[hh1:hh2+1] ))
#  if dbg: print(( "MAP => ", ' '*12, aot ))
#  #aot = reduce ( lambda o3: max(0.0, o3-40.0), o3[hh1:hh2] )
#  return np.nansum(aot)

def W126_12h(o3,dbg=False):
  return W126(o3,hh1=9,hh2=20,dbg=False)
def W126_24h(o3,dbg=False):
  return W126(o3,hh1=0,hh2=23,dbg=False)

def W126(o3,hh1=0,hh2=23,dbg=False):
  W126=0.0 # np.zeros(len(o3))
  pValid = 0
  if dbg: print('PVAL START ', pValid, hh1, hh2, len(o3) )
  for i in range(hh1,hh2+1): #  range(0,len(o3)):
    if np.isfinite( o3[i] ):
       C=o3[i] #/1000.0   # ppm
       w126i    = C/( 1+4403*np.exp(-0.126*C) )
       W126 += w126i
       pValid += 1
    if dbg: print('PVAL ', i, pValid, hh1, hh2, o3[i], w126i, W126)
  pValid = 100*pValid/(hh2-hh1+1) # (0.01 * len(o3) )
  if dbg: print('PVAL DONE ',  pValid, W126)
    
  return W126, pValid

# ---------------------------------------------------------------------------
# Method of using functions suggested by JohnnyLinBook, ch6
# NB - we use AOT40, not EUAOT40
defmetrics = {'Dmean':dmean,  'Dmax':dmax, 'M7':m7, 'M12':m12, 
   'AOT40':AOT40, 'W126':W126_12h, 'MDA8':SOMO0, 'SOMO35': SOMO35 }
# If we can sum values, set True
accumulated= {'Dmean':False,  'Dmax':False, 'M7':False, 'M12':False, 
   'AOT40':True, 'W126':False, 'SOMO35':True, 'SOMO0':True, 'MDA8':True}
# ---------------------------------------------------------------------------

first_metrics_call = True

def get_metrics(o3,metrics=defmetrics,dbg=False):
  #if first_metrics_call:
  results = {}                      # Initialise results
  o3valid = o3.copy()
  for n in range(len(o3)):
    if o3[n] < 0.0: o3valid[n] = np.nan
  #  for imetric in list(metrics.keys()):  #  dictionary for each
  #     results[imetric] = {}
  #  first_metrics_call = False
  for m in list(metrics.keys()):
      results[m] = metrics[m](o3valid,dbg)
      if dbg: print(('get_metrics: ', metrics[m], results[m] ))
  return results.copy()  # COPY needed to avoid other calls resetting contents 
  #  http://python.net/crew/mwh/hacks/objectthink.html (see objectthink.pdf)

#def get_metrics2(o3,dbg=False):
#  for m in list(metrics.keys()):
#      results[m] = metrics[m](o3,dbg)
#      if dbg: print(('get_metrics: ', metrics[m], results[m] ))
#  return results

if __name__ == '__main__':

  metrics = {'Dmean':dmean,  'Dmax':dmax } #, 'M7':m7, 'M12':m12, 
#   'AOT40':AOT40, 'W126':W126_12h, 'MDA8':SOMO0, 'SOMO35': SOMO35 }
  tz = 0
  dbg=True
  for case in  range(3):
    # Case 1, constant 50 ppb in day, 20 ppb at night
    if case == 0:
       tz = 0 
       o3gmt = np.full(24,50.0)
       o3gmt[:9] = 20.0
       o3gmt[20:] = 20.0
    if case == 1:
       tz = 12
    if case == 2:
       tz = 0
       o3gmt[12] = np.NaN

    o3 = tzo3(o3gmt,tz=tz)
    print("============ CASE ========== ", case, tz, o3[12] )
    print('Test%d with tz=%d ' % (case,tz) + multiwrite(o3,'%3.0f') )

#    gg=EUAOT40(o3)
#    m=m7(o3,dbg=True)
#    print( ' Simple M7: ', tz,  m )
  
  
#    r=get_metrics(o3)  # was metrics2, why?
#    o3p = np.ones(24)
#    z=get_metrics(o3)  # was metrics2, why?
#    for kk, vv in r.items():
#      print(kk, tz, ' R ', vv, ' Z ', z[kk])    # should now be e.g.   dmax   34.5  24
  
    #for kk, vv, nn in r.items():
    #  print(kk, vv, nn)    # should now be e.g.   dmax   34.5  24
  
    # formatting issues. %g only preserves numer of sig figs, dropping zeros.
    #print('TESTR ', r.values())
    r=get_metrics(o3,metrics=metrics,dbg=dbg)
    vals = [ r[kk][0] for kk in r.keys() ] 
    dc   = [ int( r[kk][1]+0.5)  for kk in r.keys() ] 
    #print('TESTR ', vals)
    print('METRIC', multiwrite( r.keys(), '%9s') )
    print('VALS  ', multiwrite( vals, '%9.4g') )
    print('DC    ', multiwrite( dc, '%9d'  ) )
  
    #m, n = mean_of_ValidHrs(o3p)
    #print('TESTok  mean_of-VaidHrs ', m, n)
    #o3p[:] = np.NaN
    #m, n = mean_of_ValidHrs(o3p)
    #print('TESTNaN mean_of_ValidHrs ', m, n)
  
  
  #def meapValidHrs(x,n):
