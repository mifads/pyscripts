#!/usr/bin/env python3
from math import exp, log
"""
Hellen 2020, Pallas
"""

def esqt_fT(T):  # fig 4a
  return 2.48 * exp(0.05*T)
def emt_fT(T):  # fig 4b
  return 0.27 * exp(0.08*T)
def eiso_fT(T):  # fig 4c
  return 0.31 * exp(0.18*T)
def eiso_fG(f):  # fig 4d, vs CL*CT
  return 88.24 * f + 5.1

print(f"fCL*CT {eiso_fG(1.0):.3f}") # matches text also
for t in [ 0, 15, 30, 35 ]:
  fsqt  = esqt_fT(t) 
  fmt   = emt_fT(t) 
  fiso  = eiso_fT(t) 
  print( f" {t:5.1f}  {fiso:7.3f} {fmt:7.3f} {fsqt:7.3f} {fsqt/fmt:7.3f}")

""" =>
  15.0    4.613   0.896   5.250   5.857
  30.0   68.636   2.976  11.115   3.734
  35.0  168.817   4.440  14.271   3.214
"""
