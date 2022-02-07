#!/usr/bin/env python3
""" Reads pre-processed emissums file, in which emissions are given for
    OMff, etc. for all detailed sectors (A1, F3, ...) and produces
    defaults and specials emissplit files
   JAN 2022 - 
   MAY 2021 - edited to make ResNonRes species
"""
# 2022: Adapted from 2021 camsmakePMsplits.py. Still hard-coded compared to camsmakeNMVOC.py
# and now including SO4 (fine only)
# Adapted from RdCAMS50nov2019.py
# Adapted from RdCAMS71jan2020.py
# Adapted from camsmakePMsplits.py (June 2020)
# with more flexible read of bioshare for comp with Agnes (Mar 2020)
import collections
from datetime import date
import numpy as np
import pandas as pd # mar2020 as genfromtxt didn't have encoding
import pprint # pretty print
import os
import sys
# Dave's
import emxmisc.auto_dicts as auto_dicts
import emxemis.cams_emep_codes as ce
import emxemis.camsSectorTables as cs
import emxmisc.codetxt as codetxt
import emxemis.normaliseEmisSplits as en

# For outputs:

def sfmt(array):
  """ join-function for a list of numbers """
  return ';'.join(str(x) for x in array) 

use_so4 = True # true for cams
ResNonRes = False
ResNonRes = True
header_specs = dict()
if ResNonRes:
  header_specs['fine'] = 'POM_f_Res,POM_f_nonRes,EC_f_Res_new,EC_f_Res_age,EC_f_nonRes_new,EC_f_nonRes_age,remPPM25_Res,remPPM25_nonRes'  
  header_specs['coarse'] = 'POM_c_Res, POM_c_nonRes,  EC_c_Res, EC_c_nonRes, remPPM_c_Res,remPPM_c_nonRes'
  if use_so4:
    header_specs['fine'] += ',SO4'  
    header_specs['coarse'] += ',SO4'  
else:
  header_specs['fine'] = 'POM_f_ffuel,POM_f_wood,EC_f_ffuel_new,EC_f_ffuel_age,EC_f_wood_new,EC_f_wood_age,remPPM25'  
  header_specs['coarse'] = 'POM_c_ffuel,  EC_c_ffuel, EC_c_wood, remPPM_c'
  sys.exit('NOT CODED YET')
pp=pprint.PrettyPrinter(indent=4)

sizes = 'fine coarse'.split()
numRefs = [ '2_0_1' ] # May2021: could be 1, 2
#sizes = 'fine'.split()
emepcc = ce.get_emepcodes() # gets emep cc iso2 iso3 name
camstab = cs.camstab()
isoDBG='ARM'
isoDBG='GRL'
#isoDBG='EUR'

# The PM_split files have A,B,C,D,E,F1,F2,F3,F4,G,H,I,J,K,L,
# though no data for A1, A2. Will copy from A

# 1)  Get sector mapping:
# cams3p1_table = """# Nov 2019
# emep  cams_code snap   cams_long
#  1        A        1   A_PublicPower
#..
#  14      A1        1   A1_PublicPower_Point
#  15      A2        1   A2_PublicPower_Area
#  16      F1        7   F1_RoadTransportExhaustGasoline

gnfrNum, gnfrName = cs.getCams2emep() # e.g. gnfrNum['G']=7,
ap = cs.tnoAPmapping()  # gets "A:A" to 'A'
camstab = cs.camstab()  # gets cmap['tnosec']  # A, B, C...

#----------------------------------------------------------------------------
def fillVals(ehandle,npolls,txt=''):
  """ converts empty emis dicts to zeros """
  if ehandle['emis'] == {}:
     emis = -888 # need to distinguish from 0.0 and -999
     vals = np.zeros(npolls)
     print('Fill '+txt)
  else:
     vals = ehandle['vals']
     emis = ehandle['emis']
  return emis, vals

#----------------------------------------------------------------------------
def process_emissums(numRef,label,dbg=False):

  epolls='OMff,OMbio,OMtot,ECff,ECbio,ECtot,Na,SO4,OthMin'.split(',')
  epolls='OMff,OMbio,ECff,ECbio,Na,SO4,OthMin'.split(',') # Skip tots
  npolls=len(epolls)

  emisSums = auto_dicts.Vividict() # allows emisSums[size]['ALB']['A:P']
  gnfrFrac = auto_dicts.Vividict() # allows emisSums[size]['ALB']['A:P']
  snapFrac = auto_dicts.Vividict() # allows emisSums[size]['ALB'][1]

#-size
#s.head(2)=
#   poll iso3  src     Emis    OMff  OMbio   OMtot   ECff  ECbio  ECtot  Na ...
#0  PM2_5  ALB  A:A -999.000   0.230    0.0   0.230  0.098    0.0  0.098   ..
#1  PM2_5  ALB  A:P   26.000   5.972    0.0   5.972  2.548    0.0  2.548  ..
#May 2021:
#emissums_gnfrRef2_yr2017_cams50_fakeECres_may2021_PMcoarse.csv
#emissums_gnfrRef2_yr2017_cams50_fakeECres_may2021_PMfine.csv
  """
poll,iso3,src,Emis,OMff,OMbio,OMtot,ECff,ECbio,ECtot,Na,SO4,OthMin
PM2_5,ALB,A:A,-9.990000e+02,0.04906,0.00000,0.04906,0.47107,0.00000,0.47107,0.01500,0.05205,0.41283
PM2_5,ALB,A:P,4.880000e+01,2.39400,0.00000,2.39400,22.98800,0.00000,22.98800,0.73200,2.54000,20.14600
  etc """
  for size in sizes:
    print('LAB ', label, size )
    s=pd.read_csv('emissums_%s_PM%s.csv'% (label, size))
    

    srcs =  s.src.unique()
    iso3s = list(s.iso3.unique()) # list for next steps
    iso3s.remove('EUR')
    iso3s.append('EUR') # make last

    # https://thispointer.com/pandas-6-different-ways-to-iterate-over-rows-in...
    # ...-a-dataframe-update-while-iterating-row-by-row/
    #row=arow._asdict()   # F.. pandas :-( Needed to use epoll below

#-size
#   arow
    #for arow in s.iterrows():
      #row=arow[1]  # 0 contains number of row
      #print('NROW', nrow)
      #print('AROW', arow)
    for nrow, row in s.iterrows():

      # when emissions are close to zero (and not -999!), harder to trust
      # fractions. Just revert to default emis splits for these cases

      iso3=row.iso3
      src=row.src

      #if abs(row.Emis) < 0.001:
      #M21if abs(row.Emis) < 0.0:
      #M21   print('Emis too low. Skip',iso3,src,row.Emis)
      #M21   continue

      cc= emepcc[iso3]['cc']
      if iso3=='EUR': cc= 0   # for defaults file

      gnfr, typ = src.split(':')
      gnum = gnfrNum[gnfr]

      emisSums[size][iso3][src]['emis'] = max(row.Emis,0.0)
      emisSums[size][iso3][src]['vals'] = np.zeros(npolls)

      for n, epoll in enumerate(epolls):
        emisSums[size][iso3][src]['vals'][n] = row[epoll]
        if iso3==isoDBG:
           print('dbgRow'+size,iso3,cc, gnum, src, n,
                                  epoll, row[epoll], row.Emis )
           #sys.exit()
                      

#-size
#   iso3
    for iso3 in iso3s:
      e=emisSums[size][iso3]
      if iso3==isoDBG:
          print('DBGemis'+size)
          pp.pprint(e)
#-size
#   iso3
#     gnfr
      for gnfr in  gnfrNum.keys(): # A, B, ... F4
        area  ='%s:A'%gnfr
        point ='%s:P'%gnfr
        eeA, evA = fillVals( e[area],  npolls, 'evA:'+iso3+gnfr )
        eeP, evP = fillVals( e[point], npolls, 'evP:'+iso3+gnfr )
        if iso3==isoDBG:
          print('DBGEE'+size, size, iso3, gnfr, eeA, eeP )
          print('DBGAV'+size, size, iso3, gnfr, sfmt(evA) )
          print('DBGPV'+size, size, iso3, gnfr, sfmt(evP) )

        if eeA >= 0.0 and eeP >= 0.0:
           vals= en.normedVals([ evA, evP], txt='A+P:'+iso3,dbg=iso3==isoDBG)
        elif eeA >= 0.0:
           vals= en.normedVals( evA, txt='eeA:'+area+':'+iso3,dbg=iso3==isoDBG)
        elif eeP >= 0.0:
           vals= en.normedVals( evP, txt='eeP:'+point+':'+iso3,dbg=iso3==isoDBG)
        else:
           vals= np.zeros(npolls)
           print('NOT FOUND:'+iso3+gnfr)

        if iso3==isoDBG:
          print('OUTV '+size, size, iso3, gnfr, sfmt(vals) )

        gnfrFrac[size][iso3][gnfr] = vals.copy()
        if dbg: print('SFMT'+iso3, gnfr, sfmt(vals))

        if gnfr == 'A1':
           gnfrFrac[size][iso3]['A1'] = gnfrFrac[size][iso3]['A']
        if gnfr == 'A2':
           gnfrFrac[size][iso3]['A2'] = gnfrFrac[size][iso3]['A']


#-size
#   iso3
#     gnfr
      gnfr='F'    # Needs post-process  from  F1 etc
      echeck = e['F1:A']['vals']
      if isinstance(echeck,np.ndarray):
          
         for num in range(1,5):
           print('M21:F%d '%num,iso3, size, e['F%d:A'%num]['vals'] )
         gnfrFrac[size][iso3][gnfr] = en.normedVals(\
                 [ e['F1:A']['vals'] ,e['F2:A']['vals'] ,\
                   e['F3:A']['vals'] ,e['F4:A']['vals'] ],\
                  txt='Trafficx4'+iso3,dbg=True) # iso3==isoDBG)
         vals = gnfrFrac[size][iso3]['F']

#     iso3
      # Add snaps
      #e=emisSums[size][iso3]
      print('ISO ', iso3)
      for gnfr in 'A B C D E F J'.split():
        ind=camstab['tnosec'].index(gnfr)
        snap = int( camstab['snap'][ind])
        snapFrac[size][iso3][snap] = gnfrFrac[size][iso3][gnfr] 
        print('GNDR->SNAP? ', iso3, size, gnfr,snap, sfmt(snapFrac[size][iso3][snap]),'-> ')
        print('GNDR from ', iso3, size,sfmt(gnfrFrac[size][iso3][gnfr]))
        print('TYPE ', type(snap))

      # TNO merge 3&4, so we just copy
      snapFrac[size][iso3][4] = snapFrac[size][iso3][3]

      # Other mobile? Choose between shipping if no road-traffic
      # at all (sea-areas) and offroad
      if np.sum( gnfrFrac[size][iso3]['F'] ) > 0.0:
         snapFrac[size][iso3][8] = gnfrFrac[size][iso3]['I']
         txt='GinROAD'
      else:
         snapFrac[size][iso3][8] = gnfrFrac[size][iso3]['G']
         txt='GinSEA'
      print('DBG:'+txt, iso3, sfmt(snapFrac[size][iso3][8]))
      #sys.exit()
      #print('GNDR->SNAP? ', iso3, size, gnfr,8, sfmt(snapFrac[size][iso3][8]))

      gnfr = 'K:A' #  K=AgriLivestock, L=AgriOther
      echeck = e[gnfr]['vals']
      print('DBGK ', iso3, size, gnfr, sfmt(e['K:A']['vals']) ,sfmt(e['L:A']['vals']))
      if isinstance(echeck,np.ndarray):
        print('AGRIK', np.sum(e[gnfr]['vals']), np.sum(e['L:A']['vals']))
        snapFrac[size][iso3][10] = en.normedVals(\
              [ e['K:A']['vals'] ,e['L:A']['vals'] ] ,\
              txt='Agri'+iso3,dbg=True) # iso3==isoDBG)
      else:
        snapFrac[size][iso3][10] = np.zeros(npolls)
      print('GNDR->SNAP? ', iso3, size, gnfr,10, sfmt(snapFrac[size][iso3][10]))

      # Snap 11
      snapFrac[size][iso3][11] = np.zeros(npolls)

      if iso3==isoDBG: 
          print('SUMVALS',size, gnfr, np.sum(vals) )
          print('gnfrINTER', size, gnfr, gnfrFrac[size][isoDBG]['A'][0], \
           gnfrFrac[size]['ALB']['A1'][0], gnfrFrac[size][isoDBG]['A2'][0])
          for sec in range(1,12):
             print('SNAPEND', iso3, sec, snapFrac[size][iso3][10])

#-size
#   iso3
#     gnfr

      if iso3==isoDBG:
        print('DBGEND emisSums:', size)
        pp.pprint(emisSums[size][isoDBG])
        print('RE_A2FMT'+iso3, 'A', sfmt(gnfrFrac[size][iso3]['A']))
        print('RE_A2FMT'+iso3, 'A1', sfmt(gnfrFrac[size][iso3]['A1']))
        print('RE_A2FMT'+iso3, 'A2', sfmt(gnfrFrac[size][iso3]['A2']))
        print('DBGEND gnfrFrac:', size)
        print('A4FMT'+iso3, 'A2', sfmt(gnfrFrac[size][iso3]['A2']))
        pp.pprint(gnfrFrac[size][isoDBG])

        # OMff   from ALB C  should be 0.012948
        # ECfine from UZB F1 should be 0.229626

  print('XX iso3s', iso3s)
  print('YY Frac', type(gnfrFrac), type(snapFrac))
  return iso3s, gnfrFrac, snapFrac

#----------------------------------------------------------------------------
def write_emislist(numRef,iso3s, tnoref, emisFrac,label,dbg=False):
  today = date.today()
  src_code=os.path.dirname(os.path.realpath(__file__)) + '/%s'% os.path.basename(__file__)
  src_code = src_code.replace('/home/davids','~')
  # now as input
  #tnoref='CAMS-REG-AP_v2.2.1_2015_REF%s' % numRef # REF1 or REF2
  #tnoref='CAMS-REG-AP_v4_2_yr2015_REF%s' % numRef # REF1 or REF2

  header_str= """# PM%s splits for EmChem19a, 19-GNFR-sector-system
# A=1;B=2;C=3;D=4;E=5;F=6;G=7;H=8;I=9;J=10;K=11;L=12;M=13;A1=14;A2=15;F1=16;F2=17;F3=18;F4=19
# ----------------------------------------------------------------------------
# Emissions from:   CAMS-REG-v5_1_with_Ref2_0_1_year2018_DT (CAMS2_40_U5)
# script:           %s
# (Generated by DS)
# ----------------------------------------------------------------------------
# Key-word MASS_ASSUMED= 0 by default, 
# change when emissions have artificial mass; e.g. 46 for NOx as NO2
: MASS_ASSUMED 0 
99,99,  %s,  #HEADERS
#DATA
""" 
 # header_str % ( size, tnoref, label, src_code, today, sector_str, header_specs[size] ))
#output all splits here
#Year;ISO3;GNFR_Sector;EC_fine;OC_fine;SO4_fine;Na_fine;OthMin_fine

#-size
#   iso3
#     gnfr
  sector_str='Sectors:'
  if 'gnfr' in label:
    sectors = dict( A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=10, K=11,
                    L=12, M=13, A1=14, A2=15, F1=16, F2=17, F3=18, F4=19)
    for code,num in sectors.items():
      sector_str += '%s=%s; ' % (num,code)
  else:
    sectors = range(1,12)
    sector_str = 'SNAPS 1-11'

  for size in sizes:

    #print('gnfrWWWW', size, emisFrac[size][isoDBG]['A'][0], \
    #     emisFrac[size]['ALB']['A1'][0], emisFrac[size][isoDBG]['A2'][0])
    #print('A5FMT'+iso3, 'A2', sfmt(emisFrac[size][iso3]['A2']))
    if size=='fine':   osize='25' # why not from start?!
    if size=='coarse': osize='co'
    output = open(odir+'emissplit_specials_pm%s.csv' % osize, 'w' )
    output.write(header_str % ( # size, tnoref, label, src_code, today, sector_str, header_specs[size] ))
       size, codetxt.codetxt(__file__), header_specs[size]  ))
 
    poll = 'PM2_5'
    if size == 'coarse': poll = 'PMc'
    for iso3 in iso3s:  
      if iso3 == 'Total': continue
      emep   = int( emepcc[iso3]['cc'] )

      if iso3=='EUR': # defaults file
        output = open(odir+'emissplit_defaults_pm%s.csv' % osize, 'w' )
        output.write(header_str % ( #size, tnoref, label, src_code, today, sector_str, header_specs[size] ))
                   size, codetxt.codetxt(__file__), header_specs[size]  ))
        emep = 0

      for sec in sectors:
        if iso3==isoDBG:
            print("SEC",iso3, sec, size, emisFrac[size][iso3][sec] )
        
        if iso3=='EUR':
           print('EURTEST ', size, iso3, sec, np.sum(emisFrac[size][iso3][sec]) )
           if np.sum(emisFrac[size][iso3][sec]) < 0.001: 
              emisFrac[size][iso3][sec][-1] = 1.0  # Add fake remPPM
        print('XXX', size, iso3, sec, emisFrac[size][iso3][sec])
        if np.sum(emisFrac[size][iso3][sec]) < 0.001: continue
        if np.min(emisFrac[size][iso3][sec]) < 0.0: 
            print('NEGPM!!!', numRef, size, iso3, sec )
            print('NEGPM!!!', emisFrac[size][iso3][sec])
            sys.exit()
        #epolls='OMff,OMbio,ECff,ECbio,Na,SO4,OthMin'
        omff = emisFrac[size][iso3][sec][0]
        ombb = emisFrac[size][iso3][sec][1]
        ecff = emisFrac[size][iso3][sec][2]
        ecbb = emisFrac[size][iso3][sec][3]
        Na   = emisFrac[size][iso3][sec][4]
        so4  = emisFrac[size][iso3][sec][5]
        OthMin=emisFrac[size][iso3][sec][6]
 
        if use_so4:
          remPPM = Na+OthMin       # for CAMS
        else:
          remPPM = Na+so4+OthMin   # for EMEP
          so4 = 0.0
        sumPM = omff+ombb +ecff+ecbb +remPPM + so4
        if sec==2: print('ALBCA', sec, size, omff, ombb, ecff, ecbb, so4, OthMin, sumPM)
        if sumPM < 0.9999: continue

        isec=sec
        if 'gnfr' in label: isec=sectors[sec]
        if size == 'fine':
#       # want POM_f_ffuel EC_f_ffuel_new EC_f_ffuel_age  POM_f_wood
#       #   ...EC_f_wood_new EC_f_wood_age  remPPM25'  

          if iso3=='EUR': print('EURFINE ', size, iso3, sec, sumPM)
          # assume 80% new, 20% age for EC
          nspecs = len(header_specs['fine'].split(','))
          fmt = '%3d,%4s ' + ' ,%8.3f'*nspecs + '\n'
          #if use_so4: fmt = '%3d,%4s ' + ' ,%8.3f'*nspecs + '\n'
          if ResNonRes:
            #'POM_f_Res,POM_f_nonRes,EC_f_Res_new,EC_f_Res_age,EC_f_nonRes_new,EC_f_nonRes_age,remPPM25_Res,remPPM25_nonRes'  
            # emissums had alrady put all OM; EC into GNFR C
            remPPMnr=remPPM; remPPMres=0.0
            if isec==3:
               remPPMnr=0.0; remPPMres=remPPM
            if use_so4:
              print('FMT', fmt)
              print('N', nspecs)
              print('H', header_specs['fine'] )
              output.write( fmt % ( emep, isec, 100*ombb, 100*omff, 
               ecbb*80, ecbb*20, ecff*80, ecff*20, 100*remPPMres, 100*remPPMnr, 100*so4 )) 
            else:
              output.write( fmt % ( emep, isec, 100*ombb, 100*omff, 
               ecbb*80, ecbb*20, ecff*80, ecff*20, 100*remPPMres, 100*remPPMnr )) 
          else:
            #fmt = '%3d,%4s ' + ' ,%8.3f'*7 + '\n'
            sys.exit()
            output.write( fmt % ( emep, isec, 100*omff, 100*ombb, 
               ecff*80, ecff*20, ecbb*80, ecbb*20, 100*remPPM )) 

        else:
          nspecs = len(header_specs['coarse'].split(','))
          fmt = '%3d,%4s' + ',%8.3f'*nspecs + '\n'
          # 'POM_c_Res, POM_c_nonRes,  EC_c_Res, EC_c_nonRes, remPPM_c_Res,remPPM_c_nonRes'
          xPOM=100*(omff+ombb); xEC=100*(ecff+ecbb); xPPM=100*remPPM
          if ResNonRes:
            POMnr=xPOM;    POMres=0.0
            ECnr= xEC;     ECres=0.0
            remPPMnr=xPPM; remPPMres=0.0
            if isec==3:
               POMres=xPOM;      POMnr=0.0
               ECres =xEC;       ECnr=0.0
               remPPMres=xPPM;   remPPMnr= 0.0
            if use_so4:
              output.write( fmt % ( emep, isec, 
                POMres, POMnr, ECres, ECnr, remPPMres, remPPMnr, 100*so4  ))
            else:
              output.write( fmt % ( emep, isec, 
                POMres, POMnr, ECres, ECnr, remPPMres, remPPMnr  ))
          else:
            output.write( fmt % ( emep, isec, 
              100*(omff+ombb), 100*ecff, 100*ecbb, 100*remPPM ))
  return


#----------------------------------------------------------------------------

for numRef in numRefs:
  #for PMc_method in 'raw10 max1'.split():
  # emissums use gnfr label

  #2021 comment: label needed here to access pre-calculated emissums files.
  #emissums_gnfrRef2_yr2017_cams50_fakeECres_may2021_PMcoarse.csv
  #emissums_gnfrRef2_yr2017_cams50_fakeECres_may2021_PMfine.csv
  label = 'gnfr' # Ref%d_yr2017_cams50_fakeECres_may2021' % numRef
  #May2021: tnoref = 'gnfrRef%d_yr2017_cams50_fakeECres_may2021' % numRef
  tnoref = 'gnfrRef%s_yr2018_cams50_jan2022' % numRef
  #if ResNonRes:
  #  tnoref = 'gnfrRef%f_yr2017_CAMS-REG-AP_v4_2_may2021' % numRef
  iso3s, gnfrFrac, snapFrac = process_emissums(numRef,tnoref,dbg=True)
  rnr=''
  if ResNonRes: rnr='_rnr'
  odir='./emissplits_%s/' % label
  odir += 'CAMS-REG-v5_1_with_Ref%s_year2018_DT%s/' % ( numRef, rnr )  # eg emissplits_gnfr/CAMS-REG-AP_v2.2.1_2015_REF1
  #if ResNonRes:
  #  tnoref=tnoref + '_rnr' #MAY2021:'CAMS-REG-AP_v4_2_yr2017_REF2_1'
  #  odir='./emissplits_%s/%s/' % ( label, tnoref)  # eg emissplits_gnfr/CAMS-REG-AP_v2.2.1_2015_REF1
  #odir='TESTDIRS/'  # NOTE / essential!!!!
  os.makedirs(odir,exist_ok=True)

  s1=write_emislist(numRef,iso3s,tnoref, gnfrFrac,'gnfr',dbg=False)
  #2021: label = 'snapRef%d_yr2015_jun2020' % numRef
  # s2=write_emislist(numRef,iso3s, snapFrac,'snap',dbg=False)

#Jan2022: emissums_gnfrRef2_yr2018_cams50_jan2022_PMcoarse.csv emissums_gnfrRef2_yr2018_cams50_jan2022_PMfine.csv
