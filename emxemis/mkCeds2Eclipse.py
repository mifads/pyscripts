#!/usr/bin/env python3
import numpy as np
from collections import OrderedDict as odict
#from AutoVivs import Vividict as vdict  # Used since defautdict gave KeyError. 
import os
import pandas as pd
import sys
from emxmisc.auto_dicts import Vividict as vdict  # Used since defautdict gave KeyError. 

from emxmisc.auto_dicts import Vividict as vdict  # Used since defautdict gave KeyError. 
#import RdCEDS  # get_ceds_emis for tot, dom and road. Use def years
import emxemis.readCedsEmis as readCedsEmis  # get_ceds_emis for tot, dom and road. Use def years

odir='Femis_CEDtoEclipse_June022'
os.makedirs(odir,exist_ok=True)

Historical=True
#years=[ 1950, 2005 ]
if Historical:
  #years= list(range(1850,2011,10)) 
  years= list(range(1980,1990,5))  # 1991 would give double entry!
  ref= 1990  # We need this in list to get femis
  years.insert(-1,ref)
else:
  ref=2010
  years= list(range(2010,2015,2)) # Can't use 2015 
print(years)

# Get emissions: #  e.g. secs =  ['tot', 'road', 'air']
# keys of emis are CEDS countries, including GLOBAL for aviation and int. shipping
# secs are now 0..13, where 0 is for total

polls, secs, ceds_emis = readCedsEmis.get_ceds_emis(years,dbgPoll=None)  # e.g. emis[cc]['BC'][1990][sec]

print('SECS', secs )
print('CCS', ceds_emis.keys() )
print('NH3 gnfr 4', ceds_emis['grc']['NH3'][1980][4], ceds_emis['grc']['NH3'][1990][4] )
print('NH3 gnfr 5',ceds_emis['grc']['NH3'][1980][5], ceds_emis['grc']['NH3'][1990][5] )
print('NOx gnfr 8',ceds_emis['global']['NOx'][1980][8], ceds_emis['global']['NOx'][1990][8] )

dbg_cnum=1          # 225  # KORN = ceds PRK
dbg_gains= 'AL'  # 'KORN'
dbg_iso3 = 'global'  # 'PRK'
dPoll = 'NOx'

print('DBG ', ceds_emis[dbg_iso3][dPoll][years[0]][6], # 'road'], 
              ceds_emis[dbg_iso3][dPoll][years[-1]][6], # road'], 
              ceds_emis[dbg_iso3][dPoll][years[0]][0], # tot'], 
              ceds_emis[dbg_iso3][dPoll][years[-1]][0] # tot'] )
     )

# 1)  eclipse_to_ceds.txt:
#  cc        gains           ceds    comment
#   1           AL             ALB    -
# 224         NAFR             SSD,SDN,DZA,LBY,MAR,TUN    from_atlas_only
# 1TMP) Res_mkEclipseCedsMapping_June2022.txt
## Created by mkEclipseCedsMapping June 2022
# then edited from older_eclipse_to_ceds.txt and by hand
#cnum   gains_isoX         iso3 cnum_ceds
#   1           AL          alb    1
#   2           AT          aut   10
#..
#   6           DK          dnk,fro   55

ds=pd.read_csv('EditRes_mkEclipseCedsMapping_June2022.txt',sep='\s+',skiprows=2)
emep_cnum = ds.cnum.values
gains_code = ds.gains_isoX
ceds_codes = ds.iso3

outemis = vdict() # will store sums of countries

for y in years:

  for cnum, gains, ceds_iso3s in zip( emep_cnum, gains_code, ceds_codes):
    print('MK', cnum, gains, ceds_iso3s ) #  MK 1 AL ALB
    if gains==dbg_gains: 
      print ('ICC', y, 'cnum:', cnum, 'gain:', gains )

    # Collect info into GAINS groups first, using e.g. =>  emis[2]['BC'][1990]

    for poll in polls:
       outemis[cnum][poll][y] = np.zeros(len(secs)) # [s] = 0.0
       for s in secs:

          for ceds_iso3 in ceds_iso3s.split(','): # Sum over groups of countries
        
            print('PP', poll, y, s, ceds_iso3 )
            em = ceds_emis[ceds_iso3][poll][y][s]
            print('SS', poll, y, s, type(em), em  )
            if em > 0.0:
              print ('CEDS', cnum, s,  ceds_iso3, ceds_iso3s, poll , em )
              outemis[cnum][poll][y][s] += em

              if cnum == dbg_cnum and poll==dPoll:
                print ('SPL', y, ceds_iso3, poll, cnum, s, ceds_emis[ceds_iso3][poll][y][s], outemis[cnum][poll][y][s] ) # , ceds[cc][poll][-1][s] )

            if ceds_emis[ceds_iso3][poll][y][0] < 0.0:
              print( 'NEG! ', ceds[ceds_iso3][poll][y] )
              sys.exit()


    for poll in [ 'PM25', 'PMco' ]:
       outemis[cnum][poll][y] = np.zeros(len(secs))

    for s in secs:
      for ceds_iso3 in ceds_iso3s.split(','): # Sum over groups of countries
        if cnum==dbg_cnum: print('PM:', cnum, y, s, ceds_emis[ceds_iso3]['BC'][y][s],ceds_emis[ceds_iso3]['OC'][y][s])
        print('PM', y, s, ceds_iso3, ceds_emis[ceds_iso3]['BC'][y][s] )
        pm = ( ceds_emis[ceds_iso3]['BC'][y][s]+1.3*ceds_emis[ceds_iso3]['OC'][y][s] + 
                0.05*ceds_emis[ceds_iso3]['SO2'][y][s]  )  # we assume PM ~ 5% SO2+1.3*OC+BC
        outemis[cnum]['PM25'][y][s] += pm
        outemis[cnum]['PMco'][y][s] += pm  # Making same scaling as PM2.5

    # We group several sectors together to try for more robust femis
    """
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

    grps=dict()
    for poll in polls + [ 'PM25', 'PMco' ]:
      grps['ene']    = np.array([1,2])
      grps['misc']   = np.array([4,5,7,8,9,10,13])
      grps['agr']    = np.array([11,12])
      #grps['nroad']    = np.array([7,8,9])
      for grp, subsecs in grps.items():
          if cnum == 999: 
              continue  # don't add global ships + aircraft!
          sumgrp = outemis[cnum][poll][y][subsecs].sum()
          for s in  subsecs:
            orig                      = outemis[cnum][poll][y][s]
            outemis[cnum][poll][y][s] = sumgrp
            if cnum==11 and poll=='CO': print('SUM '+grp, y, cnum, s,  orig, outemis[cnum][poll][y][s] )

# Now, we have 2005 and all other years
header='Land   7     nox      nh3       co       voc      sox       pmco     pm25'
fmt=   '%4s  %4d %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f\n'
print(header)
femis=odict()
for y in years:
  with open(odir+'/femisLand.ceds%dtoEclipse%d' % ( ref, y), 'w' ) as f:
    ftot=open(odir+'/femisLand.cedsTots%dtoEclipse%d' % ( ref, y), 'w' )
    f.write(header+'\n')
    ftot.write(header+'\n')
    for cnum, iso3 in zip(emep_cnum, ceds_codes):

      print('Femis ', cnum, iso3, len(emep_cnum), len(ceds_codes)  )
      for s in secs:

          outstr=''
          emtot = 0.0
          for poll in 'NOx NH3 NMVOC CO SO2 PM25 PMco'.split():
            print('EMTOT', cnum, y,  s, poll, outemis[cnum][poll][ref][s],  emtot )
            emtot += outemis[cnum][poll][ref][s]
         
          for poll in 'NOx NH3 NMVOC CO SO2 PM25 PMco'.split():

            emref = outemis[cnum][poll][ref][s]
            emyr  = outemis[cnum][poll][y][s]
            
            #if cnum==11 and poll == 'NH3':
            #  if poll=='NH3':print('xx'+poll, y, ref, s, emref, emyr)
            print('xx'+poll, iso3, y, ref, s, emref, emyr, type(emref) )
            if isinstance(emref,float) and  emref > 0.0:
              femis[poll] = emyr / emref
            else:
                print('FEMIS', s, poll, emref )
                femis[poll] = femis0[poll] # scale by totals
            if femis[poll] > 13.0:
                print('ALERT:ff'+poll, cnum, iso3,  y, ref, s, emref, emyr, femis[poll] )
                #if cnum < 300: print('FAILED ', cnum, s, poll, outemis[cnum][poll][ref][s] )

            outstr += '%10.4f' % femis[poll]
            if s==0: femis0 = femis.copy()

          #outstr += '%10.1f' % emtot # just checking

          outcnum = cnum
          if iso3 == 'global':
                if   s ==  7: outcnum = 350
                elif s ==  8: outcnum = 900
                else:
                    print('CONTINUES', cnum, s,  outstr)
                    continue
          if s > 0 : 
            f.write('%4d %4d %s\n' % ( outcnum, s, outstr))
          else:
            ftot.write('%4d %4d %s\n' % ( outcnum, s, outstr))

