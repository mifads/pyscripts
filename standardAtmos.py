#!/usr/bin/env python3
from math import log, exp
import numpy as np

def StandardAtmos_kPa_2_km(p_kPa):
 """
  Relations from Stull Meteorology for Scientists and Engineers
 """
 if p_kPa > 22.632:         # = 11 km height
    # t = 288.15/(p_kPa/101.325)**(-1.0/5.255876)
    #- use the power function replacament, m**n == exp(n*log m)

    t = 288.15/exp(-1.0/5.255876*log(p_kPa/101.325))
    h_km = (288.15-t)/6.5
 else:
    h_km = 11.0 + log( p_kPa/22.632)/(-0.1576884)
 return h_km

def dP_2_dZ(dP):  # thin layer approx
  rho = 1.225  # kg/m3 at sea-level
  g   = 9.81   # m/s/s
  dZ = dP/(g*rho)
  return dZ

if __name__ == '__main__':

  # test emep's lowest layers
  Ps = 1.0325e5  # Pa
  pEC = 7.367743 + 0.99401945*Ps
  p20 =  120.0   + 0.9880*Ps
  print('P(Pa) ', pEC, p20 )
  print('EC lowest ', 1000.0*StandardAtmos_kPa_2_km(0.001*pEC) )
  print('EM lowest ', 1000.0*StandardAtmos_kPa_2_km(0.001*p20) )
  print('EC lowest ', dP_2_dZ(Ps-pEC))
  print('EM lowest ', dP_2_dZ(Ps-p20))

  for p in [ 1013, 925, 850, 750, 500 ]: # hPa
    print(f'{p:4d} {StandardAtmos_kPa_2_km(0.1*p):.2f}')


#x=np.loadtxt('/home/davids/VERSION_CONTROL/svn/EMEP_Reports/Report2018/table.txt')
#k=x[:,0]
#a=x[:,1]
#b=x[:,2]
#p=x[:,3] * 0.001  # kPa
#
#for n in range(21):
#  print("%3d & %12.5f & %12.5f & %7.2f & %8.1f \\\\" % ( 
#     int(k[n]), a[n], b[n], 
#     10*p[n],    # as hPa
#     1000*StandardAtmos_kPa_2_km(p[n] ) )) # as m

