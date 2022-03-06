#!/usr/bin/env python3
"""
  Reads TNO CAMS format emission file (units kg/cell) and converts to EMEP netcdf
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
parser.add_argument('-o','--ofile',help='Outut netcdf file')
parser.add_argument('-l','--label',help='label for output, e.g. scen1') # CAMS3p1')
parser.add_argument('-s','--style',help='Style of TNO input file, e.g. cams3p1, NMR-RWC')
parser.add_argument('--csv',help='Output interim csv (large!)')
parser.add_argument('-log', '--loglevel', type=str, choices= ['DEBUG','INFO','WARNING','ERROR','CRITICAL'], help='Set the logging level')
args=parser.parse_args()

assert 'sm_davsi' in os.environ['HOME'], 'Probably need to run on nebula!' 
logger = logging.getLogger()
logging.basicConfig(level=args.loglevel)
logger.info('INFO args: '+ str(args))
logger.warning('WARN args: '+ str(args))
extraSnaps=False

sect_label = 'GNFR_Sector'  # or 'SNAP'
extraSnaps = True # TMP
compact_polls=True
dbg=False
if compact_polls:
  # skip coarse POM_c_wood (<0.6% of POM_f), and no fuel tag on remPPM
  pollmap = dict(
    EC_coarse  ='EC_c_TAG',     OC_coarse='POM_c_TAG',  # still _c_ tag here
    EC_fine    ='EC_f_TAG_new', OC_fine='POM_f_TAG',  # ONLY have new so far!
    remPPM25   ='remPPM25',     remPPMc = 'remPPMc',
    SO4_coarse ='pSO4c',        SO4_fine='pSO4f' )
else:
  pollmap = dict(
    EC_coarse  ='EC_c_TAG',     OC_coarse='POM_c_TAG',
    EC_fine    ='EC_f_TAG_new', OC_fine='POM_f_TAG',  # ONLY have new so far!
    remPPM25   ='remPPM25_TAG', remPPMc = 'remPPMc_TAG',
    SO4_coarse ='pSO4c',        SO4_fine='pSO4f' )



def set_polltag(tagname,sect):
  """ We will replace TAG in tagname with e.g. Res, nonRes, ffuel, wood"""
  polltag = tagname
  if sect=='Cf': 
    polltag = polltag.replace('TAG','ffuel')
  elif sect=='Cb': 
    polltag = polltag.replace('TAG','wood')
  elif sect=='C': 
    polltag = polltag.replace('TAG','ffuel') # Default to ffuel
  else:
    sys.exit('POLLTAG'+polltag )
#    polltag = polltag.replace('TAG','nonRes')
  return polltag

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
  seclabel = 'snap'
elif ( style=='cams3p1' or style=='NMR-RWC') :
  gnfr2num, gnfr2name = camstabs.getCams2emep() # gets e.g ['F3'] = 18
  gnfr2num['Cf'] = gnfr2num['C']
  gnfr2num['Cb'] = gnfr2num['C']
  extraSnaps=True
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

if args.csv is not None:
  csvfile='tmpnmr'+os.path.basename(args.ifile)
  df.to_csv(csvfile,index=False,sep=";")  # tmp output as csv

dflons=np.sort( df.Lon.unique() )
dflats=np.sort( df.Lat.unique() )
countries = df.ISO3.unique()
print(df.keys())
dx= nf(dflons[1] - dflons[0])
dy= nf(dflats[1] - dflats[0])
print('DFLONS', min(dflons), max(dflons), dflons[1] - dflons[0], dx )
print('DFLATS', min(dflats), max(dflats), dflats[1] - dflats[0], dy )

polls= list( df.keys() )
for i in 'Lon Lat ISO3 Year SourceType'.split():
  if i in polls: polls.remove(i)
polls.remove(sect_label) # Mar4
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

#MV   'Grid_resolution': "0.1" , # should have been in meters, not 0.1
globattrs={
                'Conventions': "CF-1.0" ,
                'projection': "lon lat" ,
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


sumsectemis = dict()
sectemis = dict()  # Need to place outside poll loop if we want to add e.g. c to f
all_polls = True  # produce file with all polls
if all_polls:
  xrarrays=[] #
for poll in polls:

  #DBG if 'OC_f' not in poll: continue
  if not all_polls:
    xrarrays=[] #

  #SumEmis  =  np.zeros([ len(lats),len(lons) ])
  sums     = dict()       # Not used

   # nov2019. Tried this, but it kills my PC memory
   # xx=np.genfromtxt(ifile,delimiter=';',names=True,dtype=None)
   # for n in range(len(xx)): # with open(ifile) as f:
   #Lon_rounded;Lat_rounded;ISO3;Year;GNFR_Sector;SourceType;CH4;CO;NH3;NMVOC;NOX;PM10;PM2_5;SO2
  
  for index, row in df.iterrows():
    #if dbg and index>2000: break
    #if index>5000: break
    iso3 = row.ISO3
    if iso3 not in sums.keys():
       sums[iso3] = dict()  # np.zeros(11)
       sums[iso3]['tot'] = 0.0
       for sect in gnfr2num: sums[iso3][str(sect)] = 0.0
    iso2=emepcodes[iso3]['iso2']
    #if iso2 != 'NL': continue  #  index>200: break
    sect=row[sect_label]
    isect   = gnfr2num[sect]
    lon = row.Lon
    lat = row.Lat
    ix  = int( (lon-xmin)/dx )
    iy  = int( (lat-ymin)/dy )
    if ix > nlons-1 or iy > nlats-1:
       print('OOPS', lon, lat, iso3, ix, iy)
       sys.exit()

    #logger.debug('OUPUT'+sect) #logger.info('INFO'+sect)

    if style == 'cams3p1' or style == 'NMR-RWC':
      if sect=='A':
       if row.SourceType=='P': sect= 'A1'
       if row.SourceType=='A': sect= 'A2'

#ABC# exclude aviation and waste
#ABC# elif fields[5]=='P' & not ( sect == 'H' or sect == 'J') : sys.exit('NEW POINT')

    polltag = set_polltag(pollmap[poll],sect)  # replace TAG with e.g. wood
    vtot = '%s_%s_sec%2.2d'% ( 'tot', polltag, isect) 
    if vtot not in sectemis.keys():
      sectemis[vtot] =  np.zeros([ len(lats),len(lons) ])

    if not extraSnaps:
       if isect > 12 : isect = isect // 10  # 21 to 2, 34 to 3,  etc

    x = row[poll]

    if x > 0.0:

      sums[iso3][sect]  += x
      sums[iso3]['tot'] += x

      v = '%s_%s_sec%2.2d'% ( iso2, polltag, isect)  # replace TAG with Res
      if dbg and 'POM_c' in v: print('V:', sect, isect, x, v, polltag)
      if compact_polls and 'POM_c_wood' in v:
          v=v.replace('POM_c_wood','POM_f_wood')
      if v not in sectemis.keys():
         sectemis[v] =  np.zeros([ len(lats),len(lons) ])
         if v not in sumsectemis.keys():
           sumsectemis[v] = 0.0

      sectemis[v][iy,ix] += x
      sectemis[vtot][iy,ix] += x
      #if abs(lon-17.65) < 0.001 and ( 45 < lat < 50 ):
      #  print('LLAT ',v,lon,lat, ymin, 10*(lat-ymin), iy, x, sectemis[vtot][iy,ix])

  # ====  end of rows input 

for v in sectemis.keys():   # '%s_%s_sec%2.2d'% ( iso2, polltag, isect)  # replace TAG with Res
    fields=v.split('_')
    iso2, rem = v.split('_',1) # =fields[0], rem is e.g. EC_c_ffuel_sec03
    species=v.removeprefix('%s_' % iso2 )
    species=species.removesuffix('_sec03' )
    #TEST if iso2 =='RU': iso2= 'XYZRUSSIA'
    #sec=np.int32( sec.replace('sec','') )  # No need for long integer (LL in ncdump)
    sec=np.int32(3)     # HARD-CODED SECT "C" , use np.int32 for netcdf
    # in loop: poll=fields[1:-1]
    # output finals as ktonne (input in kg)
    #print('ENDING %4s %d %12s   %20s %12.3f' % (iso2, sec, poll,  v, 1.0e-6*np.sum(sectemis[v]) ) ) #, type( sectemis[v] ) )
    #print('SUM (t) %4s %d %-12s  %-25s %12.3g' % (iso2, sec, poll,  v, 1.0e-6*np.sum(sectemis[v]) ) ) #, type( sectemis[v] ) )
    sumsectemis[v] =  np.sum(sectemis[v])
    print('SUM (t) %-25s %12.3f' % (v,  1.0e-6*sumsectemis[v] ) ) #, type( sectemis[v] ) )

    if np.sum(sectemis[v]) > 0.0:
      attrs = {'units':'kg/year','country_ISO':iso2,
       'species':species,'sector':sec}
      if iso2 =='tot': attrs={'units':'kg/year','sector':sec}

      xrarrays.append(dict(varname=v, dims=['lat','lon'],
       attrs = attrs,
       coords={'lat':lats,'lon':lons},data=sectemis[v].copy() ) )
      #xx= {'units':'kg/year','country_ISO':iso2, 'species':set_polltag(pollmap[poll],'C'),'sector':'%d'%sec} # HARD-CODED SECT

      # === add levo. Use zero for SP, 0.1 * DT for DT. Then process diff file along with CPOA
      if 'POM_f_wood' in v:
         attrs['species'] = 'Levo'       
         if '_SP_' in args.ifile:
            vals = np.zeros([ len(lats),len(lons) ])
         else:
            vals = 1/13.0 * sectemis[v]   # OC/OM = 1/1.3, Levo/OC = 0.1
         print('LEVO', v, np.max(vals) )
         xrarrays.append(dict(varname=v.replace('POM_f_wood','Levo'), dims=['lat','lon'],
           attrs = attrs,
           coords={'lat':lats,'lon':lons},data=vals ) )
   

      print('TABOUT: %-10s' % iso2,end='')
      for p in pollmap.keys():
         for sect in 'Cb Cf'.split(): # 'wood ffuel Res nonRes'.split(): # C is now same as Cf
           v = '%s_%s_sec%2.2d'% ( iso2, set_polltag(pollmap[p],sect), isect)
           if v in sectemis.keys():
              print('   %-25ss%10.3g' % ( v, np.sum(sectemis[v])  ), end='' )
      print() # gives newline


  # end of poll:
#  if not all_polls:
#    xrout =  cdf.create_xrcdf(xrarrays,globattrs=globattrs,outfile='Mar5nmrTnoEmis%s_%s.nc' % ( poll, args.label) ,skip_fillValues=True)
if all_polls:
  if args.ofile is None:
    ofile='nmr'+os.path.basename(args.ifile).replace('.csv','.nc')
  else:
    ofile= args.ofile
  xrout =  cdf.create_xrcdf(xrarrays,globattrs=globattrs,outfile=ofile) # ,skip_fillValues=True)

#  EC_coarse  ='EC_c_TAG',     OC_coarse='POM_c_TAG',
#  EC_fine    ='EC_f_TAG_new', OC_fine='POM_f_TAG',  # ONLY have new so far!
#  remPPM25   ='remPPM25_TAG', remPPMc = 'remPPM_c_TAG',
#  SO4_coarse ='pSO4c',          SO4_fine='pSO4f' )
#SKIPfor iso3 in countries:
#SKIP    iso2=emepcodes[iso3]['iso2']
#SKIP    for p in 'EC POM remPPM pSO4'.split():
#SKIP      if iso2=='NL': print('XRATIO POLL', p)
#SKIP      for fuel in 'wood ffuel'.split():
#SKIP        if compact_polls and p=='POM' and fuel == 'wood': continue
#SKIP        vf= '%s_%s_f_%s_sec03' % ( iso2, p, fuel )
#SKIP        if p=='remPPM': vf= vf.replace("_f_","25_")
#SKIP        if p=='pSO4':   vf= vf.replace("_f_wood","f_")
#SKIP        if p=='EC':     vf= vf.replace("sec03","new_sec03")
#SKIP        vc= '%s_%s_c_%s_sec03' % ( iso2, p, fuel )
#SKIP        if p=='remPPM': vc= vc.replace("_c","c")
#SKIP        if p=='pSO4':   vc= vc.replace("_c_wood","c_")
#SKIP        if iso2=='NL':
#SKIP            print('XRATIO FUEL', fuel, vf, vc)
#SKIP            print('XRATIO SS', sumsectemis[vf] )
#SKIP        if vf in sumsectemis:
#SKIP          if sumsectemis[vf] > 0.0:
#SKIP            if vc not in sumsectemis: sumsectemis[vc] = -1.0e-99
#SKIP            print('ratio? ', vf, sumsectemis[vf], sumsectemis[vc] )
#SKIP            #txt='%s_%s_%s' % ( iso2, poll, fuel )
#SKIP            print('RATIO %-3s Poll%s Fuel%s %12.5f pcnt' % ( iso2, p, fuel,  100*sumsectemis[vc]/ sumsectemis[vf]) )

if __name__ == '__main__':

  logging.basicConfig(level=logging.DEBUG)
