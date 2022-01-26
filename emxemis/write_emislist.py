#!/usr/bin/env python3
# was mkNMVOCsplits.py
import collections  # old python!
import numpy as np
import os
import emxmisc.auto_dicts       as ad
import emxemis.camsSectorTables as cs
import emxemis.cams_emep_codes as ce
#import emxemis.normaliseEmisSplits as ne
#import pandas as pd
import sys

isoDBG='ARM'

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
cctab = ce.get_emepcodes() # cctab['ALB']['cc'] = '1'

# 1)  Get sector mapping:
# cams3p1_table = """# Nov 2019
# emep  cams_code snap  cams_long
#  1        A        1  A_PublicPower
#..

camstab = cs.camstab() # ARGH - too many!
tnoAP_to_19 = cs.tnoAPmapping()  #  tnoAP_to_19['A:P'] Returns A2
camssecs = camstab['tnosec']
print('keys ', tnoAP_to_19.keys())  # A:A, A:P, ...
print('vals ', tnoAP_to_19.values()) # A1, A2 .
print('cams ', camssecs) # tab['tnosec']) # A B C .. A1 .F1..

#-----------------------------------------------------------------------------
def write_emislist(emisFrac,emepUsed,header=None,label='TEST'):

  header_last="""
# Key-word, MASS_ASSUMED= 0 by default,
# change when emissions have artificial mass, e.g. 46 for NOx as NO2
: MASS_ASSUMED 0
"""
  if header==None:
    emislist_header="""# VOC splits for %s sectors and EmChem19a
# A=1;B=2;C=3;D=4;E=5;F=6;G=7;H=8;I=9;J=10;K=11;L=12;M=13;A1=14;A2=15;F1=16;F2=17;F3=18;F4=19
# F1-F4 splits for road traffic and K-L for agriculture from CAMS-REG-AP_v2.2.1 for 2015
# created by camsmakeNMVOCsplits.py Jun 2020 and earlier mkEC19emissplitMCM.py.
# Maps TNO/CAMS 25-compounds (v01...) from CAMS-REG-v3_1_2 matrix to EmChem species
# Note - two changes to keep C5H8 and terpenes as BVOC only:
#  moved trace amounts of apinene to 50%%  C2H4 and 50%% unreactive. 
#  moved trace amounts of isoprene to C2H4.""" % label   + header_last
  else:
    emislist_header = header + header_last

  sector_str='Sectors:'
  npolls = len(emepUsed)

  if 'gnfr' in label:
    sectors = dict( A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=10, K=11,
                    L=12, M=13, A1=14, A2=15, F1=16, F2=17, F3=18, F4=19)
    for code,num in sectors.items():
      sector_str += '%s=%s; ' % (num,code)
  else:
    sectors = range(1,12)
    sector_str = 'SNAPS 1-11'
    #print('DBGKLSNAP ', sfmt(emisFrac['ARM'][10]))

  out=open('emissplit_specials_%s_voc.csv'%label,'w')
  out.write(emislist_header)
  out.write('  99,  99,'+ ','.join('%9s'%x for x in emepUsed )+ \
               ', #HEADERS\n#DATA\n')

  for iso3 in emisFrac.keys(): #
    print('ZZISO ', iso3, sfmt(emisFrac[iso3][10])) # emisFrac[iso3].keys())
    if iso3== 'EurTot':
       out=open('emissplit_defaults_%s_voc.csv'%label,'w')
       out.write(emislist_header)
       out.write('  99,  99,'+ ','.join('%9s'%x for x in emepUsed )+ \
               ', #HEADERS\n#DATA\n')
       ccnum = 0
       emisFrac[iso3][11] = np.zeros(npolls)
       emisFrac[iso3][11][-1] = 100.0
       #continue # will do in defaults below
    else:
       ccnum = cctab[iso3]['cc']

    for sec in sectors:   # emisFrac[iso3].keys():
      if not isinstance(emisFrac[iso3][sec],np.ndarray):
         print('NO DATA ', iso3, sec, emisFrac[iso3][sec])
         continue
     
      isec= sec
      if 'gnfr' in label: isec=sectors[sec]
      if np.sum( emisFrac[iso3][sec] ) < 99.99: continue
      lhs = '%4s, %4s, '% ( ccnum, isec)
      rhs = ','.join('%.4f'%x for x in emisFrac[iso3][sec])
      out.write(lhs+rhs+'\n')
      print('ZZFRACSA', iso3, 's', sec, ' N:', isec)
  return

#-----------------------------------------------------------------------------

if __name__ == '__main__':

  emisFrac=ad.Vividict()

  import nmvoc_mapping as nm
  vmap = nm.get_vspecMap() #  or vmap['A']['v01']['esplit'] = [..]
  print('VMAP', vmap['emepUsed'])

  npolls = len(emepUsed)
  emisFrac['SWE'][1] = np.zeros(npolls)
  emisFrac['SWE'][1][0] = 100.0
  emisFrac['SWE'][2] = np.zeros(npolls)
  emisFrac['SWE'][2][3] = 100.0

  w = write_emislist(emisFrac,emepUsed,label='MYTEST')
