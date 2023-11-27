#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
  Simple numerical functions to help remember what to do

    nint - equivalent to fortran nint. Copes with negative numbers
                which int or int(x+0.5) gets wrong
    intround  - rounds integers to given number of significant digits
"""

def nint(x):
      return int(round(x))

def intround(n, p):
   ''' rounds an integer. if "p"<0, p is a exponent of 10; if p>0, left to
       right digits. Code from
       https://stackoverflow.com/questions/3348825/how-to-round-integers-in-python'''
   if p==0: return n
   if p>0:  
       ln=len(str(n))  
       p=p-ln+1 if n<0 else p-ln
   return (n + 5 * 10**(-p-1)) // 10**-p * 10**-p

def nicefloat(x):
  """ Used with lon/lat ranges and dimensions
      converts eg 0.09999999999787 to 0.1 """
  return float('%12.6f' % x)

def is_int(x):
  import numpy as np
  return isinstance(x,np.integer) or isinstance(x,int)

def to_precision(x, p):
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """
    import math

    x = float(x)

    if x == 0.0:
        return "0." + "0" * (p - 1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x / tens)

    if n < math.pow(10, p - 1):
        e = e - 1
        tens = math.pow(10, e - p + 1)
        n = math.floor(x / tens)

    if abs((n + 1.0) * tens - x) <= abs(n * tens - x):
        n = n + 1

    if n >= math.pow(10, p):
        n = n / 10.0
        e = e + 1

    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p - 1):
        out.append(m)
    elif e >= 0:
        out.append(m[: e + 1])
        if e + 1 < len(m):
            out.append(".")
            out.extend(m[e + 1 :])
    else:
        out.append("0.")
        out.extend(["0"] * -(e + 1))
        out.append(m)

    return "".join(out)

if __name__ == '__main__':
  tgt=5555555
  d=2
  print('\t{} rounded to {} places:\n\t{} right to left \n\t{} left to right'.format( tgt,d,intround(tgt,-d), intround(tgt,d))) 

  tgt=-5555555
  d=2
  print('\t{} rounded to {} places:\n\t{} right to left \n\t{} left to right'.format( tgt,d,intround(tgt,-d), intround(tgt,d))) 

  mytest = 130.99999999999994
  print( nint(100*mytest) )
  print( intround(int(100*mytest),3) )
  print( nicefloat(mytest) )
  print( nicefloat(-mytest) )
  print( to_precision(-mytest,12) )
  print('IS INT? 1.0, 1', is_int(1.0) , is_int(1) )
