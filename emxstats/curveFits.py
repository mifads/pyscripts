#!/usr/bin/env python3
from numpy import exp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import beta
import sys

def betaFit(sw,mode,a=2.5,norm=True):
  """ beta distribution testing. Let a=2, mode=(a-1)/(a+b-2), dvs b=(a-1-m)/m + 2
    m=(a-1)/(a+b-2)
    ma + mb - 2m = a-1
    mb = a-ma-1+2m = a(1-m) -1 + 2m
     b = [a(1-m)-1]/m + 2
  from 2024_SoilNO/scripts_PC/mkHuberFit.py
  """
  b=(a - a*mode -1)/mode + 2
  res =  beta.pdf(sw,a,b)
  #print('GB', res)
  if norm:
    res /= max(res)
  return a,b, res

if __name__ == '__main__':
  import matplotlib.pyplot as plt

  x=np.linspace(0,1.0,100,endpoint=True)
  for  mode  in [ 0.79, 0.85 ]:  # location of max
    for aa in [  6, 6.5, 7, 7.5 ]:
      a,b,res=betaFit(x,mode,a=aa,norm=True)
      plt.plot(x,res,label=f'beta b={aa}, mode={mode}')
  plt.legend()
  plt.show()



