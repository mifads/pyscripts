#!/usr/bin/env python3
from math import exp
import matplotlib.pyplot as plt
import numpy as np
import emxbio.convEPs as ep
import emxbio.mkGuentherCT as guenther
import sys

# Hyltemosssa
lai=4.77
sla = 38.4       # cm2/g
slw = 1.0e4/sla  # Now g/m2  260
D = lai * slw    # should be ca. 1240

# Use 30C values from scatter plots (2025_ICOSconf, Holst)
def isop(t):
  nm = 0.025 * exp(0.164*t)
  return  nm * ep.nmolem2s_to_uggh(nm,D,68.0) # Assume m2 is m2 ground!

def isopLA(t):
  nm = 0.025 * exp(0.164*t)
  return  nm * ep.nmolem2LAs_to_uggh(nm,slw,68.0)

def terp(t):
  nm = 0.0621 * exp(0.1639*t)
  print('mt (nmol/m2/s)', nm)
  return  nm * ep.nmolem2s_to_uggh(nm,D,136.0)

temps = np.linspace(10,35,30)
tK = temps + 273.15
Is   = np.array([ isop(t) for t in temps])
Is30 = isop(30.0)
Is30la = isopLA(30.0)
print('Holst Is(30) = ', Is30 )
print('Holst Is(30)a = ', Is30la )
mt30 = terp(30.0)
print('Holst MT(30) = ', mt30 )
sys.exit()

#mtIs   = np.array([ mtIso(t) for t in temps])
#mtIs = np.where(mtIs<3.0,mtIs,np.nan)
#mtIso30 = mtIso(30.0)

Is95 = np.array([ guenther.G9x_Ct(t) for t in tK])
Is95std = guenther.G9x_Ct(30.0+273.15)
IsSeco = np.array([ guenther.secoG99(t) for t in tK])
sec30 = guenther.secoG99(303.15)
IsPCEEA = np.array([ guenther.Ct_PCEEA06(t,t-10) for t in tK])
pc30 = guenther.Ct_PCEEA06(303,303)
plt.plot(temps,Is/Is30,label='Holst Is')
#plt.plot(temps,mtIs/mtIso30,label=' mtIs')
plt.plot(temps,Is95/Is95std,label='Emep Is')
plt.plot(temps,IsSeco/sec30,label='Seco Is')
plt.plot(temps,IsPCEEA/pc30,label='PCEEA Is')
plt.legend()
plt.show()

print(f"SWL:{slw:.2f}  D:{D:.2f}  Is: {isop(30.0):.2f} Imt: {terp(30.0):.2f}" )

