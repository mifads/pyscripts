#!/usr/bin/env python3
""" converts 11-sector snap to nearest GNFR_CAMS. Skips 
    snap4 and just uses 3 instead. Matching based upon:
# emep  cams_code  snap  cams_long
  1        A          1  A_PublicPower
  2        B          3  B_Industry
  3        C          2  C_OtherStationaryComb
  4        D          5  D_Fugitive
  5        E          6  E_Solvents
  6        F          7  F_RoadTransport
  7        G          8  G_Shipping
  8        H          8  H_Aviation
  9        I          8  I_Offroad
  10       J          9  J_Waste
  11       K         10  K_AgriLivestock
  12       L         10  L_AgriOther
  13       M          3  M_Other
  14      A1          1  A1_PublicPower_Point
  15      A2          1  A2_PublicPower_Area
  16      F1          7  F1_RoadTransportExhaustGasoline
  17      F2          7  F2_RoadTransportExhaustDiesel
  18      F3          7  F3_RoadTransportExhaustLPGgas
  19      F4          7  F4_RoadTransportNonExhaust
 """
import os
import sys

if len(sys.argv) < 2 or sys.argv[1] == '-h':
  sys.exit('\n\nUsage: snap2gnfrSplit emissplit_xxxx_yyy.csv\n\n - will output emissplit_gnfr_xxxx_yyy.csv')
ifile=sys.argv[1]
assert os.path.isfile(ifile),'Error missing file:%s'%ifile
ofile= ifile.replace('split','split_gnfr')
assert not os.path.isfile(ofile),'Error file exists :%s'%ofile

out=open(ofile,'w')

snap2g = { 1:[1,14,15], 2:[3], 3:[2], 4:[999], 5:[4], 6:[5], 
           7:[6,16,17,18,19], 8:[7,8,9], 9:[10],
           10:[11,12], 11:[13],
         }

#lines= open(ifile,'r').readlines()

with open(ifile,'r') as f:
  start = True
  for row in f:
    if start:
      print(row,end='')
      out.write(row)
      if row.startswith('#DATA'): start=False
      continue
    fields= row.split(',')
    snap=int(fields[1])
    if snap == 4: continue
    for gnfr in snap2g[snap]:
      fields[1] = str(gnfr)
      newrow = ','.join(fields)
      print(newrow.strip())
      out.write(newrow)
