#!/usr/bin/env python3
import numpy as np
import sys

def sfmt(array):
  """ join-function for a list of numbers """
  return ';'.join('%.5f'% x for x in array)
  #return ';'.join('%.5f'% str(x) for x in array)

def normedVals(varray, txt='',minval=1.0e-6,dbg=False):
  """ gets normalised PM fractions for aggregate of input arrays
     Usually used to combine A1+A2=A, F1+F2+F3+F4=F
  """
  dtxt='norming:'

  dbg=True
  if dbg: print(dtxt+txt+'types', type(varray), np.shape(varray), len(varray) )
  if isinstance(varray[0],float): # simple list
    vv = np.array(varray)
    if dbg: print(dtxt+txt+':SIMPLE LIST', np.shape(varray), np.sum(vv), np.sum(varray) )
    if np.sum(varray) < minval: return varray

  else:
    #nvals = np.zeros(len(varray[0])) # default
    if dbg:
       print(dtxt+txt+':COMPLEX TYPE LIST', type(varray), np.shape(varray)) # , np.sum(vv), np.sum(varray) )
       print('VVV', varray)
    vv = np.sum(varray,axis=0)  # length 7 returns
    if dbg: print(dtxt+txt+':COMPLEX TYPE LISTB', type(varray), np.shape(varray) , np.sum(vv), np.sum(varray) )
    #sys.exit()

    if dbg: print(dtxt+txt+':2D LIST=',  np.shape(varray) )

  if np.sum(varray) > 0.0:
    newvals = vv/np.sum(varray)
  else:
    print('ERROR:'+dtxt+txt+' VV zero:', txt, vv, np.sum(varray) )
    sys.exit()
  if dbg: print(dtxt+txt+':RES:', sfmt(newvals), np.sum(newvals) )
  return newvals

def normedVals2(varray, txt='',dbg=False):
  """ gets normalised PM fractions for aggregate of input arrays
     Usually used to combine A1+A2=A, F1+F2+F3+F4=F
    DICT, but tricky..
  """
  dtxt='norming:'

  dbg=True
  if dbg: print(dtxt+txt+'types', type(varray), np.shape(varray), len(varray) )

  if isinstance(varray[0],dict): #  eg F1
    if dbg: print(dtxt+txt+':DICT', np.shape(varray), len(varray), varray[0] )
    for nv, v in enumerate(varray): # Coping with empty dicts
      varray[nv] = v
      if v == {}: varray[nv] = 999 # nvals
      if dbg: print(dtxt+txt+'VSET0 ',nv, varray[nv] )

  if dbg: print(dtxt+txt+'values', varray )
  if isinstance(varray[0],float): # simple list
    vv = np.array(varray)
    nvals = np.zeros(len(varray)) # default
    if dbg: print(dtxt+txt+':SIMPLE LIST', nvals, np.shape(varray) )
  else:
    nvals = np.zeros(len(varray[0])) # default
    vv = np.sum(varray,axis=0)  # length 7 returns
    if dbg: print(dtxt+txt+':2D LIST=', nvals, np.shape(varray) )

  #vv = np.sum(varray,axis=0)  # length 7 returns
  if np.sum(varray) > 0.0:
    nvals = vv/np.sum(varray)
  if dbg: print(dtxt+txt+'VVLENs:', txt, nvals, np.sum(nvals) )
  return nvals

if __name__ == '__main__':
  f1 = np.array([ 1.0, 2.0, 3.0 ])
  f2 = np.array([ 2.0, 2.0, 4.0 ])
  x= normedVals( [ f1, f2], txt='f1f2',dbg=True)
  f3 = np.array([ 0.2, 0.7, 0.1 ])
  y= normedVals( [ f3], dbg=True,txt='[f3]')
  f3 = [ 0.2, 0.7, 0.1 ]
  y= normedVals( f3, dbg=True,txt='f3') # No [] needed now

  if np.sum(f1)>0.0:
   xx=1
  elif np.sum(f1) < -2:
   xx=-2
