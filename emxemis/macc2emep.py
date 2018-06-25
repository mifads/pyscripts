#!/usr/bin/env python3
"""
  Reads TNO MACC format emission file and converts to EMEP netcdf
"""
#  July 2017
#import collections
from collections import OrderedDict as odict
import os
import sys
import numpy as np

#DS stuff
#import macc.MaccEmepCodes as m
#import mkCdf
import emxemis.maccEmepCodes as m
import emxcdf.makecdf as makecdf

Usage="""
  Usage:
     cams2emep.py tno_emission_file   label   [-x]
  e.g.
     cams2emep.py TNO_MACC_III_emissions_v1_1_2011.txt  MACC_III_emissions_v1_1_2011

  where -x triggers the use of detailed snaps, eg 22, 74
"""
if len(sys.argv) < 3: sys.exit('Error!\n' + Usage)
ifile=sys.argv[1]
label=sys.argv[2]
extraSnaps=False
if len(sys.argv) == 4:
  if sys.argv[3] == '-x': extraSnaps=True
  else:                   sys.exit(Usage)

if not os.path.exists(ifile): sys.exit('Error!\n File does not exist: '+ifile)

#1) emepcodes: 
# e.g. FIN ->  {'cc': '7', 'iso2': 'FI', 'iso3': 'FIN', 'name': 'Finland'}),

emepcodes = m.getMaccEmepCodes()    # e.g. 'FIN',


# 2)  Emissions

# MACC-III style SNAPs, with merged 3+4, split 7
snaps = (1,2,21,22,3,34,5,6,7,71,72,73,74,75,8,9,10) # 74 was zero   # Can be more than used
polls = 'CH4 CO NH3 NMVOC NOX PM10 PM2_5 SO2'.split()  # TNO  style
epolls= 'ch4 co nh3   voc nox pmco pm25 sox'.split()   # EMEP style

# HARD CODE
lon0= -29.93750; lon1 = 60.0625   # :MACCIII_from_A 59.9375
lat0=  30.03125; lat1=  71.96875 
nlon=721; nlat=672
dy=1.0/16 # 0.0625
dx=1.0/8  # 0.125

xmin= lon0 - 0.5*dx     # left edge, here -30
xmax= lon1 + 0.5*dx     # right edge, here 60.125
ymin= lat0 - 0.5*dy     # bottom edge, here 30.0  
ymax= lat1 + 0.5*dy     # top edge, here 72.0
nlons= int( (xmax-xmin)/dx )  
nlats= int( (ymax-ymin)/dy ) 
# BUG gave +1 on nlon, nlat
#BUG lons=np.linspace(xmin,xmin+nlons*dx,nlons) # Ensure 100% uniform
#BUG lats=np.linspace(ymin,ymin+nlats*dy,nlats) # Ensure 100% uniform
lons=np.linspace(xmin,xmin+(nlons-1)*dx,nlons) # Ensure 100% uniform
lats=np.linspace(ymin,ymin+(nlats-1)*dy,nlats) # Ensure 100% uniform
print( 'Lon', xmin, dx, xmax, len(lons), 'dx:', lons[1]-lons[0], lons[0], lons[-1])
print( 'Lat', ymin, dy, ymax, len(lats), 'dy:', lats[1]-lats[0])

idbg=316; jdbg=416 # DK

# TNO emissions:
#Lon;Lat;ISO3;Year;SNAP;SourceType;CH4;CO;NH3;NMVOC;NOX;PM10;PM2_5;SO2
#-29.937500;36.406250;ATL;2011;8;A;0.000000;0.063392;0.000000;0.018761;0.634203;0.048957;0.046509;0.417624

for ipoll in range(1,len(polls)):

   snapemis = dict()
   SumEmis  =  np.zeros([ len(lats),len(lons) ])
   sums     = dict()       # Not used

   snapsums = dict.fromkeys(snaps,0.0)
   print(snapsums)

   with open(ifile) as f:
      n=0
      for line in f:
        if n==0:
           n += 1
           continue
        nline = line.strip('\n')
        n += 1

        fields = line.split(';')
        iso3= fields[2]
        cc2=emepcodes[iso3]['iso2']

        if iso3 not in sums.keys():
           sums[iso3] = dict()  # np.zeros(11)
           sums[iso3]['tot'] = 0.0
           for snap in snaps: sums[iso3][str(snap)] = 0.0

        lon = float(fields[0])
        lat = float(fields[1])
        ix  = int( (lon-xmin)/dx )
        iy  = int( (lat-ymin)/dy )
        if ix > nlons-1 or iy > nlats-1:
           print('OOPS', lon, lat, iso3, ix, iy)
           sys.exit()
        #if ix < 0 or iy < 0:
        #    sys.exit()
        snap= fields[4]  # str
        isnap = int(snap)

        if not extraSnaps:
           if isnap > 12 : isnap = isnap // 10  # 21 to 2, 34 to 3,  etc

        x = float( fields[ipoll+6] )
        if ipoll ==  5:
           x  = x- float( fields[ipoll+7] ) #PM10->PMco
           if x < 0.0:
              print('ERR ', n,  fields[ipoll+6], fields[ipoll+7] )
              print('LINE ', line)
              sys.exit()
              

        if x > 0.0:
           #print('SS ', snapsums )
           #print('IS ', isnap )
           snapsums[isnap]   +=  x
           sums[iso3][snap]  += float( fields[ipoll+6] ) # 1=CH4 etc
           sums[iso3]['tot'] += float( fields[ipoll+6] )
 
           v = 'Emis:%s:snap:%d'% ( cc2, isnap) 
           t = 'Emis:%s:tot'% cc2    # Total, this iso3
           s = 'total_snap%d'% isnap # All countries, this snap

           if v not in snapemis.keys():
              snapemis[v] =  np.zeros([ len(lats),len(lons) ])
           if t not in snapemis.keys():
              snapemis[t] =  np.zeros([ len(lats),len(lons) ])
           if s not in snapemis.keys():
              snapemis[s] =  np.zeros([ len(lats),len(lons) ])
           snapemis[v][iy,ix] += x
           snapemis[t][iy,ix] += x
           snapemis[s][iy,ix] += x

           if ix == idbg and iy==jdbg: 
              print('DBG ', polls[ipoll], lon, lat, cc2, snap, isnap, x )

   # Now, we need to feed the mkCdf module, which expects a list of
   # the variable names, and a 3-D matrix with all values.
   # So, we build up new emissions array which matches varnames - both added
   # only if emissions exist
   emis1=np.zeros([ 1,len(lats),len(lons) ])
   emis2=np.zeros([ 1,len(lats),len(lons) ])

#J   varnames = [ 'total_all' ] # will assign emis1 here
#J   nv = 0
#J   for v in snapemis.keys():
#J       varnames.append( v )
#J       emis2[0,:,:] = snapemis[v][:,:]
#J       SumEmis = SumEmis + emis2[0,:,:]
#J       emis1=np.concatenate([emis1,emis2])
#      print('IJDBGA', nv, v, emis1[nv,jdbg,idbg], emis2[0,jdbg,idbg] )
#J       nv += 1
#J   emis1[0,:,:] = SumEmis[:,:]
   variables= odict()
#   variables['lon'] = dict(units='degrees_east',long_name='longitude',data=lons)
#   variables['lat'] = dict(units='degrees_north',long_name='latitude',data=lats)
   for v in snapemis.keys():
      variables[v] = dict(units='tonnes/yr',long_name=v,data=snapemis[v])
   ofile='SnapEmis_%s_%s.nc' % ( label, epolls[ipoll] )
   #mkCdf.createCDF(varnames,ofile,'f4',lons,lats,emis1) 
   #lonlatfmt changed to get lon lat with ncdump -c. Odd.
   makecdf.create_cdf(variables,ofile,'f4',lons,lats,lonlatfmt=False,txt='TESTING',dbg=False) 
   #sys.exit()

