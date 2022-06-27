#!/usr/bin/env python3
from collections import OrderedDict as odict
#from collections import defaultdict
import glob
import numpy as np
import os
import pandas as pd
import sys
from emxmisc.auto_dicts import Vividict  # Used since defautdict gave KeyError. 

run='jun2022'
tdir=os.environ['HOME'] + '/Work/D_Emis/CEDS/'
if run=='jun2022':
  xyears=list(range(1850,2019,10)) # test years
  xyears=list(range(1960,1991,10)) # test years
  xyears[-1] = 1990  # for Ndep project
  files=glob.glob('%s/Updates/CEDS_v2021-04-21_emissions/*sector_country*csv' % tdir )
else:
  xyears=list(range(1850,2011,10)) # test years
  xyears[-1] = 2005
  files=glob.glob('%s/Supplement/Data_Supplement/*sector_country*csv' % tdir )
#snaps='tot soil road air ship'.split() # skip dom= 1A4b_Residential, ratios became v. large for VOC, CO
emissecs = list(range(14)) # Use zero for totals

def get_ceds_emis(years=xyears,dbgPoll=None,files=files):   # 

   dbg = False
   if dbgPoll is not None:
       files=glob.glob('%s/Updates/CEDS_v2021-04-21_emissions/%s*sector_country*csv' % ( tdir, dbgPoll) )
       dbg=True

   emis=Vividict()
   polls = []
   
   nf= 0
   for f in files:
     nf2 = 0  # by file
     print(f , '='*20)
   
     inp=pd.read_csv(f)
     """"em","country","sector","units","X1750","X1751","X1752","X1753","X1754","X1755",
      "NOx","abw","1A1a_Electricity-autoproducer","ktNO2",0,0,0,0,0,0,0,0,0,0,0,0,0,0,
      "NOx","abw","1A1a_Electricity-public","ktNO2",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
      """
     em =inp['em']
     poll =em[0]
     if poll in [ 'CO2', 'N2O', 'CH4' ]: continue
     polls.append(poll)
     cc =inp['country']
     CC = [ i.lower() for i in cc ]  # Use lower case
     CC = [ i.replace('srb (kosovo)','kos') for i in CC ]
     uCC = np.unique(CC)
     #print(uCC)
     sec=inp['sector']
     secs=inp['sector'].unique()
     if dbg: print('nsec', len(sec.unique()))  # 60 for Updates
     for i, s in enumerate(secs):
       if dbg: print('Sectors:', i, s)
     units=inp['units']
   
     for land in CC:
       for y in years:
         #if land == 'FIN' and poll == 'SO2' : print('LAND ', land, y, s, poll )
         for s in emissecs:
           #print('LAND ', land, y, s, poll )
           emis[land][poll][y][s]  = 0.0
   
     # Sectors: 58 1A3aii_Domestic-aviation
     # Sectors: 59 1A3di_International-shipping (cf 1A3dii_Domestic-navigation)
     # Only found for "global", even 1A3aii_Domestic-aviation (Odd!)
     # 3D?
     # 3D_Rice-Cultivation 3D_Soil-emissions

     for n, s in enumerate(sec):
        # if dbg: print('AIR %-5s %s %-30s %12.3e' % ( poll, CC[n], s, inp['X2005'][n]) )
        # #continue
        #elif 'shipping' in s: # International-shipping
        # if dbg: print('SHIP %-5s %s %-30s %12.3e' % ( poll, CC[n], s, inp['X2005'][n]) )
        #elif poll =='NOx' and  '3D_' in s: # International-shipping
        # if land=='DEU':print('Skip Soil', n,  poll, s)
        # continue
   
        land=CC[n]
        for y in years:
          x='X%d' % y
          #if land=='DEU' and poll=='NOx' and  y==years[-1]: print('DEnox', y, n, x, s,  inp[x][n])

          emis[land][poll][y][0]  += inp[x][n]

          remark=''  # will fill in if needed
          if   '1A1a' in s: gnfr = 1  # A_PublicPower
          elif '1A1'  in s: gnfr = 2 #  B_Industry e.g. 1A1b. 1A1v
          elif '1A2'  in s: gnfr = 2 #  B_Industry still, though some in 9?
          # Messy with 1A3...
          elif 'aviation' in s:
              gnfr = 8 #14?  1A3ai_International-aviation, 1A3aii_Domestic-aviation, both GLOBAL
          elif 'shipping' in s: gnfr = 7 #15? 1A3di_International-shipping, only global
          elif 'navigation' in s: gnfr = 7 # 1A3dii_Domestic-navigation => 7,G_Shipping
          elif 'Road' in s: gnfr = 6  #  SNAP7, 1A3b_Road
          elif '1A3' in s: gnfr = 9  # => I_Offroad #1A3c_Rail, 1A3di_Oil_Tanker_Loading, 1A3dii_Domestic-navigation, 1A3eii_Other-transp
          elif any ( '1A4%s' % e in s for e in ['a', 'b']):
             gnfr = 3   # COMPLICATED 7, 8, 9 ....
             details="""
Cross_Walk_NFR_GNFR_ds.csv
3,C_OtherStationaryComb,1A4ai,Commercial/institutional: Stationary,
9,I_Offroad,1A4aii,Commercial/institutional: Mobile,
3,C_OtherStationaryComb,1A4bi,Residential: Stationary,
9,I_Offroad,1A4bii,Residential: Household and gardening (mobile),
3,C_OtherStationaryComb,1A4ci,Agriculture/Forestry/Fishing: Stationary,
9,I_Offroad,1A4cii,"Agriculture/Forestry/Fishing: Off-road vehicles and
other machinery",
9,I_Offroad,1A4ciii,Agriculture/Forestry/Fishing: National fishing,
3,C_OtherStationaryComb,1A5a,Other stationary (including military),
9,I_Offroad,1A5b,"Other, Mobile (including military, land based and recreational boats)",
CEDS:
Sectors: 22 1A4a_Commercial-institutional
Sectors: 23 1A4b_Residential
Sectors: 24 1A4c_Agriculture-forestry-fishing
"""
#
          elif '1A4a' in s: gnfr = 3   # COMPLICATED 7, 8, 9 ....
          elif '1A4b' in s: gnfr = 3   # COMPLICATED 7, 8, 9 ....
          elif '1A4c' in s: gnfr = 9  # I_Offroad, 1A4c_Agriculture-forestry-fishing, 
          elif '1A5'  in s: gnfr = 9  # 1A5_Other-unspecified, should also have 3 (ref NAEI 1A5a)?
          elif '1B'   in s: gnfr = 4  # D_Fugitive
          elif any ( '2%s' % e in s for e in ['A', 'B', 'C', 'H', 'L' ]):
              gnfr = 2
          elif '2D'   in s: gnfr = 5  #  E_Solvents 
          elif '3B'   in s: gnfr = 11 #  K_AgriLivestock
          elif '3E'   in s: gnfr = 11 #  K_AgriLivestock??? 3EEnteric-fermentation
          # 3D= 3D_Soil-emissions, 3D_Rice-Cultivation,  3I=N-fertilizers, manure, etc.
          elif any ( '3%s' % e in s for e in ['D', 'I' ]):
              gnfr = 12 #  L_AgriOther,
          elif  s.startswith('5') : gnfr = 10 #  J_Waste
          elif  s.startswith('6') : gnfr = 10 #  J_Waste 6A_Other-in-total, 6B_Other-not-in-total ????
          else:  # 7A_Fossil-fuel-fires, 7BC_Indirect-N2O-non-agricultural-N 
             gnfr = 2

          #if land =='DEU' and inp[x][n] > 0.0 :
          #    print('MAPS %s %-4s %2d %4d %12.3f    %s' % ( cc[n], poll, gnfr, y, inp[x][n], s ))
          #print('MAPS', land, poll, y,  gnfr, s, inp[x][n] )

          if 'aviation' in s and poll == 'NOx': print('AFLY', land, poll, y, s, gnfr, inp[x][n]  )
          emis[land][poll][y][gnfr]  += inp[x][n]
          if land=='global' and gnfr == 8 and poll=='NOx':
              print('BFLY', land, poll, y, s, gnfr, inp[x][n], emis[land][poll][y][gnfr]  )

   #print('YEARS ', years )
   return  polls, emissecs, emis

if __name__ == '__main__':

   polls, emissecs, emis = get_ceds_emis([1980,1990],dbgPoll='NOx')  # 
   print(emis.keys() )
   dbgcc='global'; dbgpoll ='NOx'

   for s in emissecs:

     femis = -1
     if emis[dbgcc][dbgpoll][1990][s] > 0.0:
           femis = emis[dbgcc][dbgpoll][1980][s]/  emis[dbgcc][dbgpoll][1990][s]
     print('DBG:', s,  emis[dbgcc][dbgpoll][1980][s],  emis[dbgcc][dbgpoll][1990][s], femis )
