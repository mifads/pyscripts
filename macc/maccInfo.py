#!/usr/bin/env python3
"""
  Reads TNO MACC format emission file and stores info as maccInfo
  giving e.g. maccInfo['Emis:LUX']['nox'][7]
  SNAP 71: Road transport exhaust emissions, gasoline

  NB TNO use:
   SNAP 71: Road transport exhaust emissions, gasoline
   SNAP 72: Road transport exhaust emissions, diesel
   SNAP 73: Road transport exhaust emissions, other fuels
   SNAP 74: Road transport non-exhaust emissions, evaporation of gasoline
   SNAP 75: Road transport non-exhaust emissions, road, brake and tyre wear

"""
#  July 2017
from collections import OrderedDict as odict
import os
import sys
import numpy as np

import macc.maccEmepCodes as m


maccInfo = odict()

#1) emepcodes: 
# e.g. FIN ->  {'cc': '7', 'iso2': 'FI', 'iso3': 'FIN', 'name': 'Finland'}),

emepcodes = m.getMaccEmepCodes()    # e.g. 'FIN',


# 2)  Emissionsmep
#Lon;Lat;ISO3;Year;SNAP;SourceType;CH4;CO;NH3;NMVOC;NOX;PM10;PM2_5;SO2
#-29.937500;36.406250;ATL;2011;8;A;0.000000;0.063392;0.000000;0.018761;0.634203;0.048957;0.046509;0.417624
# MACC-III style SNAPs, with merged 3+4, split 7

snaps = (1,2,21,22,3,34,5,6,7,71,72,73,74,75,8,9,10) # 74 was zero   # Can be more than used

#polls = 'CH4 CO NH3 NMVOC NOX PM10 PM2_5 SO2'.split()  # TNO  style
#epolls= 'ch4 co nh3   voc nox pmco pm25 sox'.split()   # EMEP style
mpoll2epoll = dict( CH4='ch4', CO='co', NH3='nh3', NMVOC='voc', NOX='nox',
  PM10='pmco',  # SPECIAL!
  PM2_5='pm25', SO2='sox' )


def ReadMacc(ifile,dbgcc=None):
   minlon=999.; minlat=999.; maxlon=-999.; maxlat=-999.
   dtxt='RdMacc'

   nsnaps = dict.fromkeys(snaps,0.0)
   maccInfo = odict()

   with open(ifile) as f:
      for n, line in list(enumerate(f)):
        nline = line.strip('\n')
        fields = nline.split(';')
        if n==0:
           polls=fields[6:]
           epolls = [ mpoll2epoll[p] for p in polls]
           continue

        lon  = float(fields[0])
        lat  = float(fields[1])
        iso3 = fields[2]
        debug =  iso3==dbgcc

        cc2  = emepcodes[iso3]['iso2']
        snap = fields[4]  # str
        if snap == '34': snap = '3' # simple!
        isnap= int(snap)
        nsnaps[isnap] += 1

        minlon = min(minlon, lon)
        minlat = min(minlat, lat)
        maxlon = max(maxlon, lon)
        maxlat = max(maxlat, lat)

        for ipoll, poll in list( enumerate(epolls)): # EMEP poll names
           x = float( fields[ipoll+6] )
           if ipoll ==  5:
              x  = x- float( fields[ipoll+7] ) #PM10->PMco
              if x < 0.0: sys.exit('PMco NEG')

           if x > 0.0:
 
              v = 'Emis:%s'% iso3
              s = 'Sum:%s'% iso3
              if not v in maccInfo.keys():
                 maccInfo[v] = odict()
                 maccInfo[s] = odict()
                 for poll in epolls:
                    maccInfo[v][poll] = dict.fromkeys(snaps,0.0)
                    maccInfo[s][poll] = 0.0

              maccInfo[v][poll][isnap] += x
              maccInfo[s][poll]        += x

   #           if debug:
   #              print(dtxt+'DBG ', poll, cc2, snap, isnap, x, 
   #                 maccInfo[v][poll][isnap], maccInfo[s][poll] )
   if nsnaps[7] == 0:
     if debug:
        print(dtxt+'NSNAPS ', nsnaps.keys() )
        print(dtxt+'NSNAPS ', nsnaps )
     for v in maccInfo.keys(): # Only emissions so far, so okay:
        if v.startswith('Sum'): continue
        for poll in epolls:
            maccInfo[v][poll][7]  = 0.0
            for snap in [ 71, 72, 73, 74, 75 ]:
               maccInfo[v][poll][7]  += maccInfo[v][poll][snap]
               if debug: print(dtxt+'SNAP7 ', poll, snap, maccInfo[v][poll][7] )

   maccInfo['file']   = ifile
   maccInfo['domain'] = odict( lon0=minlon,lon1=maxlon,lat0=minlat,lat1=maxlat )
   maccInfo['maccpolls'] = polls
   maccInfo['emeppolls'] = epolls
   return  maccInfo


if __name__ == '__main__':

  Usage="""
    maccInfo.py  TNO_file.txt
  """
  try:
    if len(sys.argv) < 2: sys.exit('Error!\n' + Usage)
    ifile=sys.argv[1]
    if not os.path.exists(ifile): sys.exit('Error!\n File does not exist: '+ifile)
  except: # works for Dave ;-)

    ifile='/home/davids/Work/EU_Projects/CAMS/CAMS50/CAMS50_stallo/TNO_MACC_III_emissions_v1_1_2011.txt'
  m=ReadMacc(ifile,dbgcc='FRA')
  print(m['file'])
  print(m['domain'])
  print(m['Emis:FRA']['pm25'])
  print('France :\n',m['Sum:FRA']['pm25'])

