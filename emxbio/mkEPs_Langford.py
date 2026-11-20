#!/usr/bin/env python
import numpy as np

"""
Langford - 2017, BGS - oaks
  had 82-85 for robur, 78 for pube, using G93.


xxx NOT SURE WHAT THIS is about:_
 1. Forests
 2. Auchencorth 2023 paper
 uses Keenan for D, Qrobur = 290, Q.petraea 
 Note Alice Holt = 90% Q. robur
      Castelporziana = 27% BF oak
"""
k09 = dict(Qrobur=  [  290,  70,  0,  0.3 ],
           Qpetraea=[  290,  45,  0,  0.3] 
          )

s12 = dict(Qrobur=  [  320,  80,  0.2,  0.2 ],
           Qpubescens =  [  320,  80,  0.2,  0.0 ],
           Qpetraea=[  320,  45,  0.5,  0.0] ,
           Qilex   =[  500,  0.1,  30,  0.0] ,
           Qsuber  =[  500,  0.2,  20,  0.0] 
          )

for key, kv in k09.items():
  sv = s12[key]
  print(f'{key:<10s} {kv[1]:.1f} {kv[0]*kv[1]:12.3f} {sv[1]:.1f} {sv[0]*sv[1]:12.3f} ' )


print('SNL:')
icrf=1/0.59
snl=dict(max=3071,optmax=2140,site=769,opt=1035)
for key, val in snl.items():
  print(f"{key:<6s} {icrf*snl[key]:10.1f}")

""" Eqn 3 from Langford et al., 2023 """

def newCL(L):
 #return -1.9e-7 * L**2 + 1.2e-3*L
 return 9.49e-7 * L**2 + 5.1e-5*L

par = [ n*500 for n in range(6) ]
for L in par:
  print(f"{L:4d}  {newCL(L):8.2f}" )


