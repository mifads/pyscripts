#!/usr/bin/env python3
"""

Rantala 2014 had Is=80 ng/m2/s, Imt = 380 ng/m2/s (fsynth=0.66) for Hyytiala
from PTRM using their "best" method (SLP=surface layer profile).(Also
compared with disjunct eddy-covariance.
Data from Fig.11 SLP

Rantala 2015 had ca. 100 ng/m2/s @ 20C (Fig 2)

ASSUME rates are per m2 ground, not leaf
"""
D=150  # g/m2 query
D=540  # Hakola 2006, cited by Rantala 2015
ngm2s =  1.0e-3*3600/D   #  ug/g/h

print("Rantala rates:")
print(f"R2014 Is             = {80*ngm2s:.2f} Imt={380*ngm2s:.2f} ug/g/h")

# Use pool algorithm for MT:
print("Rantala 2015 pool rates:")
print(f"R2015 Is+MBO-May/Apr = {36*ngm2s:.2f} Imt={145*ngm2s:.2f} ug/g/h")
print(f"R2015 Is+MBO-Jul     = {63*ngm2s:.2f} Imt={210*ngm2s:.2f} ug/g/h")
# Emt = Esynth + Epool = E0,hybrid [ fsynth CT*CL + (1-fsynth)*Gamma]
# where Gamma = exp(beta*(T-303.15))
#
print("Rantala 2015 hybrid rates:")
print(f"R2015 Apr      fsynth = 0.63          Imt={280*ngm2s:.2f} ug/g/h")
print(f"R2015 Jul               0.36          Imt={250*ngm2s:.2f} ug/g/h")
print(f"R2015 Oct               0.79          Imt={400*ngm2s:.2f} ug/g/h")

mtl=0.0; mtp=0.0; mmf =0.0
f=0.63; e=280*ngm2s; mmf += f
mtl += (f*e); mtp += ((1-f)*e)
print(f"R2015 Apr  {f}   {f*e:.2f}  {(1-f)*e:.2f}  {e:.2f} ug/g/h")
f=0.70; e=390*ngm2s; mmf += f
mtl += (f*e); mtp += ((1-f)*e)
print(f"R2015 May  {f:.2f}   {f*e:.2f}  {(1-f)*e:.2f}  {e:.2f} ug/g/h")
f=0.55; e=320*ngm2s; mmf += f
mtl += (f*e); mtp += ((1-f)*e)
print(f"R2015 Jun  {f}   {f*e:.2f}  {(1-f)*e:.2f}  {e:.2f} ug/g/h")
f=0.36; e=250*ngm2s; mmf += f
mtl += (f*e); mtp += ((1-f)*e)
print(f"R2015 Jul  {f}   {f*e:.2f}  {(1-f)*e:.2f}  {e:.2f} ug/g/h")
f=0.39; e=220*ngm2s; mmf += f
mtl += (f*e); mtp += ((1-f)*e)
print(f"R2015 Aug  {f}   {f*e:.2f}  {(1-f)*e:.2f}  {e:.2f} ug/g/h")
f=0.63; e=290*ngm2s; mmf += f
mtl += (f*e); mtp += ((1-f)*e)
print(f"R2015 Sep  {f}   {f*e:.2f}  {(1-f)*e:.2f}  {e:.2f} ug/g/h")
f=0.79; e=400*ngm2s; mmf += f
mtl += (f*e); mtp += ((1-f)*e)
print(f"R2015 Oct  {f}   {f*e:.2f}  {(1-f)*e:.2f}  {e:.2f} ug/g/h")

print(f"R2015 Avg  {mmf/7.0:.2f}   {mtl/7.0:.2f}  {mtp/7.0:.2f}  {(mtl+mtp)/7.0:.2f} ug/g/h")
