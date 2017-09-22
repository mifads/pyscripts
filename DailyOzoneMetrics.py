#!/usr/bin/env python3
"""
  DailyOzoneMetrics operates on incoming 24 hours of O3 data (assumed
  local time and outputs various metrics for that day. So far
  have coded:

    M7, M12
    EUAOT40
    Daily Max

  Where means, max, etc are given, these are for the non-NaN values.
  The routines also return the percentage of valid hours used in
  these calculations, so that the user may choose whether to use
  them or not.

  NB:
  EU AOT40 is 08:00 - 19:59 CET ie 09:00-20:59 GMT
    # Data for hh==8 say is from 08:00:00 to 09:00:00
    # and 20 gives up to 20:59 say, all GMT

"""
import numpy as np
import sys
from StringFunctions import multiwrite  # my code to format lots of elements

def mean_of_ValidHrs(x):
  x  = np.array(x)             # avoids confusions with list behaviour
  mX = np.NaN
  pValid = np.sum(~np.isnan(x)) #  ( x > -999).sum()  # crude way to count number of valid
  #print('MVH ', len(x), pValid, x )
  if len(x) > 0:
    pValid =  (100.0*pValid)/len(x)
    if pValid>0: mX = np.nanmean(x)
  return  mX, pValid

def max_of_ValidHrs(x):
  x = np.array(x)             # avoids confusions with list behaviour
  pValid = np.sum(~np.isnan(x)) #  ( x > -999).sum()  # crude way to count number of valid
  mX = np.NaN
  #pValid = int( 0.5 + (100.0*pValid)/len(x) )
  pValid =  (100.0*pValid)/len(x)
  if pValid > 0: mX = np.nanmax(x)
  return  mX, pValid

def sum_of_ValidHrs(x):
  x = np.array(x)             # avoids confusions with list behaviour
  pValid = np.sum(~np.isnan(x)) #  ( x > -999).sum()  # crude way to count number of valid
  pValid =  (100.0*pValid)/len(x)
  mX = np.NaN
  if pValid > 0: mX = np.nansum(x)
  return  mX, pValid

def dmean(o3,tz=None,dbg=False):
  #print ('InDmean ', tz, o3 )
  #print('InDmean res=',  mean_of_ValidHrs( o3 ) )
  return mean_of_ValidHrs( o3 ) 

def dmax(o3,tz=None,dbg=False):
  if dbg: print('InDmax  res=',  mean_of_ValidHrs( o3 ) )
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
def tzo3(hh1,hh2,o3,tz=None,dbg=None):
  """ General calculation function for M7, M12 .. type metrics
      If time zone present, adds to hh1, hh2 and assigns values in-between
      to o3used array. Hours wrap-arpund at 24 """
 # nb version with o3used = nparray, np.append, 2 x slower
  if tz:
    #print('tz check ', tz, type(tz) )
    #assert type(tz) == int, 'tzo3:time-zone needs integer, not %5.1g' % tz
    # stupid system has trouble with np.int64 vs int :-(
    assert (isinstance(tz,np.integer) or isinstance(tz,int)), 'LLLL'
    #assert isinstance((tz,np.int) == int, 'tzo3:time-zone needs integer, not %5.1g' % tz
  else:
    tz=0
  hh1=hh1+tz; hh2 =hh2+tz
  o3used = []
  for h in range(hh1,hh2+1):
     if h > 23: h = h - 24  # we allow wrap-around
     o3used.append( o3[h] )
     if dbg:
       print( 'tzo3: tz=%d hh1=%d hh2=%d h=%d o3=%7.3f'% (tz,hh1,hh2,h,o3[h]) )
  return o3used
#-----------------------------------------------------------------------------
def m7(o3,tz=None,dbg=False):
  if dbg: print ('InM7 ', tz, o3 )
  o3used = tzo3(10,16,o3,tz,dbg)          # 09:00 - 15:59
  if dbg:
     print ('InM7 ', tz, o3used )
     print('InM7 res=',  mean_of_ValidHrs( o3used ) )
  return mean_of_ValidHrs( o3used ) 
#-----------------------------------------------------------------------------
def m12(o3,tz=None,dbg=False):
  o3used = tzo3(9,20,o3,tz)          # 08:00 - 19:59
  return mean_of_ValidHrs( o3used ) 
#-----------------------------------------------------------------------------
def tzAOT40(o3,tz=None,dbg=False):
  #o3m = [] for i in range(len(o3)): o3m.append( np.max( o3[i]-40.0, 0.0 ) )
  o3m = [ max( o3[i] - 40.0, 0.0)  for  i in range(len(o3)) ]
  o3used = tzo3(9,20,o3m,tz)          # 08:00 - 19:59
  if dbg: print('tzAO ', o3used)
  return sum_of_ValidHrs(o3used)
#-----------------------------------------------------------------------------
# SOMO35 is based upon max of 8 hr values. We have 16 8h periods in day.
# MDA8 is the same, but it is useful to keep 2 names
def MDA8(o3,tz=None,dbg=False):
  return tzSOMOY(o3,tz,Y=35.0)
def tzSOMO35(o3,tz=None,dbg=False):
  return tzSOMOY(o3,tz,Y=35.0)
def tzSOMO0(o3,tz=None,dbg=False):
  return tzSOMOY(o3,tz,Y=0.0)
# For SOMOY, set Y different to 35
def tzSOMOY(o3,tz=None,dbg=False,Y=35.0):
  #o3m = [] for i in range(len(o3)): o3m.append( np.max( o3[i]-40.0, 0.0 ) )
  D8max = -999.0
  n = 0
  nValid8hrs = 0
  for hh1 in range(0,16):
    hh2=hh1+8
    avg8 = np.nansum(o3[hh1:hh1+8])
    nValid=0
    if np.isfinite(avg8):
      nValid = np.sum(np.isfinite( o3[hh1:hh1+8]))  # count number of non-NaNs
      tmp = avg8
      avg8 = avg8/nValid
      D8max = max( D8max,avg8)
      n += 1
      if dbg: print('SOMO-Y', hh1, hh2, nValid, n, tmp, avg8, D8max) 
    if D8max < -900 or nValid < 6 :
      D8max = np.nan
    else:
       D8max = np.max( [D8max- Y, 0.0] )
       nValid8hrs += 1
  if dbg: print('SOMO-Y-FINA', nValid8hrs, n, D8max, Y) 

  #if dbg: print('tzAO ', o3used)
  return D8max, 100.0*nValid8hrs/16.0
#-----------------------------------------------------------------------------
def EUAOT40(o3,tz=None,dbg=False):
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

def W126(o3,tz=None,dbg=False):
  W126=np.zeros(len(o3))
  pValid = 0
  for i in range(0,len(o3)):
    if np.isfinite( o3[i] ):
       C=o3[i] #/1000.0   # ppm
       W126[i] = C/( 1+4403*np.exp(-0.126*C) )
       pValid += 1
  pValid = pValid/(0.01 * len(o3) )
    
  return np.sum(W126), pValid

# ---------------------------------------------------------------------------
# Method of using functions suggested by JohnnyLinBook, ch6
# NB - we use tzAOT40, not EUAOT40
#metrics = {'Dmean':dmean,  'Dmax':dmax, 'M7':m7, 'M12':m12, 'AOT40':tzAOT40, 'W126':W126, 'SOMO0':tzSOMO0, 'SOMO35': tzSOMO35 }
metrics = {'Dmean':dmean,  'Dmax':dmax, 'M7':m7, 'M12':m12, 'AOT40':tzAOT40, 'W126':W126, 'MDA8':tzSOMO0, 'SOMO35': tzSOMO35 }
# If we can sum values, set True
accumulated= {'Dmean':False,  'Dmax':False, 'M7':False, 'M12':False, 'AOT40':True, 'W126':False, 'SOMO35':True, 'SOMO0':True, 'MDA8':True}
# ---------------------------------------------------------------------------

results = {}                      # Initialise results
for imetric in list(metrics.keys()):  #  dictionary for each
     results[imetric] = {}

def get_metrics(o3,tz=0,dbg=False):
  for m in list(metrics.keys()):
      results[m] = metrics[m](o3,tz,dbg)
      if dbg: print(('get_metrics: ', metrics[m], results[m] ))
  return results.copy()  # COPY needed to avoid other calls resetting contents 
  #  http://python.net/crew/mwh/hacks/objectthink.html (see objectthink.pdf)

#def get_metrics2(o3,tz=0,dbg=False):
#  for m in list(metrics.keys()):
#      results[m] = metrics[m](o3,tz,dbg)
#      if dbg: print(('get_metrics: ', metrics[m], results[m] ))
#  return results


if __name__ == '__main__':

  o3 = np.linspace(0,23,24)
  o3p = o3 + 30.0
  gg=EUAOT40(o3p)

  m=m7(o3,dbg=True)
  print( ' Simple M7: ',  m )
  m=m7(o3,tz = 12, dbg=True)
  print( ' TZ+12: ',  m )

  r=get_metrics(o3p)
  for kk, vv in r.items():
    print('o3p ', kk, vv)

  o3p[12] = np.NaN
  #io=sys.stdout
  print('TestO3  #2 hours   '+ multiwrite(range(0,24),'%5d') )
  print('TestO3  #2 with NaN'+ multiwrite(o3p,'%5.1f') )

  r=get_metrics(o3p)  # was metrics2, why?
  o3p = np.ones(24)
  z=get_metrics(o3p)  # was metrics2, why?
  for kk, vv in r.items():
    print(kk, ' R ', vv, ' Z ', z[kk])    # should now be e.g.   dmax   34.5  24

  #for kk, vv, nn in r.items():
  #  print(kk, vv, nn)    # should now be e.g.   dmax   34.5  24

  # formatting issues. %g only preserves numer of sig figs, dropping zeros.
  print('TESTR ', r.values())
  vals = [ r[kk][0] for kk in r.keys() ] 
  nums = [ r[kk][1] for kk in r.keys() ] 
  print('TESTR ', vals)
  print('TESTR ', multiwrite( r.keys(), '%9s') )
  print('TESTR ', multiwrite( vals, '%9.4g') )
  print('TESTR ', multiwrite( nums, '%9d'  ) )

  m, n = mean_of_ValidHrs(o3p)
  print('TESTok  mean_of-VaidHrs ', m, n)
  o3p[:] = np.NaN
  m, n = mean_of_ValidHrs(o3p)
  print('TESTNaN mean_of_ValidHrs ', m, n)


#def meapValidHrs(x,n):
