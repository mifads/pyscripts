#!/usr/bin/env python3
"""
 1. cams3p1_table:
 The PM_split files have A,B,C,D,E,F1,F2,F3,F4,G,H,I,J,K,L,
 NB if we split A and F, set zero emissions for those sectors

 2. tnoRefSources
 A conventient list of what's included in TNO's Ref1 and Ref2
"""

cams3p1_table = """# Nov 2019
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

def getCams2emep(table=cams3p1_table,dbg=False):
  cams2emepcode = dict()
  cams2snapcode = dict()
  cams2name     = dict()
  for line in table.splitlines():
    if line.startswith('#'): continue
    a, b, c, d = line.split()
    cams2emepcode[ b ] = int(a)
    cams2snapcode[ b ] = int(c)
    cams2name[ b ] = d
    if dbg: print( '\t'.join( [ b,  a, c ] ) )
  return cams2emepcode, cams2name

def camstab(table=cams3p1_table,dbg=False):
  cams=dict()
  cams['emepsec'] = []
  cams['name']    = []
  cams['tnosec']  = []
  cams['snap']  = []
  for line in table.splitlines():
    if line.startswith('#'): continue
    a, b, c, d = line.split()
    cams['emepsec'].append(int(a))
    cams['tnosec'].append( b)
    cams['snap'].append( c)
    cams['name'].append(d)
  return cams

def tnoAPmapping():
  """ not used so far, but a conventient list of what's included
      in TNO's Ref1 and Ref2 """
  tnoAP= ['A:A', 'A:P', 'B:A', 'B:P', 'C:A', 'D:A', 'D:P', 'E:A', 'F1:A',
       'F2:A', 'F3:A', 'F4:A', 'G:A', 'H:A', 'H:P', 'I:A', 'J:A', 'J:P',
       'K:A', 'L:A', 'L:P']
  # 2020 - uses A1, A2 or A, F1... or F. No use of :P for H or J
  tno19= ['A1', 'A2', 'B', 'B', 'C', 'D', 'D', 'E', 'F1',
       'F2', 'F3', 'F4', 'G', 'H', 'H', 'I', 'J', 'J',
       'K', 'L', 'L']
  return dict(zip(tnoAP, tno19))

if __name__ == '__main__':

  mapping, names =  getCams2emep(cams3p1_table,dbg=True)
  print('SHIPPING? ', mapping['G'], names['G'] )
  tnoAP_to_19 = tnoAPmapping()
  ap= tnoAP_to_19['A:P'] # Returns A2
  print('A:P? ', ap, mapping[ap], names[ap] )

  ctab = camstab()
