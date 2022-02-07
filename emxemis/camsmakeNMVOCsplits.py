#!/usr/bin/env python3
# was 2021 camsmakeNMVOCsplits2.py
# but now makes use of Matrix L for Matrix K. (Was 100% unreactive before)
import collections  # old python!
import numpy as np
import os
import emxmisc.auto_dicts       as ad
import emxemis.camsSectorTables as cs
import emxemis.camsInfo as ci  # Dave's script to read CAMS.csv files.
import emxemis.cams_emep_codes as ce
import emxemis.normaliseEmisSplits as ne
import emxemis.write_emislist as we
import emxmisc.codetxt as codetxt
import pandas as pd
import sys

#print(codetxt.codetxt(__file__))
#print(__file__, os.path.dirname(os.path.realpath(__file__)) )
isoDBG='ALB'
isoDBG='KWT'
isoDBG='ARM'
isoDBG='FIN'

# Helpers
def sfmt(array):
  """ join-function for a list of numbers """
  return ';'.join(str(x) for x in array)

def mydictfromkeys(keys,val=0.0):
  """ eos python too old! need to use ordered dicts """
  mydict=collections.OrderedDict()
  for k in keys:
    mydict[k] = val
  return mydict

gnfrFrac=ad.Vividict()
snapFrac=ad.Vividict()

# 0 ) get country codes
cctab = ce.get_emepcodes() # cctab['ALB']['cc'] = '1', has 'EUR' also.
#print('CC ', cctab) # has EUR

# 1)  Get sector mapping:
# cams3p1_table = """# Nov 2019
# emep  cams_code snap  cams_long
#  1        A        1  A_PublicPower
#  2        B        3  B_Industry
#..

camstab  = cs.camstab() #  keys: emepsec (=1-19), name, tnosec,  snap
camssecs = camstab['tnosec']
tnoAP_to_19 = cs.tnoAPmapping()  #  e.g. tnoAP_to_19['A:P'] Returns A2
print('keys ', tnoAP_to_19.keys())  # A:A, A:P, ...
print('vals ', tnoAP_to_19.values()) # A1, A2 .
print('cams ', camssecs) # tab['tnosec']) # A B C .. A1 .F1..

#-----------------------------------------------------------------------------
# Get emissions (needed to produce weighted F)
#e = ad.Vividict()
#e['NMVOC']['NOR']['F1:A'] = 1.0
#e['NMVOC']['NOR']['F2:A'] = 1.0
# F1 etc ...
#efile='/home/davids/Work/D_Emis/TNO_Emis/CAMS71_REF2_v1_2015/CAMS71-II_scenarios_v1_REF2_2015.csv'
#efile='/home/davids/Work/D_Emis/TNO_Emis/TNO_Inputs/CAMS-REG-AP_v2.2.1_2015_REF2.csv'
efile='/home/davids/MDISKS/Nebula/MG/work/CAMS2_40/U5_emissions/CAMS-REG-v5_1_with_Ref2_0_1_year2018_DT.csv'
efile='/home/davids/Work/D_Emis/TNO_Emis/2022_CAMS2_40_U5_emissions/CAMS-REG-v5_1_with_Ref2_0_1_year2018_DT.csv'
emisfile="CAMS-REG-v5_1_with_Ref2_0_1_year2018_DT (CAMS2_40_U5)"
e=ci.readCams(efile , wanted_poll='NMVOC')   #dict_keys(['polls', 'iso3s', 'srcs', 'snap2', 'lons', 'lats', 'dx', 'dy', 'NMVOC'])
emNMVOC = dict()

for iso3 in e['NMVOC'].keys():    # iso3s has ALB..., plus EurTot 

  emNMVOC[iso3] = mydictfromkeys(camssecs,0.0) # Initialise

  for gnfrAP in e['NMVOC']['EurTot'].keys():
    if gnfrAP.startswith('Sum'): continue
    ap = tnoAP_to_19[gnfrAP] # Returns A2
    em = e['NMVOC'][iso3][gnfrAP]['sum']
    emNMVOC[iso3][ap] += em
    if iso3==isoDBG: print('emNMVOC:'+iso3,  gnfrAP, ap, em, emNMVOC[iso3][ap]) 
    emNMVOC[iso3]['A'] = emNMVOC[iso3]['A1'] + emNMVOC[iso3]['A2']
    emNMVOC[iso3]['F'] = emNMVOC[iso3]['F1'] + emNMVOC[iso3]['F2'] + \
                         emNMVOC[iso3]['F3'] + emNMVOC[iso3]['F4']

# 2) Get matrices which map v01 etc to EMEP
#CAMS name      CH3OH C2H5OH C2H6 NC4H10 C2H4 C3H6 BENZENE TOLUENE OXYL HCHO MEK CH3CHO GLYOX MGLYOX C5H8 APINENE UNREAC
#v01 alcohols  0.8774  0.046   0     0     0    0     0       0     0    0     0     0    0     0     0      0    0.0767
idir='/home/davids/Work/EMEP_Projects/emepgit/emepecosx/chem/utils/EmChem_conversion/EmisWork/'

vspecMap = ad.Vividict()  # will produce eg vspecMap['A']['v01']['CH3OH']. Misses A1,A2,F,M

for gnfrCode in camssecs: # A, B, C ... F4
  ifile=idir + 'EC19_Matrix.CAMS-REG-v3_1_2_Sector%s.csv' % gnfrCode
  if gnfrCode=='K': ifile=idir + 'EC19_Matrix.CAMS-REG-v3_1_2_Sector%s.csv' % 'L' # K was missing
  if os.path.isfile(ifile):
    m =pd.read_csv(ifile,sep='\s+')
    headers =  list(m.keys())
    emepSpecs= headers[2:]
    if gnfrCode=='A':
      emepUsed = emepSpecs.copy()
        #  will be converted to other
      emepUsed.remove('APINENE')
      emepUsed.remove('C5H8')
    print('GNFR NOW ', gnfrCode)

  # merge with vocMap[iso3][gnfr] = vals  # e.g. vocMap['UZB']['A'] = [.... ]
  # m.head(3):
  # CAMS      name  CH3OH  C2H5OH  C2H6  NC4H10  C2H4  C3H6  BENZENE  TOLUENE  \
  #0  v01  alcohols   0.95    0.05   0.0     0.0   0.0   0.0        0        0   
  #1  v02    ethane   0.00    0.00   1.0     0.0   0.0   0.0        0        0   
  #2  v03   propane   0.00    0.00   1.0     0.0   0.0   0.0        0        0  

    for nrow in range(len(m)): # m.iterrows():
      vspec = m['CAMS'][nrow]  # v01, ... v25
      vspecMap[gnfrCode][vspec] = mydictfromkeys(emepSpecs,0.0) # Initialise
      #if vspec=='v11':
      #print('GNFR VSPEC ', gnfrCode, vspec, type(vspec))
      for espec in emepSpecs:
        frac  = m[espec][nrow] # row[col]  #  CH3OH ...
        if gnfrCode == 'G' and vspec=='v01':
            print('GNFR  vspec frac ', gnfrCode, vspec, espec, frac)
        if espec == 'APINENE':
         # Crude fix to assign the trace (<1%) amounts of APINENE
         # to 50% C2H4 and UNREAC, and 100% C5H8 to c2h4:
         # This keeps the anthropogenic and biogenic SOA separate
         vspecMap[gnfrCode][vspec]['C2H4']    += (0.5*frac)
         vspecMap[gnfrCode][vspec]['UNREAC']  += (0.5*frac)
        elif espec == 'C5H8':
         vspecMap[gnfrCode][vspec]['C2H4']    += frac
        else:
         vspecMap[gnfrCode][vspec][espec] += frac 

# Collect totals in tfrac array:
tfrac = dict()
for gnfr in camssecs + [ 'F' , 'A1' , 'A2']:
  tfrac[gnfr] = mydictfromkeys(emepUsed,0.0)

# 3) Get CAMS splits and create emissplits
#Year;ISO3;GNFR_Category;v01;v02;v03;v04;v05;v06;v07;v08;v09;v12;v13;v14;v15;v16;v17;v18;v19;v20;v21; ..v25
#2016;ALB;A;0.2;0;0.01;0.07;0.045;0.085;0;0;0;0.01;0.01;0.025;0.01;0.015;0;0;0;0;0.15;0.05;0.05;0.2;0
# (note misses v10, v11
idir='/home/davids/Work/D_Emis/TNO_Emis/CAMS50_20191031/VOC_splits/'
idir='/home/davids/Work/D_Emis/TNO_Emis/2022_CAMS2_40_U5_emissions/'
ifile='NMVOC_split_for_CAMS-REG-v3_1_2emep.csv'
ifile='NMVOC_split_for_CAMS-REG-v5_1.csv'
splitfile="NMVOC_split_for_CAMS-REG-v5_1.csv"

# camsSplit.head(3):
#   Year ISO3 GNFR_Category       v01       v02       v03       v04       v05  \
#0  2016  ALB             A  0.200000  0.000000  0.010000  0.070000  0.045000   
#1  2016  ALB             B  0.194052  0.033605  0.102604  0.108938  0.131137

camsSplit =pd.read_csv(idir+ifile,delimiter=';')
camsHeaders = camsSplit.keys()  # Year, ISO3, GNFR_, v01...
camsCountries= camsSplit['ISO3'].unique()
print('CAMS CC', camsCountries)

#g=camsSplit['GNFR_Category']; sorted(g.unique()) =>
# ['A', 'B', 'C', 'D', 'E', 'F1', 'F2', 'F3', 'F4', 'G', 'H', 'I', 'J', 'L']
#   1    2    3    4    5    16    17    18    19    7   8     8   10   12
# misses 6=traffic, 14-15 = A1,2

npolls = len(emepUsed)

for iso3 in camsCountries:
  for gnfrCode in camssecs: # tab['tnosec']: # A B C .. A1 .F1..
    gnfrFrac[iso3][gnfrCode] = np.zeros(npolls)
    if iso3==isoDBG: print('INIT ', iso3, gnfrCode)

for n in range(len(camsSplit)): # rows, A..F1..F4..L

  sumv = 0.0
  sume = 0.0
  efrac = mydictfromkeys(emepUsed,0.0) # Initialise

  for vspec in camsHeaders:
    val = camsSplit[vspec][n]
    if   vspec=='Year'         : continue
    elif vspec=='ISO3'         : iso3= val
    elif vspec=='GNFR_Category':
      gnfrCode = val
    else: # Continuev
      sumv += val
      for espec in emepUsed:
        #print('n vspec val sumv espec', n, vspec, val, sumv, espec)
        vMap = vspecMap[gnfrCode][vspec][espec] 
        nmvoc = emNMVOC[iso3][gnfrCode]
        #print('VMAP ', vMap, type(vMap), np.isscalar(vMap), np.isreal(vMap) )
        if np.isscalar(vMap):  # Weird!!! np.isreal still True for vMap={}!
         if vMap > 0:
          efracTmp      = val * vMap * nmvoc
          efrac[espec] += efracTmp
          tfrac[gnfrCode][espec] += efracTmp
          sume         += efracTmp
          if iso3==isoDBG:
               print('ESPEC %s %s %-12s %s %s'% \
                 ( iso3, gnfrCode, espec, vspec, 
                     sfmt([nmvoc, vMap,  efracTmp, efrac[espec], sumv, sume, tfrac[gnfrCode][espec] ]) ))
          if gnfrCode=='G': print('GVALS-TS ', gnfrCode, iso3, tfrac[gnfrCode] )

  evals = np.array( list(efrac.values()) )
  if np.sum(evals) < 1.0e-3:
    print('EVALS ZERO ', iso3, gnfrCode, np.sum(evals))
    continue
  print('EVALS HERE ', iso3, gnfrCode, evals)

  if gnfrCode.startswith('F'):
    tmpvals= ne.normedVals(evals,txt='F:'+gnfrCode, dbg=False)
    print('FCALCS START ', gnfrCode, sfmt(tmpvals))
    if gnfrCode == 'F1':
      fvals = evals.copy() # new array for F, write out later
    else:
      fvals = np.vstack((fvals,evals))
    if gnfrCode == 'F4':
      if np.sum(fvals) > 0.0:
        fvals= ne.normedVals(fvals,txt='FCALC:'+gnfrCode, dbg=True)
        # For EurTot, we need to put back emissions:
        for n, espec in enumerate(emepUsed):
          tfrac['F'][espec] += (fvals[n]*nmvoc)

      print('FCALC END: ', gnfrCode, np.shape(fvals), tfrac['F'][espec] ) #, fvals )

  if iso3==isoDBG:
      print('EEVALS ', iso3, gnfrCode, np.shape(evals),
        evals, np.sum(evals) )
  #if gnfrCode == 'K': Kvals[iso3] = evals # Don't normalise
  #if gnfrCode == 'L': Lvals[iso3] = evals
  if np.sum(evals) < 1.0e-3: continue 
  nvals= ne.normedVals(evals,txt='NNN'+gnfrCode, dbg=True)
  assert abs(np.sum(nvals)-1.0)<1.0e-3, 'SUMV error %f'% np.sum(nvals)
  nvals *= 100.0

  gnfrFrac[iso3][gnfrCode] = nvals
  if iso3==isoDBG:
     #print('FRACSET ', iso3, gnfrCode, sfmt(nvals))
     print('FRACSET ', iso3, gnfrCode, *nvals,sep=';') #test *

  if gnfrCode == 'A':
    for sec in 'A1 A2'.split():
      gnfrFrac[iso3][sec] = nvals
  elif gnfrCode == 'F4' and np.sum(fvals) > 0.0:
    fvals *= 100.0
    gnfrFrac[iso3]['F'] = fvals

#sys.exit()

# Totals?
#print('FVALS-X ', gnfrCode, tfrac['F'] )
tfrac['A1'] =  tfrac['A'].copy()
tfrac['A2'] =  tfrac['A'].copy()
for gnfr in 'M': # 'K' .split(): # No NMVOC here
   print('CHECK KM ', gnfr,  tfrac[gnfr] )
   tfrac[gnfr] = mydictfromkeys(emepUsed,0.0)
   tfrac[gnfr]['UNREAC'] = 100.0  # to fill


# DEFAULTS?
for gnfrCode in camstab['tnosec']: # A B C .. A1 .F1..
  #print('FVALS-Y ', gnfrCode, tfrac['F'] )
  evals = np.array(list(tfrac[gnfrCode].values()))
  print('GVALS-TFR', gnfrCode, tfrac[gnfrCode] )
  print('GVALS-NFR', gnfrCode, gnfrFrac['EurTot'][gnfrCode] )
  print('GVALS-G ', gnfrCode, np.sum(evals), evals )
  if np.sum(evals) > 0:
    evals= 100 * ne.normedVals(evals,txt='EER'+gnfrCode)
  else:
    sys.exit('ARGH'+gnfrCode)
  gnfrFrac['EurTot'][gnfrCode] = evals
  print('KKKEUR', gnfrCode, gnfrFrac['EurTot'][gnfrCode])

# Snap sectors

for iso3 in gnfrFrac.keys():
 #for gnfrCode in gnfr[iso3].keys()

  for gnfrCode in 'A B C D E F J'.split():

     if not isinstance(gnfrFrac[iso3][gnfrCode],np.ndarray):
        print('SNAPSKIP', iso3, gnfrCode )
        continue

     ind=camstab['tnosec'].index(gnfrCode)
     snap = int( camstab['snap'][ind])
     snapFrac[iso3][snap] = gnfrFrac[iso3][gnfrCode]
     print('GNFR->SNAP? ', iso3, gnfrCode,snap, sfmt(snapFrac[iso3][snap]),'-> ')
     print('GNFR from ', iso3, sfmt(gnfrFrac[iso3][gnfrCode]))

    # TNO merge 3&4, so we just copy
     if snap==3:
       snapFrac[iso3][4] = snapFrac[iso3][3]
     elif snap==7:
        # Other mobile? Choose between shipping if no road-traffic
        # at all (sea-areas) and offroad
        if np.sum( gnfrFrac[iso3]['F'] ) > 0.0:
           snapFrac[iso3][8] = gnfrFrac[iso3]['I']
           txt='GinROAD'
        else:
           snapFrac[iso3][8] = gnfrFrac[iso3]['G']
           txt='GinSEA'
        print('DBG:'+txt, iso3, sfmt(snapFrac[iso3][8]))

# gnrfCode  K=AgriLivestock, L=AgriOther
  g = gnfrFrac[iso3]
  print('DBGKL-E ', iso3, e.keys() )
  Kemis = emNMVOC[iso3]['K'] # 1.6-e5
  Lemis = emNMVOC[iso3]['L'] # 1.6-e5
  print('DBGKL-K ', iso3, Kemis,Lemis, g['K'] )
  print('DBGKL-L ', iso3, Kemis,Lemis, g['L'] )
  #if (Kemis + Lemis )  > 0.0 :
  if np.sum(g['K']+g['L'])  > 0.0 :
    snapFrac[iso3][10] = 100 *  ne.normedVals(\
              [ g['K']*Kemis, g['L']*Lemis, ] ,\
              txt='Agri'+iso3,dbg=True) # iso3==isoDBG)
    print('DBGKLDONEL ', iso3,sfmt(snapFrac[iso3][10]))
  else:
    snapFrac[iso3][10] = np.zeros(npolls)
    print('DBGKLZERO ', iso3)
  print('GNFR-> KLAgr? ', iso3, 10, Kemis,Lemis, sfmt(snapFrac[iso3][10]))

  # Snap 11
  #snapFrac[iso3][11] = np.zeros(npolls)
  #snapFrac[iso3][11][-1] = 100.0
  


# GNFR
header="""# VOC splits for %s sectors and EmChem19a
# A=1;B=2;C=3;D=4;E=5;F=6;G=7;H=8;I=9;J=10;K=11;L=12;M=13;A1=14;A2=15;F1=16;F2=17;F3=18;F4=19
# ----------------------------------------------------------------------------
# Emissions from:   %s
# NMVOC split from: %s
# script:           %s
# ----------------------------------------------------------------------------
# Maps TNO/CAMS 25-compounds (v01...) from CAMS-REG-v3_1_2 matrix to EmChem species
# Note - two changes to keep C5H8 and terpenes as BVOC only:
#  moved trace amounts of apinene to 50%%  C2H4 and 50%% unreactive.
#  moved trace amounts of isoprene to C2H4.""" % ( 'gnfr', emisfile, splitfile, codetxt.codetxt(__file__)  )
print('DBGWRIYE', header )
x=we.write_emislist(gnfrFrac,emepUsed,header, label='gnfr')
#print('DBGKLHERE ', sfmt(snapFrac['ARM'][10]))
#y=we.write_emislist(snapFrac,emepUsed,label='snapX')

# SNAP

# Target EmChem19a has
#  99, 99,  NC4H10, OXYL, C2H4, C3H6, HCHO, MEK, TOLUENE, CH3OH, C2H6,  CH3CHO, C2H5OH, BENZENE, UNREAC,#HEADERS
#DATA
#  0,  1,  10.345, 6.62,3.154,3.325, 55.905, 0.0,  1.017, 0.704, 17.039,  0.02,    0.0,   1.869,  0.0
# misses GLYOX, MGLYOX and APINENE
