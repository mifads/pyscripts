#!/usr/bin/env python3
"""
  Reads TNO CAMS format emission file and converts to EMEP netcdf
  Updated Feb 2022 for new-style netcdf, and flexible keys
  Updated Nov 2019 for new sector possibilities
  previous:  July 2017
  From  NMR-RWC, reads file such as :
Lon;Lat;ISO3;Year;GNFR_Sector;SourceType;EC_coarse;OC_coarse;SO4_coarse;Na_coarse;OthMin_coarse;EC_fine;OC_fine;SO4_fine;Na_fine;OthMin_fine
-4.250000000;48.025000000;FRA;2015;Cf;A;3.258181162;0.183700710;0.000000000;0.211288887;17.475717960;15.773615404;44.312587775;0.609503468;0.116269231;29.658024453
14.750000000;41.325000000;ITA;2015;Cf;A;0.185477034;0.000000000;0.000000000;0.003279270;0.139170701;0.576266359;2.241383583;0.088344069;0.041452721;1.197825403
"""
import argparse
from collections import OrderedDict as odict
import logging
import os
import sys
import numpy as np
import pandas as pd

import emxemis.cams_emep_codes as m
import emxemis.camsSectorTables as camstabs
import emxmisc.codetxt as codetxt
from   emxmisc.numberfunctions import nicefloat as nf
import emxcdf.makecdf as cdf

tmpx = 0.0

Usage="""
  Usage:
     cams2emep.py tno_emission_file   label   [-x]
  e.g.
     cams2emep.py TNO_MACC_III_emissions_v1_1_2011.txt  MACC_III_emissions_v1_1_2011

  where -x triggers the use of detailed snaps, eg 22, 74
"""

parser = argparse.ArgumentParser()
parser.add_argument('-i','--ifile',help='TNO-style emissions file, semicolon separated')
parser.add_argument('-l','--label',help='label for output, e.g. Cb') # CAMS3p1')
parser.add_argument('-s','--style',help='Style of TNO input file, e.g. cams3p1, NMR-RWC')
parser.add_argument('-log', '--loglevel', type=str, choices= ['DEBUG','INFO','WARNING','ERROR','CRITICAL'], help='Set the logging level')
args=parser.parse_args()

logger = logging.getLogger()
logging.basicConfig(level=args.loglevel)
logger.info('INFO args: '+ str(args))
logger.warning('WARN args: '+ str(args))
extraSnaps=False

extraSnaps = True # TMP
pollmap = dict(
  EC_coarse = 'EC_c',  OC_coarse='OC_c',
  EC_fine='EC_f',      OC_fine='OC_f',
  remPPM25='remPPM25', remPPMc = 'remPPMc',
  SO4_coarse='pSO4',   SO4_fine='SO4' )

if not os.path.exists(args.ifile): sys.exit('Error!\n File does not exist: '+args.ifile)

#1) emepcodes: e.g. FIN ->  {'cc': '7', 'iso2': 'FI', 'iso3': 'FIN', 'name': 'Finland'}),

emepcodes = m.get_emepcodes()
logger.debug('INFO emepcodes: '+ str(emepcodes))


# 2)  Emissions
# TNO emissions 2017-ish:
#Lon;Lat;ISO3;Year;SNAP;SourceType;CH4;CO;NH3;NMVOC;NOX;PM10;PM2_5;SO2
#-29.937500;36.406250;ATL;2011;8;A;0.000000;0.063392;0.000000;0.018761;0.634203;0.048957;0.046509;0.417624
# CAMS Nov 2019:
#Lon_rounded;Lat_rounded;ISO3;Year;GNFR_Sector;SourceType;CH4;CO;NH3;NMVOC;NOX;PM10;PM2_5;SO2
#-29.950000000;60.025000000;ATL;2016;G;A;0.000000000;5.658706000;0.000000000;0.810892000;107.728119000;8.422509000;8.422509000;65.927017000

# MACC-III style SNAPs, with merged 3+4, split 7
style='maccIII'
style='cams3p1'
extended=''
if style=='maccIII':
  snaps = (1,2,21,22,3,34,5,6,7,71,72,73,74,75,8,9,10) # 74 was zero   # Can be more than used
  ipoll0 = 6  # CH4 col
  seclabel = 'snap'
elif ( style=='cams3p1' or style=='NMR-RWC') :
  sectorcodes, sectornames = camstabs.getCams2emep() # gets e.g ['F3'] = 18
  extraSnaps=True
  ipoll0 = 6  # CH4 col
  seclabel = 'gnfr'
else:
  sys.exit('SET STYLE?')
if extraSnaps==True: extended='_ext'

df=pd.read_csv(args.ifile,sep=";")

# merge to remPPM:
df['remPPM25'] = df.Na_fine + df.OthMin_fine
df['remPPMc']  = df.Na_coarse + df.OthMin_coarse
df.drop(['Na_fine',   'OthMin_fine'],axis=1,inplace=True)
df.drop(['Na_coarse', 'OthMin_coarse'],axis=1,inplace=True)
df['GNFR_Sector'] = 'C'  # from Cb, Cf, C

bfile='tmpnmr'+os.path.basename(args.ifile)
df.to_csv(bfile,index=False,sep=";")  # tmp output as csv

dflons=np.sort( df.Lon.unique() )
dflats=np.sort( df.Lat.unique() )
countries = df.ISO3.unique()
print(df.keys())
dx= nf(dflons[1] - dflons[0])
dy= nf(dflats[1] - dflats[0])
print('DFLONS', min(dflons), max(dflons), dflons[1] - dflons[0], dx )
print('DFLATS', min(dflats), max(dflats), dflats[1] - dflats[0], dy )

polls= list( df.keys() )
for i in 'Lon Lat ISO3 Year GNFR_Sector SourceType'.split():
  if i in polls: polls.remove(i)
print('POLLS', polls)
for poll in polls:
  assert poll in  pollmap, 'Missing POLL%s' % poll

#polls = 'CH4 CO NH3 NMVOC NOX PM10 PM2_5 SO2'.split()  # TNO  style
#epolls= 'ch4 co nh3   voc nox pmco pm25 sox'.split()   # EMEP style

# HARD CODE
lon0= nf(dflons[0]); lon1=nf(dflons[-1])      # :MACCIII_from_A 59.9375
lat0= nf(dflats[0]); lat1=nf(dflats[-1])     # :MACCIII_from_A 59.9375

xmin= nf(lon0 - 0.5*dx)    # left edge, here -30
xmax= nf(lon1 + 0.5*dx)    # right edge, here 60.125
ymin= nf(lat0 - 0.5*dy)    # bottom edge, here 30.0  
ymax= nf(lat1 + 0.5*dy)    # top edge, here 72.0
nlons= int( (xmax-xmin)/dx )  
nlats= int( (ymax-ymin)/dy ) 
lons=np.linspace(lon0,lon0+(nlons-1)*dx,nlons) # Ensure 100% uniform
lats=np.linspace(lat0,lat0+(nlats-1)*dy,nlats) # Ensure 100% uniform
print( 'Lon', xmin, dx, xmax, len(lons), 'tmpdx:', lons[1]-lons[0], lons[0], lons[-1])
print( 'Lat', ymin, dy, ymax, len(lats), 'tmpdy:', lats[1]-lats[0])

idbg=316; jdbg=416 # DK

globattrs={
                'Conventions': "CF-1.0" ,
                'projection': "lon lat" ,
                'Grid_resolution': "0.1" ,
                'Created_by': codetxt.codetxt(__file__),  # will add script and date
                'Data_from': "TNO, J. Kuenen, Jan 2022",
                'MSC-W_Contact': "David Simpson",
                'Sector_names': "GNFR_CAMS" ,
                'sec01': "A_publicpower" ,
                'sec02': "B_industry" ,
                'sec03': "C_otherstationarycomb" ,
                'sec04': "D_fugitive" ,
                'sec05': "E_solvents" ,
                'sec06': "F_roadtransport" ,
                'sec07': "G_shipping" ,
                'sec08': "H_aviation" ,
                'sec09': "I_offroad" ,
                'sec10': "J_waste" ,
                'sec11': "K_agrilivestock" ,
                'sec12': "L_agriother" ,
                'sec13': "M_other" ,
                'sec14': "A1_PublicPower_Point",
                'sec15': "A2_PublicPower_Area",
                'sec16': "F1_RoadTransportExhaustGasoline",
                'sec17': "F2_RoadTransportExhaustDiesel",
                'sec18': "F3_RoadTransportExhaustLPGgas",
                'sec19': "F4_RoadTransportNonExhaust",
                'periodicity': "yearly" ,
}


all_polls = True  # produce file with all polls
if all_polls:
  xrarrays=[] #
for poll in polls:

#  if 'OC_f' not in poll: continue
  if not all_polls:
    xrarrays=[] #

  sectemis = dict()
  SumEmis  =  np.zeros([ len(lats),len(lons) ])
  sums     = dict()       # Not used

  sectsums = dict.fromkeys(sectorcodes.keys(),0.0)
  #print(poll, sectsums)

   # nov2019. Tried this, but it kills my PC memory
   # xx=np.genfromtxt(ifile,delimiter=';',names=True,dtype=None)
   # for n in range(len(xx)): # with open(ifile) as f:
   #Lon_rounded;Lat_rounded;ISO3;Year;GNFR_Sector;SourceType;CH4;CO;NH3;NMVOC;NOX;PM10;PM2_5;SO2
  sect_label = 'GNFR_Sector'  # or 'SNAP'
  
  for index, row in df.iterrows():
    iso3 = row.ISO3
    if iso3 not in sums.keys():
       sums[iso3] = dict()  # np.zeros(11)
       sums[iso3]['tot'] = 0.0
       for sect in sectorcodes: sums[iso3][str(sect)] = 0.0
    iso2=emepcodes[iso3]['iso2']
    lon = row.Lon
    lat = row.Lat
    #jix  = int( (lon-xmin)/dx )
    #jiy  = int( (lat-ymin)/dy )
    ix  = int( 10*(lon-xmin) )
    iy  = int( 10*(lat-ymin) )
    if ix > nlons-1 or iy > nlats-1:
       print('OOPS', lon, lat, iso3, ix, iy)
       sys.exit()
    sect=row[sect_label]

    #logger.debug('OUPUT'+sect)
    #logger.info('INFO'+sect)

    if style == 'cams3p1' or style == 'NMR-RWC':
      if sect=='A':
       if row.SourceType=='P': sect= 'A1'
       if row.SourceType=='A': sect= 'A2'

#ABC# exclude aviation and waste
#ABC# elif fields[5]=='P' & not ( sect == 'H' or sect == 'J') : sys.exit('NEW POINT')
    isect = sectorcodes[sect]
    vtot = '%s_%s_sec%2.2d'% ( 'tot', pollmap[poll], isect) 
    if vtot not in sectemis.keys():
      sectemis[vtot] =  np.zeros([ len(lats),len(lons) ])

    if not extraSnaps:
       if isect > 12 : isect = isect // 10  # 21 to 2, 34 to 3,  etc

    x = row[poll]

    if x > 0.0:
       #print('SS ', sectsums )
       #print('IS ', isect, sectsums.keys() )
      sectsums[sect]    +=  x
      sums[iso3][sect]  += x
      sums[iso3]['tot'] += x

      v = '%s_%s_sec%2.2d'% ( iso2, pollmap[poll], isect) 
      #print(sect, isect, x, v)
      if v not in sectemis.keys():
         sectemis[v] =  np.zeros([ len(lats),len(lons) ])
         #print('VV', v, sectemis.keys())

      sectemis[v][iy,ix] += x
      sectemis[vtot][iy,ix] += x
      #if abs(lon-17.65) < 0.001 and ( 45 < lat < 50 ):
      #  print('LLAT ',v,lon,lat, ymin, 10*(lat-ymin), iy, x, sectemis[vtot][iy,ix])

  #print('ENDKEYS ', v, iso3, poll, sectemis.keys() )
  for v in sectemis.keys():
    fields=v.split('_')
    iso2=fields[0]
    sec=fields[-1]
    sec=int( sec.replace('sec','') )
    # in loop: poll=fields[1:-1]
    print('ENDING ', iso2, sec, poll,  v, np.sum(sectemis[v]), type( sectemis[v] ) )

    if np.sum(sectemis[v]) > 0.0:
      xrarrays.append(dict(varname=v, dims=['lat','lon'],
       attrs = {'units':'tonnes/year','country_ISO':iso2,'species':poll,'sector':'%d'%sec},
       coords={'lat':lats,'lon':lons},data=sectemis[v].copy() ) )

  # end of poll:
  if not all_polls:
    xrout =  cdf.create_xrcdf(xrarrays,globattrs=globattrs,outfile='xxnmrTnoEmis%s_%s.nc' % ( poll, args.label) ,skip_fillValues=True)
if all_polls:
  ofile='nmr'+os.path.basename(args.ifile).replace('.csv','.nc')
  xrout =  cdf.create_xrcdf(xrarrays,globattrs=globattrs,outfile=ofile,skip_fillValues=True)
  #xrout =  cdf.create_xrcdf(xrarrays,globattrs=globattrs,outfile='xxnmrTnoEmis%s_%s.nc' % ( 'polls', args.label) ,skip_fillValues=True)
#  sys.exit()


if __name__ == '__main__':

  logging.basicConfig(level=logging.DEBUG)
