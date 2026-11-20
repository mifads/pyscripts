#!/usr/bin/env python3
# from Ormeno 2007 SW paper
import numpy as np

# 
def Emt_Phale(sw):
   return np.exp(2.10+5.20/sw)
def Emt_Qcocc(sw):
   return np.exp(2.28+5.54/sw)

# SQT had no regression


sw = [ -8, -6, -4, -2, -0.5 ]

for s in sw:
  print(f"{s:7.2f}  {Emt_Qcocc(s):8.2f} {Emt_Phale(s):8.2f}")
