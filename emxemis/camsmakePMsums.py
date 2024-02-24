#!/usr/bin/env python3
""" Jan2022, May 2021: Use fbio = 1 for GNFR C to get get fake ECres for CAMS50
    Jun2022. Adapt to CAMS-REG-v5.1 """
# Adapted from 2021 camsmakePMsums.py
# Adapted from 2020 camsmakePMsums.py
# Adapted from RdCAMS50nov2019.py
# Adapted from RdCAMS71jan2020.py
# with more flexible read of bioshare for comp with Agnes (Mar 2020)
import collections
import numpy as np
import sys
# Dave's
#import emxemis.maccEmepCodes as macc2emep
import emxemis.camsInfo as camsInfo  # Dave's script to read CAMS.csv files.
                 # Returns a dictionary
                 # with values such as e1['CO']['NOR']['A:A']  for GNFR sector
                 # A (:A means area emissions), or e1['CO']['NOR']['Sum'] for
                 # sum of sectors
                 # Needed to convert shares in PM10 to shares in PMc
import emxemis.camsreadPMbioshares as camsreadPMbioshares
import emxemis.camsreadPMsplits as camsreadPMsplits # => split['EC']['NOR']['C']['fine']
import emxmisc.auto_dicts as auto_dicts

sizes = 'fine coarse'.split()

polls ='Emis OMff OMbio OMtot ECff ECbio ECtot Na SO4 OthMin'.split()
npolls= len(polls) # for fmt
headers=['poll','iso3','src'] + polls
print('HEADERS',headers)
emisSums = auto_dicts.Vividict() # Allows emisSums['ALB']['A:A'] in 1 step
firstSum = dict()
euSum='EUR'  # exists in cams_emep_codes as country 999

#----------------------------------------------------------------------------
# Process all splits here
#Year;ISO3;GNFR_Sector;EC_fine;OC_fine;SO4_fine;Na_fine;OthMin_fine

#tnoInputs='../EurodeltaCarb_2020agnes/TNO_Inputs/' # for share
tnoInputsShare='/home/davids/Work/D_Emis/TNO_Emis/TNO_Inputs/' # for bio share, for 2015 only
tnoInputs='/home/davids/lustre/storeB/project/fou/kl/emep/Emissions/CAMS50_U4_emissions/'
tnoInputs='/home/davids/CAMS50_U4_emissions/'
#tnoInputs='/home/davids/MDISKS/Nebula/MG/work/2022_CAMS2_40_U5_emissions/'
tnoInputs='/home/davids/Work/D_Emis/TNO_Emis/2022_CAMS2_40_U5_emissions/'
tnoSplits= tnoInputs + 'PM_split_for_CAMS-REG-AP_v5_1_with_Ref2_0_1_year2018_DT_20220102.xlsx'
tnoEmis= tnoInputs+ 'CAMS-REG-v5_1_with_Ref2_0_1_year2018_DT.csv'
outlabel = 'xgnfrRef%s_yr2018_cams50_jan2022'
# July 2023 Ref2:
tnoInputs='/home/davids/MDISKS/Nebula/MG/work/CAMS2_40/VRA2021_emissions/'
refNums = [ 'v6_1_1_Ref2_v2_1' ]    # messy labels...


def write_emissums(splits,emisdict,fbio,outlabel,dbg=False):

 for size in sizes:

   # Files to collect all data in one:
   outsum = open('emissums_%s_PM%s.csv' % ( outlabel, size), 'w' )
   sfmt = '%s,%s,%s' + ',%s'*npolls + '\n'
   outsum.write( sfmt %  tuple(headers) )
 
   poll = 'PM2_5'
   if size == 'coarse': poll = 'PMc'
   for component in 'sum omff ombb ecff ecbb Na so4 OthMin'.split():
     for src in emisdict['srcs']:
       emisSums[euSum][src][component] = 0.0

   for iso3 in emisdict['iso3s']:  
     if iso3 == 'EurTot': continue
     esum = 0.0 # sum per country
     print('SPLITHEAD',poll,iso3)
     for src in emisdict['srcs']:
       firstSum[src] = True
       #if src == 'Sum': continue
       print('SPLITTING',poll,iso3,src)
       sec, typ = src.split(':')  # A:P -> A, etc.
       om = splits['OC'][iso3][sec][size]
       ec = splits['EC'][iso3][sec][size]
       Na = splits['Na'][iso3][sec][size]
       so4= splits['SO4'][iso3][sec][size]
       OthMin= splits['OthMin'][iso3][sec][size]
       if om=={}: om=0.0
       if ec=={}: ec=0.0
       if Na=={}: Na=0.0
       if so4=={}: so4=0.0
       if OthMin=={}: OthMin=0.0
       remPPM = Na+so4+OthMin   # for EMEP
       sumPM = om+ec+remPPM
       if iso3=='NOR': print('Iceland SPLITTING',poll,iso3,src, om, sumPM )
       #M21 if sumPM < 0.9999: continue
       if sumPM < 1.0e-3: continue

       f=0.0
       #M21fake if sec == 'C' and iso3 in fbio: # misses eg ARM
       #M21  f = fbio[iso3][size]
       if sec == 'C' and size=='fine': # misses eg ARM
         f= 1.0
   
         #M21print('SSS', size, iso3, src, om, so4, 'f:', 
         #M21        fbio[iso3]['fine'],fbio[iso3]['coarse'])
      # use fbio for both EC and OM; since we don't know better
       omff = (1-f) * om
       ombb = f * om
       ecff = (1-f) * ec
       ecbb = f * ec
       if f>1 or ecff<0:
         print('SNEG', size, iso3, src, ec, 'f:', f,
                 fbio[iso3]['fine'],fbio[iso3]['coarse'])
         sys.exit()



#        else: # not all present, especially Africa, Middle-East
#          fbio = 0.0   # Crude, 

       if iso3 in emisdict['iso3s']:

        # output of simple format - all emissions and split
        # and convert to tonne (fac 0.001)
         ee= 0.001 * emisdict[poll][iso3][src]['sum']
         if iso3=='ARM':
           print('Iceland DICT',poll,iso3,src,ee, size )
         esum += ee
         sfmt = '%s,%s,%s,%s' + ',%.3f'*6
         print(sfmt%('EE'+ outlabel, iso3, poll, src, ee, f,
                   omff*ee,ombb*ee, ecff*ee, ecbb*ee) )
         #M21sfmt = '%s,%s,%s' + ',%.5f'*npolls + '\n'
         sfmt = '%s,%s,%s,%e' + ',%.5f'*(npolls-1) + '\n' # first num as %e
         #if iso3=='ITA' and src=='F1':
         if iso3=='ARM' and src.startswith('F'):
           print('DBGARM ', emisdict[poll][iso3][src] )
         #if ee>0.0:
         if ee>1.0e-6: # Prevens e.g. PMc ITA F2:A 9.99989424599e-13
           ee_out = ee
         else:
           ee_out = -999 # Marker for zero emissions
           ee = 1.0
         outsum.write( sfmt % ( poll, iso3, src, ee_out,
               omff*ee, ombb*ee, (omff+ombb)*ee, 
               ecff*ee, ecbb*ee, (ecff+ecbb)*ee, 
               Na*ee, so4*ee, OthMin*ee
               ))
         print('ESUMB', emisSums[euSum][src]['sum'], ee, src)
         emisSums[euSum][src]['sum']    += ee  # query 0.01 fac
         emisSums[euSum][src]['omff']   += omff*ee
         emisSums[euSum][src]['ombb']   += ombb*ee
         emisSums[euSum][src]['ecff']   += ecff*ee
         emisSums[euSum][src]['ecbb']   += ecbb*ee
         emisSums[euSum][src]['Na']     += Na*ee
         emisSums[euSum][src]['so4']    += so4*ee
         emisSums[euSum][src]['OthMin'] += OthMin*ee

       else:
         sys.exit('missing%s' % iso3)
   # Now, European totals:
   for src in emisdict['srcs']:
      sec, typ = src.split(':')  # A:P -> A, etc.
      ee=  emisSums[euSum][src]['sum']   #= ee  # query 0.01 fac
      if not ee: continue # some can be empty, e.g. L:P
      print('ESUMC', emisSums[euSum][src]['sum'], ee, src)
      omff=emisSums[euSum][src]['omff']  #= omff*ee
      ombb=emisSums[euSum][src]['ombb']  #= ombb*ee
      ecff=emisSums[euSum][src]['ecff']  #= ecff*ee
      ecbb=emisSums[euSum][src]['ecbb']  #= ecbb*ee
      Na = emisSums[euSum][src]['Na']    #= Na*ee
      so4= emisSums[euSum][src]['so4']   #= so4*ee
      OthMin= emisSums[euSum][src]['OthMin']  #= OthMin*ee
      outsum.write( sfmt % ( poll, euSum, src, ee, omff, ombb, (omff+ombb),
          ecff, ecbb, (ecff+ecbb), Na, so4, OthMin ))

 return 'finished %s' % outlabel
#----------------------------------------------------------------------------

#for refNum in [ 1, 2 ]:
for refNum in refNums: 

  elabel    ='CAMS-REG-AP_%s_year2021' % refNum    # => e.g. CAMS-REG-AP_v6_1_1_Ref2_v2_1_year2021.csv
  tnoEmis   = tnoInputs+ elabel + '.csv'  #'CAMS-REG-AP_v6_1_1_Ref2_v2_1_year2021.csv'
  outlabel  = 'gnfr_%s' % elabel
  print('OUTS: ', tnoEmis, outlabel)

  # 1) Splits =>  s['EC']['NOR']['C']['fine']

  if 'Ref2' in refNum:
     tnoSplits = tnoInputs + 'CAMS-REG-v6_PM_split_Ref2.xlsx'
  else:
     tnoSplits = tnoInputs + 'CAMS-REG-v6_PM_split.xlsx'

  splits= camsreadPMsplits.getPMsplit( tnoSplits) #JAN2022 Inputs + \

  # 2)  Emissions => e['CO']['NOR']['A:P'],  e['snap2']['PM2_5']['NOR']
  e=camsInfo.readCams( tnoEmis, wanted_poll='PM' ) # JAN2022 + \

  # 3) bioshares, => f[iso3][size]
  # for small combustion and PM2_5 or PM10. 
  # Have to pass snap2 emissions to get PMc values
  #for PMc_method in 'max1 raw10'.split():
  # raw just applied fbio from PM10 to PMc, since 'proper' calc gives neg values.

  for PMc_method in 'raw10'.split():

     #JAN2022: FAKED ANYWAY 'Share_biofuels_in_PM_small_combustion_REF%d_2015.csv' % refNum, \
     #JAN2022: 1,2015,';', snap2=e['snap2'],txt='Ref%d'% refNum, \
    fbio=camsreadPMbioshares.get_biofrac( tnoInputsShare + \
     'Share_biofuels_in_PM_small_combustion_REF%d_2015.csv' % 2 , \
        1,2015,';', snap2=e['snap2'],txt='Ref%d'% 2, \
        PMc_method=PMc_method) # ,dbg=True,dbgcc='NOR')
    # FAKE-it: set fbio to 1.0 for all GNFR C, since CAMS-50 wants ECres, not ECwood etc
    for cc in fbio.keys():
      for size in sizes:
        fbio[cc][size] = 1.0

    #JAN2022 outlabel = 'gnfrRef%s_yr2017_cams50_fakeECres_may2021' % refNum
    #JULY 2023 xoutlabel = outlabel % refNum
    f=write_emissums(splits,e,fbio,outlabel,dbg=False)

