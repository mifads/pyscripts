#!/usr/bin/env python3
from math import exp, log
"""
Hakola 1998
nb Young trees, 1-1.5m high
Some oddities: temp response v. high, cf use of 0.09 below
 text says emt = 3.7@29C, but eqns give 3.2
 3.7 consistent with tab1, but above reg line
"""

def eiso_fTaspen(T):
  beta=0.2395; alpha=3.6558
  return 0.001*exp(beta*T+alpha)    # ng->ug

def emt_fTaspen(T):
  beta=0.3606; alpha= -2.3794
  return 0.001*exp(beta*T+alpha)    # ng->ug

Is30 = eiso_fTaspen(30.0)
mt30 = emt_fTaspen(30.0)

for t in [ 15.0, 29, 30.0 ]:
  hiso = eiso_fTaspen(t) 
  giso = Is30 * exp(-0.09*(30-t))
  hmt  = emt_fTaspen(t) 
  gmt  = mt30 * exp(-0.09*(30-t))
  print( f"Is {t:5.1f}  {hiso:7.3f} {giso:7.3f}  MT:  {hmt:7.3f} {gmt:7.3f}")

