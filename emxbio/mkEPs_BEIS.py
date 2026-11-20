#!/usr/bin/env python3
import glob
import numpy as np
import os
import pandas as pd
import sys

args=sys.argv
print(args[1:])

df=pd.read_excel("Updated_BVOC_emissions_DATABASE_6-16.xlsx",sheet_name="Enclosure_Database")
#for k in df.keys(): print(k)

#reliability_codes = df.Reliability.unique() All nan!

def tostr(x,n=3):
  try:
    f = f"{x:.{n}f}"  # works for nan too, but returns "nan" even with .2 format
  except:
    f = str(x)
  if f=="nan": f="-"
  return f

omit_keys="Family Genus_species Common_Name Isoprene_Rate Total_Monoterpenes Total_Sesquiterpenes Isoprene_Not Monoterpene_Note Sesquiterpene_Note Reference_Code".split()

extras=dict(
  SLM="Specific_Leaf_Mass", SLMsrc="Estimated_Reported", SLMref="SLM_ref",
  D="Leaf_Biomass_Density", Dref="LBD_ref", typ="Study_type",
  setting="Study_Setting", field="Field_site", enc="Enclosure_system",
  intact="Plant_Intact", anal="Analytical_Technique",
  DynSt="Dynamic_or_Static", Env="Environmentally_controlled",
  N="N_samples", T="Temperature_C", PAR="PAR ", An="Photosynthesis_Rate",
  Phen="Plant_pheological_status", Gr="Growth_Conditions",
  Gs="Stomatal_Conductance ", RH="Humidity", Trans="Transpiration",
  nut="Nutrients")
# Reverse
extras = { v:k for k, v in extras.items() }  # e.g. extras["Specific_Leaf_Mass"] = "SLM"

#args="xx x Capparis indica".split()
for n, row in df.iterrows():

  genus=row.Genus_species
  if type(genus) != str: continue

  if all(x in genus for x in args[1:]): # match all substrings
    cname= tostr(row.Common_Name)
    Eiso = tostr(row.Isoprene_Rate)
    Emt  = tostr(row.Total_Monoterpenes)
    Esqt = tostr(row.Total_Sesquiterpenes)
    Inote = str(row.Isoprene_Note)
    Mnote = str(row.Monoterpene_Note)
    Snote = str(row.Sesquiterpene_Note)
    ref   = str(row.Reference_Code)
    print(f"{n:5d} {genus[:19]:<20s}"
          f" {tostr(row.Emit_Isoprene):4s} {Eiso:>8s}  {Inote:<12s}"
          f" {tostr(row.Emit_Monoterpene):4s} {Emt:>8s}  {Mnote[:6]:<12s}"
          f" {Esqt:<8s}", f" {ref:<8s}; {cname} ",end="")
    #if "median" in genus:
    for k, v in row.items():
      if k not in extras: continue
      vv=tostr(row[k],1)
      vv=vv.replace("Estimated", "E")
      if vv != "-": print(f"{extras[k]}={vv}; ",end="")
    print()

"""
    if n ==  577: sys.exit() # sheet row 578 Capparis indica      Y     337.824 %        -           - nan      -         Stein97b; SLM=100.0; SLMsrc=E; T=311.0
"""
