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
