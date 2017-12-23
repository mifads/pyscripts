#!/usr/bin/env python3
# Equation from Hollaway, but with C in ppb, not ppm as suggested
from numpy import *
from pylab import *

O3=arange(0.0,80.0,2.0)
W126=zeros(len(O3))


for i in range(0,len(O3)):
  C=O3[i] #/1000.0   # ppm
  W126[i] = C/( 1+4403*exp(-0.126*C) )

plot(O3,W126)
show()
