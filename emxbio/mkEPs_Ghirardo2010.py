#!/usr/bin/env python3
""" GhirardoMTemis2010 
  2yr old seedlings, (5 yrs for Q.ilex), 30C, full sunlight in day
"""
import emxbio.convEPs as ep

IsopFracs = dict(Larix=12,Picea=23,Pinus=13.9)
# nmol/m2(leaf)/s approx, from Fig.
mtEmis    = dict(Larix=2.3,Picea=1.0,Pinus=0.6,Betula=0.25,Quercus=12)
isoEmis   = dict(Larix=0.45,Picea=0.28,Pinus=0.05,Betula=0.7,Quercus=0.45)
slw       = dict(Larix=150, Picea=150, Pinus=150, Betula=100,Quercus=100)

print("VERY CRUDE; eyeballed")
for k, v in mtEmis.items():

  mt  = ep.nmolem2LAs_to_uggh(v,slw[k],136)
  iso = ep.nmolem2LAs_to_uggh(isoEmis[k],slw[k],68)
  rat=100*iso/mt
  f="-"
  if k in IsopFracs:
    f = IsopFracs[k] * 0.5  # from nmole to mass
  print(f"{k:<8s} {v:7.2f} {mt:7.2f} {iso:7.2f} {rat:5.1f}   {f}")



