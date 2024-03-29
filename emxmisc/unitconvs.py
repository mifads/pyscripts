#!/usr/bin/env python3

#AVOG = 6.023e23
MVOL = 22.41e-3  # m3 @ 273.15 and 101.325 kPa

def ppb2ugm3(x,mw,P=1013.25,T=273.15):
  """
    returns ug/m3 for given mixing ratio (ppb) and mw (g)
    default pressure in hPa, temp in K
  """
  #! 1 mole has  volume (m3):
  vol = MVOL * T/273.15 * 1013.25/P

# i.e. for one mole we have 
# mass concentration = w/vol g/m3 or 10^6 . w/vol ug/m3
# If we have 1 ppb, we have 10^-09 * 10^6 * w/vol ug/m3

  ugm3 = 0.001  * x * mw/vol     #! g/m3 * 1.0e6 -> ug * 
  return ugm3

def ugm32ppb(ug,mw,P=1013.25,T=273.15):
  """
    returns ug/m3 for given mixing ratio (ppb) and mw (g)
    default pressure in hPa, temp in K
  """
  #! 1 mole has  volume (m3):
  vol = MVOL * T/273.15 * 1013.25/P
  ppb = 1.0e3 * ug * vol/mw
  return ppb

if __name__ == '__main__':

  x= 1.0
  print( 'Scalar 1 ppb O3 STP = ', ppb2ugm3(x,48.0) )
  print( 'Scalar 1 ppb O3 20 dev = ', ppb2ugm3(x,48.0,T=293.15) )
  print( 'Scalar 1 ppb O3 25 dev = ', ppb2ugm3(x,48.0,T=298.15) )
  c=12.0; h=1.0
  print( 'Scalar 1 ppb C2H2 20 dev = ', ppb2ugm3(x,2*c+2.0,T=293.15) )
  print( 'Scalar 1  ug C2H2 20 dev = ', ugm32ppb(x,2*c+2.0,T=293.15) )
