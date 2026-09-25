#!/usr/bin/env python3
import numpy as np

def getmax2d(array):
  """ gets 1st max value in 2-D array """
  j, i = np.unravel_index(a.argmax(),a.shape)
  return j,i
