#!/usr/bin/env python3
"""
  Reads TNO MACC format emission file and stores as camsInfo
  giving e.g. camsInfo['Emis:LUX']['nox']['A2:P']
  Updated Nov 2019 for new sector possibilities, and to use pandas
  previously maccInfo:  July 2017
"""
from collections import OrderedDict as odict
import copy
import os
import pandas as pd
import sys
import numpy as np

Usage="""
  Usage:
     camsInfo.py tno_emission_file
  e.g.
     cams2Info.py TNO_MACC_III_emissions_v1_1_2011.txt

"""

camsInfo = odict()

# 2)  Emissions
# TNO emissions 2017-ish:
#Lon;Lat;ISO3;Year;SNAP;SourceType;CH4;CO;NH3;NMVOC;NOX;PM10;PM2_5;SO2
#-29.937500;36.406250;ATL;2011;8;A;0.000000;0.063392;0.000000;0.018761;0.634203;0.048957;0.046509;0.417624
# CAMS Nov 2019:
#Lon_rounded;Lat_rounded;ISO3;Year;GNFR_Sector;SourceType;CH4;CO;NH3;NMVOC;NOX;PM10;PM2_5;SO2
#-29.950000000;60.025000000;ATL;2016;G;A;0.000000000;5.658706000;0.000000000;0.810892000;107.728119000;8.422509000;8.422509000;65.927017000
#    idbg=316; jdbg=416 # DK

polls = 'CO NH3 NMVOC NOX PM10 PM2_5 PMc SO2'.split()  # TNO  style, skip CH4
#polls = 'PM10 PM2_5'.split()  # TNO  style, skip CH4

def nicefloat(x):
  """ converts eg 0.09999999999787 to 0.1 """
  return float('%12.6f' % x)

def nicefloats(xlist):
  return [ nicefloat(x) for x in xlist ]

def src_name(sec_key, sec, typ):
  """ Returns compound name, e.g. A1:P.  If SNAP, use 2-digit sector name,
      e.g. 01:P """
  if sec_key == 'SNAP':
    return '%2.2d:%s' % (sec, typ)  #  could be int, e.g. 7, in SNsrc system
  else:
    return '%s:%s' % (sec, typ)  #  could be int, e.g. 7, in SNsrc system

def check_ranges(coords,txt):
  """ checks the lon or lat coordinates to find min and max spacing 
      since the values are sometimes irregular  """
  dmin= 999; dmax= -999
  for i in range(1,len(coords)):
    dcoord= coords[i]-coords[i-1]
    if dcoord < dmin: dmin=dcoord
    if dcoord > dmax: dmax=dcoord
  dcoord= coords[1]-coords[0] # Hopefully a good dx, dy guess
  print( txt, ' coords', nicefloats([ dcoord, coords[0], coords[-1], 
     coords[-1]-coords[0], (coords[-1]-coords[0])/dcoord, dmin, dmax ] ) )

def readCams(ifile,wanted_poll=None,get_vals=False,dbgcc=None):


    print('Reading %s;\n *** can take a while!' % ifile )
    df = pd.read_csv(ifile,sep=';')
    
    used_polls = polls
    if wanted_poll == 'PMc' or wanted_poll == 'PM':
      used_polls = 'PM2_5 PM10 PMc'.split()
    elif wanted_poll is not None:
      used_polls = [ wanted_poll, ]
    if wanted_poll == 'PM': wanted_poll = None # no longer needed

    if 'PMc' in used_polls and 'PMc' not in df.keys():
       print('PM is wanted: special handling for PMc' )
       df['PMc'] =  df['PM10'] - df['PM2_5']
    elif wanted_poll is not None: 
       assert wanted_poll in df.keys(), '!! POLL not found: ' + wanted_poll

    print('KEYS', wanted_poll, df.keys() )

    # 1-d fields:
    lonList    = df.iloc[:,0].values
    latList    = df.iloc[:,1].values
    iso3List   = df.ISO3.values
    sec_key    = df.keys()[4]   # eg GNFR_Sector or SNAP
    typ_key    = df.keys()[5]   #  SourceType A or P
    secList    = df[sec_key].values
    typList    = df.SourceType.values
    iso3s = np.unique(iso3List)
    iso3s = np.append(iso3s,'Total')
    if dbgcc is not None: print(iso3s)
    
    sectors = sorted( df[sec_key].unique() )
    types   = sorted( df[typ_key].unique() )
    srcs = []
    for sec, typ in zip( secList, typList ):
       srcs.append( src_name( sec_key, sec, typ) )

    srcs = np.unique(srcs)  #  np unique also sorts
    print('Zipped list from sec_key, typ_key', srcs, len(srcs) )

   # Find lon/lat ranges and dimensions
   # look for max and min, BUT tno spacings are not always regular
   # Hopefully the distance 0 to 1 is
    lons = np.unique( lonList ) # Unique list, sorted W to E
    lats = np.unique( latList ) # Unique list, sorted S to N 

    dx  = nicefloat( lons[1]  - lons[0] )
    dy  = nicefloat( lats[1]  - lats[0] )

    xmin= nicefloat( lons[0]  - 0.5*dx  )  # left edge, here -30
    xmax= nicefloat( lons[-1] + 0.5*dx  )  # right edge, here 60.125
    ymin= nicefloat( lats[0]  - 0.5*dy  )  # bottom edge, here 30.0  
    ymax= nicefloat( lats[-1] + 0.5*dy  )  # top edge, here 72.0
    nlons= int( (xmax-xmin)/dx )  +  1  # +1 needed to cope with uneven longitude range
    nlats= int( (ymax-ymin)/dy )  +  1
    newxmax =  xmin + nlons*dx
    newymax =  ymin + nlats*dy
    # safety (in case dx ain't very big!):
    assert  newxmax > xmax, 'x Coordinate problem: %f < %f ' % (newxmax, xmax)
    assert  newymax > ymax, 'y Coordinate problem: %f < %f ' % (newymax, ymax)
    print( 'minmax coords', ymin, ymax, newymax, xmin, xmax, newxmax  )
    
    check_ranges(lons,'Lon')    #  checking linearity of longitude:
    check_ranges(lats,'Lat')
    

    srcEmis =  dict()
    srcEmis['polls']=used_polls.copy()
    srcEmis['lons']=lons.copy()
    srcEmis['lats']=lats.copy()
    srcEmis['dx']=dx
    srcEmis['dy']=dy
     
     

    for poll in used_polls: #  'NOX',: 

       print('Process poll ', poll )
       vals = df[poll].values
       print('Process vals ', poll )

       srcEmis[poll]  = dict()
       for iso3 in iso3s:
         srcEmis[poll][iso3] = dict()
         for src in srcs:
           srcEmis[poll][iso3][src] = dict()
           srcEmis[poll][iso3][src]['sum']  =  0.0
           #if get_vals is not None:
           if get_vals:
             srcEmis[poll][iso3][src]['vals'] =  np.zeros([nlats,nlons])
      
       for n in range(len(df)): # with open(ifile) as f:
    
          iso3       = iso3List[n]
          sec        = secList[n]
          typ        = typList[n]
          lon        = lonList[n]
          lat        = latList[n]
   
          ix  = int( (lon-xmin)/dx )
          iy  = int( (lat-ymin)/dy )
          assert ix < nlons , 'OOPSXX %6.3f %6.3f %6.3f %7.4f %6.3f %s %d %d'% ( lon, xmin, xmax, dx, (lon-xmin)/dx, iso3, ix, nlons  )
          assert ix < nlons and  iy < nlats, 'OOPSXY %6.3f %6.3f %s %d %d %d %d'% ( lon, lat, iso3, ix, iy, nlons, nlats  )
    
          src  = src_name(sec_key, sec, typ)  # e.g. H:P or A2:A or 07:A

          x =  vals[n]

          srcEmis[poll][iso3][src]['sum']    += x
          srcEmis[poll]['Total'][src]['sum'] += x
          #print('GET VALS?', get_vals)
          #MAR2020 if get_vals is not None:
          if get_vals:
             srcEmis[poll][iso3][src]['vals'][iy,ix] += x
    
     
#          if ix == idbg and iy==jdbg: 
#            print('DBG ', poll, lon, lat, src, x, srcEmis[src][iso3][iy,ix] )


    if dbgcc is not None:
       if wanted_poll is 'PMc': used_polls.append('PMc')
       print('Summary, kt, %s' % ifile) 
       print('used ', used_polls ) 
       print('%8s' % 'src', end='')
       for poll in used_polls: print('%12s' % poll, end='')
       print()
       for src in srcs:
         print('%8s' % src, end='')
         for poll in used_polls:
           print('%12.1f' % ( 0.001 * srcEmis[poll][dbgcc][src]['sum']),
                   end='') # kt
         print()

    return srcEmis
   
    
if __name__ == '__main__':

  Usage="""
    camsInfo.py  -h 
     or
    camsInfo.py  TNO_file   (ascii, semicolon separated)
  """
  print('MAIN ', sys.argv)
  if 'ipython' in sys.argv[0]:
    ifile = 'TestCamsInfo.txt'
    ifile = '/home/davids/Work/EU_Projects/CAMS/CAMS50/CAMS50_stallo/TNO_MACC_III_emissions_v1_1_2011.txt'
  else:
    if len(sys.argv) < 2:   sys.exit('\nError! Usage:\n' + Usage)
    if sys.argv[1] == '-h': sys.exit('\nUsage: \n' + Usage)
    ifile=sys.argv[1]

  assert  os.path.exists(ifile), '\nError!\n File does not exist: '+ifile

  print('IFILE', ifile)

  m=readCams(ifile,wanted_poll='PM',get_vals=False,dbgcc='Total')  #PMc is special
  v=readCams(ifile,wanted_poll='PM',get_vals=True,dbgcc='Total')  #PMc is special

  #m=readCams(ifile,wanted_poll='NOX',get_vals=True,dbgcc='Total')  #PMc is special
  #poll='NOX'; iso3='FRA'; src= 'F1:A'
  #m=readCams(ifile,dbgcc='Total')
  #print(np.mean( m[poll][iso3][src]['vals'][:,:] ))

#  print(m['file'])
#  print(m['domain'])
#  print(m['Emis:FRA'][poll])
#  print('France :\n',m['Sum:FRA'][poll])


