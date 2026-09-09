#!/usr/bin/env python3
import pandas as pd

wanted="Pinus"
mts="APIN BPIN D3CAR DLIM CAMPH MYRC ATERP BPHE SABI PCYM OCIM ATHU TRPO GTERP".split()
ifile="/home/davids/Work/EU_Projects/CAMAERA/BVOC_Update/Jesse/beld6_efac_with_ag_yn.csv"
df = pd.read_csv(ifile,comment="#",sep=",")
# LC, var, unit, EF
vegs=ds.LC.unique()

for veg in vegs:

  if veg.startswith(wanted):
    lai = float( df[(df['LC']==veg) & (df['var']=='LAI')]['EF'].values[0] )
    isop = float( df[(df['LC']==veg) & (df['var']=='ISOP')]['EF'].values[0] )
    sqt  = float( df[(df['LC']==veg) & (df['var']=='SESQT')]['EF'].values[0] )
    summt = 0.0
    for mt in mts:
       summt += float( df[(df['LC']==veg) & (df['var']==mt)]['EF'].values[0] )
    print(f"{veg:<20s} {lai:.2f} {isop:8.4f}  {summt:8.4f} {sqt:8.4f}")

"""
LAI WFAC ISOP SESQT NO
MBO
APIN BPIN D3CAR DLIM CAMPH MYRC ATERP BPHE SABI PCYM OCIM ATHU TRPO GTERP
METH ETHE PROPE ETHO ACET HEXA HEXE HEXY FORM ACTAL BUTE ETHA FORAC ACTAC BUTO
ORVOC
CO
AG_YN
"""
