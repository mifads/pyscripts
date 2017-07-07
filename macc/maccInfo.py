#!/usr/bin/env python3
"""
  Reads TNO MACC format emission file and stores info as MaccInfo
  giving e.g. maccInfo['Emis:LUX']['nox'][7]
"""
#  July 2017
from collections import OrderedDict as odict
import os
import sys
import numpy as np

import macc.MaccEmepCodes as m


MaccInfo = odict()

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


def ReadMacc(ifile,dbg=False):
   minlon=999.; minlat=999.; maxlon=-999.; maxlat=-999.

   nsnaps = dict.fromkeys(snaps,0.0)
   maccInfo = odict()

   with open(ifile) as f:
      for n, line in list(enumerate(f)):
        nline = line.strip('\n')
        fields = nline.split(';')
        if n==0:
           polls=fields[6:]
           epolls = [ mpoll2epoll[p] for p in polls]
           maccInfo['maccpolls'] = polls
           maccInfo['emeppolls'] = epolls
           continue

        lon  = float(fields[0])
        lat  = float(fields[1])
        iso3 = fields[2]
        cc2  = emepcodes[iso3]['iso2']
        snap = fields[4]  # str
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
              if not v in maccInfo.keys():
                 maccInfo[v] = odict()
                 for poll in epolls:
                    maccInfo[v][poll] = dict.fromkeys(snaps,0.0)

              maccInfo[v][poll][isnap] += x

              if dbg and  iso3 == 'LUX':
                 print('DBG ', poll, cc2, snap, isnap, x, maccInfo[v][poll][isnap] )
   if nsnaps[7] == 0:
     if dbg:
        print('NSNAPS ', nsnaps.keys() )
        print('NSNAPS ', nsnaps )
     for v in maccInfo.keys():
        for poll in epolls:
            maccInfo[v][poll][7]  = 0.0
            for snap in [ 71, 72, 73, 74, 75 ]:
               maccInfo[v][poll][7]  += maccInfo[v][poll][snap]
         #      if iso3 == 'LUX': print('SNAP7 ', poll, snap, maccInfo
   maccInfo['file']   = ifile
   maccInfo['domain'] = odict( lon0=minlon,lon1=maxlon,lat0=minlat,lat1=maxlat )
   return  maccInfo


if __name__ == '__main__':

  Usage="""
    maccInfo.py  TNO_file.txt
  """
  if len(sys.argv) < 2: sys.exit('Error!\n' + Usage)
  ifile=sys.argv[1]
  if not os.path.exists(ifile): sys.exit('Error!\n File does not exist: '+ifile)

  # ifile='../CAMS50_stallo/TNO_MACC_III_emissions_v1_1_2011.txt'
  x=ReadMacc(ifile)
  print(x['file'])
  print(x['domain'])
  print(x['Emis:LUX']['nox'])

