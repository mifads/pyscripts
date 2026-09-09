#!/usr/bin/env python3
from math import exp


def Ct_PCEEA06(T,Tdaily):
  """ The PCEEA algirithm uses Tdaily /air temp for 1week to 1 month
   here we use T240 anyway
  """
  CT1=80.0   # isoprene
  CT2=200.0
  Topt = 313 + 0.6*(Tdaily-297)       # G06 - 9
  Eopt = 1.75*exp(0.08*(Tdaily-297))
  x=( (1/Topt)-(1/T) ) / 0.00831
  gT = Eopt * ( CT2*exp(CT1*x) / (CT2-CT1*(1-exp(CT2*x))) )
  return gT

def Ct(T,T24,T240):
  CT1=95.0   # isoprene
  Ceo = 2    # isoprene
  CT2=230.0
  Topt = 313 + 0.6*(T240-297)       # G06 - 9
  Eopt = 2.034*exp(0.05*(T24-297)) * exp(0.05*(T240-297))
  x=( (1/Topt)-(1/T) ) / 0.00831
  gT = Eopt * ( CT2*exp(CT1*x) / (CT2-CT1*(1-exp(CT2*x))) )
  return gT

def secoG99(T):
  """ citing 1999 EXPRESSO paper """
  R=0.008314 # kJ/K/mol
  CT1=95.0
  CT2=230.0
  Topt = 312.5
  Eopt = 1.9
  x=( (1/Topt)-(1/T) ) / R
  return Eopt * ( CT2*exp(CT1*x) / (CT2-CT1*(1-exp(CT2*x))) )

def OldCt(itk):
    """ from emep code,G93/95? """
    agts = 303.
    agr = 8.314
    agtm = 314.         # G93/G95
    agct1 = 95000.      # G93/G95
    agct2 = 230000.     # G93/G95
    agct = exp(agct1*(itk - agts)/(agr*agts*itk)) / (1. + exp(agct2*(itk - agtm)/(agr*agts*itk)))
    return agct


for tC in [ 0, 10, 20, 30 ]:
  tK = tC + 273.15
  T24  =  tK - 0.0
  T240 =  tK - 0.0
  print(f"{tC:2d}  {Ct(tK,T24,T240):10.3f} {secoG99(tK):10.2f}  {OldCt(tK):10.2f}")
