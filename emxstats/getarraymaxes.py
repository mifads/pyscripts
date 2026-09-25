#!/usr/bin/env python3
import numpy as np


def getmax1d(a):
  """ gets 1st max value in 2-D array """
  return a.argmax()

def getmax2d(a):
  """ gets 1st max value in 2-D array """
  j, i = np.unravel_index(a.argmax(),a.shape)
  return j,i

if __name__ == '__main__':
  a= np.array( [1.0, 3.0, 2.5, 6.0, 1.0 ])
  i = getmax1d(a)
  print( i, a[i] )
