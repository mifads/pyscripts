#!/usr/bin/env python3
# Originally /home/davids/Work/EMEP_Projects/EMEP4XX/EMEP4UK/UMAN_WRF/UmanZcoords.py
import netCDF4
import numpy as np
from math import exp, log
import sys

PS=101325.0 # Pa

def StandardAtmos_kPa_2_km(p_kPa,dbg=False):
  """ converts pressure (Pa) to height (m) for standard atmosphere
     t = 288.15/(p/101325.0)**(-1.0/5.255876)
     - use the power function replacament, m**n == exp(n*log m)
    h_km = (288.15-t)/6.5
    From EMEP  StandardAtmos_kPa_2_km
  """
  if p_kPa > 22.623:
    t = 288.15/exp(-1.0/5.255876*log(p_kPa/101.325))
    h_km = (288.15-t)/6.5
    #if dbg: print(( 'SIGMA %9.4f %9.4f %7.1f %7.1f\n' % ( sigma, p_kPa, t, h ) ))
  else:
   h_km = 11.0 + log( p_kPa/22.632)/(-0.1576884)
  return h_km

def wiki(p,t,dbg=False):
   """ From wikipedia, can re-arrange to get:
    h-h0 = Tb*( (p0/p)**(1/eps) -1 )
    where eps = g0*M/Rgas*Lb
 FAILS
   """
   Pb = 101325.0  # Pa
   Tb = 288.0     # K
   Lb = -0.0065   # K/m
   Rgas = 8.3144598   # J/(mol.K)
   g0   = 9.80665     # m/s2
   M    = 0.0289644   # kg/mol for air
   eps = g0*M/(Rgas*Lb)
   h0=0.0
   h = h0 +  Tb *( (Pb/p)**(-eps) -1 )
   if dbg: print('EPS ', eps, 1/eps, h)   # -5.256, -0.190266
   return h # eps

def Jacobsen_hPa_2_km(p,t,dbg=False):  
  """ Jacobsen eqn 2.38,  p in hPa, t in K
      (book says km, but should be m)
  """
  Gamma_s = +0.0065  # -deg/m  (NOT deg/km as in book)
  Rgd = 287.04       # m2/s2/K   gas constant for dry air
  ps = 1013.25       # hPa
  g = 9.81           # m/s
  eps = Gamma_s*Rgd/g   # Just curious
  z = t/Gamma_s * (1- (p/ps)**(Gamma_s*Rgd/g) )
  if dbg: print('JAC p(hPa):%10.3f T: %7.1f eps: %9.4f z:%7.2f'%(p,  t,  eps, z_km))
  return 0.001*z
  #print('JAC p(hPa):%8.3f ',p, ' T:', t,  ' eps:', eps, 'z_km:', z_km)

def hypso(p,t):
  """ hypsometric eqn from https://keisan.casio.com/exec/system/1224585971#! 
   Note defaults are 1013.25 hPa and 288 K for standard conditions
   and lapse rate is -0.0065  K/m
  """
  
  p0 = 1013.25  # hPa
  h = ((p0/p)**(1/5.257) - 1 ) * t / 0.0065   # t in K
  return h

def hybridAB_2_p(A,B,ps=PS):
  return A+B*ps # p

def sigma2m(sigma,ptop):
  """
   calculates height from sigma and assuming standard atmosphere
      sigma = (p-Ptop)/(Ps-Ptop)
  """

  Ps = 1.01325e5 # Pa
  p  = sigma*(Ps-Ptop) + Ptop
  h = Pa2m(p)
  return h

def sigma2AB(sigma_k,Pt):
  """ Converts from sigma to EMEP's A, B coordinates. Uses pressure at top
      of domain, Pt. Then:
        Pk = Ak + Bk.Ps
        sigma_k = (Pk - Pt)/(Ps-Pt)
        Ak = (1-sigma_k) * Pt
        Bk = sigma_k
  """
  return  (1-sigma_k)*Pt,  sigma_k

#OLD
#OLDe=netCDF4.Dataset('wrfout_d01_2018_08_01_0200.nc')
#OLD
#OLDuman_znu= e.variables['ZNU'][0,:]
#OLDuman_znw= e.variables['ZNW'][0,:]
#OLDuman_ptop= e.variables['P_TOP'][0] # = 5000.f ; # Assume Ptop in Pa?
#OLD
#OLD# Assume UMAN data are sigma coords:
#OLDPs = 1.0e5
#OLDsfmt= '%3s %6s'   + ' %12s'*2   + '%12s %9s'
#OLDnfmt= '%3d %6.1f' + ' %12.4f'*2 + '%12.1f %9d'
#OLDline= '-'*60
#OLDfor coords in [ 'ZNU', 'ZNW' ]:
#OLD  print(line)
#OLD  print('Coordinates: ' + coords)
#OLD  print(sfmt % ( 'k', 'Pt', 'Ak', 'Bk', 'P', 'h'))
#OLD  print(line)
#OLD  if coords == 'ZNU': zn = uman_znu
#OLD  if coords == 'ZNW': zn = uman_znw
#OLD
#OLD  for k, sigma_w in enumerate( zn ): 
#OLD    Ak, Bk = sigma2AB(sigma_w,uman_ptop)
#OLD    P = Ak + Bk*Ps
#OLD    h = Pa2m(P)
#OLD    print(nfmt % (  k, uman_ptop, Ak, Bk, P, h ))
#OLD  print(line)
#OLD  #print '-'*60
#OLD 
#OLDsys.exit()
#OLD
#OLD
#OLD#EMEP 20 layer, Pa, top to bottom:
#OLDemep0 = np.array([
#OLD  10000.00,12261.37,16508.86,21502.51,27205.92,33604.39,40613.28,48079.07,
#OLD  55797.34,63530.60,71026.27,78034.55,84326.34,89711.18,94055.11,97298.68,
#OLD  98513.99,99474.72,100202.36,100726.39,101325.00 ])
#OLDemep = emep0[::-1]  # reversed
#OLD
#OLD#WRF, seems to be layer-centre (ZNU), and layer bounds (ZNW):
#OLD# From Chalmers HK work:
#OLDhk_Ptop = 5000.0  # ??? VGTOP?
#OLDhk_znu = np.array([  
#OLD  0.99895, 0.99675, 0.99435, 0.99175, 0.98895, 0.98595, 0.98255, 0.9785, 
#OLD    0.9737, 0.968, 0.9612, 0.95315, 0.94365, 0.9324, 0.91915, 0.90355, 
#OLD    0.8852, 0.8637, 0.8386, 0.8094, 0.7767, 0.7413, 0.7031, 0.66215, 0.6185, 
#OLD    0.5722, 0.52345, 0.4726, 0.42005, 0.36635, 0.31215, 0.2583, 0.20585, 
#OLD    0.15625, 0.11135, 0.07225, 0.03915, 0.01205 ])
#OLDhk_znw = np.array([
#OLD  1, 0.9979, 0.9956, 0.9931, 0.9904, 0.9875, 0.9844, 0.9807, 0.9763, 0.9711, 
#OLD    0.9649, 0.9575, 0.9488, 0.9385, 0.9263, 0.912, 0.8951, 0.8753, 0.8521, 
#OLD    0.8251, 0.7937, 0.7597, 0.7229, 0.6833, 0.641, 0.596, 0.5484, 0.4985, 
#OLD    0.4467, 0.3934, 0.3393, 0.285, 0.2316, 0.1801, 0.1324, 0.0903, 0.0542, 
#OLD    0.0241, 0 ])
#OLD
#OLD  
#OLD# sigma = p-ptop/(ps-ptop)
#OLDfor iz, sigma_w in enumerate( ZNW ):
#OLD  if iz == 20: break  # No emissions above this
#OLD  zu = -999.
#OLD  ze = -999.
#OLD  zemep = -999.
#OLD  zw = sigma2m(sigma_w)
#OLD  if iz < len(ZNU):
#OLD   sigma_u = ZNU[iz]
#OLD   zu = sigma2m(sigma_u)
#OLD  if iz < len(VGLVLS):  # emissions
#OLD   sigma_e = VGLVLS[iz]
#OLD   ze = sigma2m(sigma_u)
#OLD  if iz < len(emep):
#OLD   zemep = Pa2m( emep[iz] )
#OLD
#OLD  if iz==0:
#OLD
#OLD     fmt= '%3s' + ' %9s'*3 + ' %8s'*8 
#OLD     print(( fmt % ( 
#OLD       'iz', 'sig-WRFb','sig-WRFm', 'sig-Emis', 'z-WRFb','z-WRFm', 
#OLD       'z-Emis', 'z-emep', 'qt', 'ind', 'ene', 'marine' )))
#OLD
#OLD#  fmt= '%3d' + ' %9.4f'*3 + ' %8.1f'*8 
#OLD#  print( fmt % ( 
#OLD#       iz, sigma_w, sigma_u, sigma_e,  zw, zu,
#OLD#       ze, zemep,  uman_))
#OLD
#OLD#ie emissions match for 1st 20-ish then take big steps

if __name__ == '__main__':

 for t in range(273,303,5):
   for hPa in [1.0, 1.0e2, 850., 1.0e3, 1.01325e3]:
    kPa =hPa/10.0
    #FAILS print('W %7.1f P(hPa) %9.f Pa%12.3f'% (t,p*100,0.001*wiki(hPa,t)))
    print('J %7.1f P(hPa) %7.f Pa%12.3f'% (t,hPa,Jacobsen_hPa_2_km(hPa,t)))
    print('E %7.1f P(hPa) %7.f Pa%12.3f'% (t,hPa,StandardAtmos_kPa_2_km(kPa,dbg=False)))
    print('H %7.1f P(hPa) %7.f Pa%12.3f'% (t,hPa,0.001*hypso(hPa,t)))

