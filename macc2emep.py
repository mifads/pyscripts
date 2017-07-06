#!/usr/bin/env python3
# Merged RdTNO.py and RdCAMS.py,   Jul 2017
import collections
import os
import sys
import numpy as np
import mkCdf # Dave's
Usage="""
Usage:
     cams2emep.py tno_emission_file   label
e.g.
     cams2emep.py TNO_MACC_III_emissions_v1_1_2011.txt  MACC_III_emissions_v1_1_2011
"""
if len(sys.argv) < 3: sys.exit('Error!\n' + Usage)
ifile=sys.argv[1]
label=sys.argv[2]
if not os.path.exists(ifile): sys.exit('Error!\n File does not exist: '+ifile)

# 1) Country codes file: #EMEP   ISO3   ISO2  Name #1     ALB    AL    Albania

emepcodes=collections.OrderedDict() # stores iso2, iso3 etc.
tnonum =dict()
CountryList="""
# This file sets EMEP codes, Iso3 and Iso2 (except where the EMEP
# model uses 3-letter Iso2 - e.g. ATL!)
#EMEP   ISO3   ISO2  Name
1     ALB    AL    Albania
56    ARM    AM    Armenia
2     AUT    AT    Austria
69    AZE    AZ    Azerbaijan
3     BEL    BE    Belgium
4     BGR    BG    Bulgaria
50    BIH    BA    Bosnia_and_Herzegovina
39    BLR    BY    Belarus
24    CHE    CH    Switzerland
55    CYP    CY    Cyprus
46    CZE    CZ    Czech_Republic
60    DEU    DE    Germany
6     DNK    DK    Denmark
22    ESP    ES    Spain
43    EST    EE    Estonia
7     FIN    FI    Finland
8     FRA    FR    France
27    GBR    GB    United_Kingdom
54    GEO    GE    Georgia
11    GRC    GR    Greece
49    HRV    HR    Croatia
12    HUN    HU    Hungary
14    IRL    IE    Ireland
13    ISL    IS    Iceland
15    ITA    IT    Italy
53    KAZ    KZ    Kazakhstan
68    KGZ    KG    Kyrgyzstan
45    LTU    LT    Lithuania
16    LUX    LU    Luxembourg
44    LVA    LV    Latvia
41    MDA    MD    Moldova_Republic_of
52    MKD    MK    Macedonia
57    MLT    MT    Malta
17    NLD    NL    Netherlands
18    NOR    NO    Norway
19    POL    PL    Poland
20    PRT    PT    Portugal
21    ROU    RO    Romania
61    RUS    RU    Russian_Federation
47    SVK    SK    Slovakia
48    SVN    SI    Slovenia
23    SWE    SE    Sweden
25    TUR    TR    Turkey
40    UKR    UA    Ukraine
51    YUG    CS    Serbia_and_Montenegro		
30    BAS    BAS   Baltic_Sea
31    NOS    NOS   North_Sea
32    ATL    ATL   Atlantic_Ocean
70    ATX    ATX   Rest_of_Atlantic_Ocean
33    MED    MED   Mediterranean_Sea
34    BLS    BLS   Black_Sea
58    ASI    ASI   Rest_of_Asia
350   INT    INTSHIPS    International_shipping
"""

lines=CountryList.splitlines()
ncc = 0
for line in lines:
   if line == '': continue    # header
   if line.startswith('#'): continue    # header
   cc, iso3, iso2, name = line.split()
   emepcodes[iso3] = dict( cc = cc, iso2=iso2, iso3=iso3, name=name )
   tnonum[iso3] = ncc   # eg GBR -> 27
   ncc += 1

# 2)  Emissions

# MACC-III style SNAPs, with merged 3+4, split 7
snaps = (1,2,34,5,6,71,72,73,74,75,8,9,10) # 74 was zero
polls = 'CH4 CO NH3 NMVOC NOX PM10 PM2_5 SO2'.split()  # TNO  style
epolls= 'ch4 co nh3   voc nox pmco pm25 sox'.split()   # EMEP style

# HARD CODE # From stallo nc:
lon0= -29.93750; lon1 = 59.9375
lat0=  30.03125; lat1=  71.96875 
nlon=720; nlat=672
dy=1.0/16 # 0.0625
dx=1.0/8  # 0.125

xmin= lon0 - 0.5*dx     # left edge
xmax= lon1 + 0.5*dx     # right edge
ymin= lat0 - 0.5*dy     # bottom edge, 27.625
ymax= lat1 + 0.5*dy     # top edge
nlons= int( (xmax-xmin)/dx )  
nlats= int( (ymax-ymin)/dy ) 
lons=np.linspace(xmin,xmin+nlons*dx,nlons+1) # Ensure 100% uniform
lats=np.linspace(ymin,ymin+nlats*dy,nlats+1) # Ensure 100% uniform
print( 'Lon', xmin, dx, xmax, len(lons), 'dx:', lons[1]-lons[0])
print( 'Lat', ymin, dy, ymax, len(lats), 'dy:', lats[1]-lats[0])

idbg=316; jdbg=416 # DK

# TNO emissions:
#Lon;Lat;ISO3;Year;SNAP;SourceType;CH4;CO;NH3;NMVOC;NOX;PM10;PM2_5;SO2
#-29.937500;36.406250;ATL;2011;8;A;0.000000;0.063392;0.000000;0.018761;0.634203;0.048957;0.046509;0.417624

for ipoll in range(1,len(polls)):

   snapemis = dict()
   SumEmis  =  np.zeros([ len(lats),len(lons) ])
   sums     = dict()       # Not used
   snapsums = np.zeros(11) # Not used

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
        #if ix < 0 or iy < 0:
        #    print('OOPS', lon, lat, ix, iy)
        #    sys.exit()
        snap= fields[4]  # str
        isnap = int(snap)
        if isnap > 12 : isnap = isnap // 10  # 21 to 2, etc

        x = float( fields[ipoll+6] )
        if ipoll ==  5:
           x  = x- float( fields[ipoll+7] ) #PM10->PMco
           if x < 0.0:
              print('ERR ', n,  fields[ipoll+6], fields[ipoll+7] )
              print('LINE ', line)
              sys.exit()
              

        if x > 0.0:
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

   varnames = [ 'total_all' ] # will assign emis1 here
   nv = 0
   for v in snapemis.keys():
       varnames.append( v )
       emis2[0,:,:] = snapemis[v][:,:]
       SumEmis = SumEmis + emis2[0,:,:]
       emis1=np.concatenate([emis1,emis2])
#      print('IJDBGA', nv, v, emis1[nv,jdbg,idbg], emis2[0,jdbg,idbg] )
       nv += 1
   emis1[0,:,:] = SumEmis[:,:]
   ofile='SnapEmis_%s_%s.nc' % ( label, epolls[ipoll] )
   mkCdf.createCDF(varnames,ofile,'f4',lons,lats,emis1) 

