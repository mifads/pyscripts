#!/usr/bin/env python3
# from elvis read_bionat.py
# VERY CRUDE START. TOO COMPLEX :-(
# Probably genral Dataset is simpler than readcdf system...?
# but we might need to work with PS later
import argparse
import matplotlib.pyplot as plt
import netCDF4
#import netCDF4 as cdf
import numpy as np
import os
import sys
homedir=os.getenv('HOME')
#--------- emep bits ---------------
import emxgeo.arealonlatcell as A
import emxgeo.world_box_regions as box

#------------------ arguments  ----------------------------------------------

parser=argparse.ArgumentParser()
parser.add_argument('-i','--ifile',help='Input model day.nc file',required=True)
parser.add_argument('-u','--units',help='units, ngNm2s or kgNha', required=True)
parser.add_argument('-v','--var',help='variable',required=True)
parser.add_argument('--lat',help='lat variable',default='lat')
parser.add_argument('--lon',help='lon variable',default='lon')
parser.add_argument('--area',help='area variable')
args=parser.parse_args()
dbg=False

print('ARGS', args)
emepFile=args.ifile
var=args.var    # 'Emis'  # _mgm2_BioNatNO'
vars= [ var, ] # need array, can't remember why
season='annual' # others need more coding
print('VARS', vars)

# Output in Tg so far, and grid cell areas will be km2
# Series k, M, G, T

if args.units == 'ngNm2s': # e.g  emissions soil N are in ngN/m2/s
  # ng = 1.0e-9 g;  Tg = 1.0e+12 g
  # e * 1.0e6  (km2->m2)  * 1.0e-21  * 365*24*3600 -> Tg

  unitfac=1.0e6 * 1.0e-21 * 365*24*3600  

elif args.units == 'mgm2': #  typical Base_fullrun
  # Tg = 1.0e12 mg
  # e / 1.0e6  (km2->m2)  * 1.0e-9  -> Tg

  unitfac=1.0e6 * 1.0e-15

elif args.units == 'kgNm2': # e.g  Weng soil N 
  # Tg = 1.0e9 kg
  # e / 1.0e9  (km2->m2)  * 1.0e-9  -> Tg

  unitfac=1.0e6 * 1.0e-9

elif args.units == 'kgNha':  # Annual
  # e * 1.0e2  (km2->ha)  * 1.0e9 -> Tg
  unitfac=1.0e2 * 1.0e-9

#elif args.units == 'tonne':  # Annual
#  # e * 1.0e2  (km2->ha)  * 1.0e9 -> Tg
#  unitfac=1.0e2 * 1.0e-9

else:
  sys.exit('Units not coded yet: '+ args.units)

# e in mg/m2
# e * km2 * 1.0e6 = mg
# *1.0e-18 -> Tg
#unitfac=1.0e6 * 1.0e-15  * 14/30.0 # emep gives mg(NO)/m2/y


#------------------ directory setup -----------------------------------------
ecdf = netCDF4.Dataset(emepFile,'r') # for all variables etc
if args.lat: lat=args.lat
if args.lon: lon=args.lon
print('VARS ', ecdf.variables.keys())
lats=ecdf.variables[lat][:]
lons=ecdf.variables[lon][:]
if args.area:
  areaVar=args.area
  areaVals=ecdf.variables[areaVar][:]
  if np.max(areaVals) > 1.0e7:  # assume m2
    areaVals *= 1.0e-6  
  print('Reads area too: ', np.max(areaVals) )
dlat = lats[1]-lats[0]  # Assume equal deltas
dlon = lons[1]-lons[0]  # Assume equal deltas
print('DLAT, DLON', dlat, dlon )

regions=box.getMaccRegions()
print(regions)

def shortvar(var):
      """ just shortens name """
      var2=var.replace('SURF_ug_PM_','')
      var2=var2.replace('SURF_ug_','')
      var2=var2.replace('_NV','')
      var2=var2.replace('BioNat','')
      return var2
  
nReg = len(regions.keys())
regmask = np.zeros([nReg,len(lats),len(lons)])
regsum  = np.zeros([nReg,len(vars)])
regavg  = np.zeros([nReg,len(vars)])
area    = np.zeros([nReg])
area2    = np.zeros([nReg]) # from emep for comp
tsum = {}

  
idbg=114; jdbg= 82  #  11508 mg/m2
idbg=50; jdbg= 50  # 
idbg=380; jdbg= 300  # ca. Oslo 

ny=len(lats)
nx=len(lons)
km2=np.zeros(ny) # function of latitude only

for j, ylat in enumerate(lats):
    if args.area:
      km2[j] = areaVals[j,0] # should be same for all lon
    else:
      #km2[j] = A.km2_areaLonLatCell(ylat,dlat,dlon)
      km2[j] = A.km2_areaLonLat_of_wgs84pixel(ylat,dlat,dlon)
    if j==jdbg:
        print('DBGAREA', ylat, dlat, dlon, np.sqrt(km2[j]) )

    for i, xlon in enumerate(lons):
  
      n=0
      for key in regions.keys():
         y0, y1, x0, x1 = regions[key][:]
         if j == jdbg and i == idbg:
           #if dbg: 
           print('DBG ', key, y0, y1, x0, x1,  ylat, xlon, np.sqrt(km2[j]))
  
         if ( y0 <= ylat <= y1 ) and ( x0 <= xlon <= x1 ):
            regmask[n,j,i] = 1.0
            if j == jdbg and i == idbg: print('AREA ', i,j, km2[j] ) #BOX , xkm2)
            area[n] += km2[j]
         n += 1
  
iVar=0  
xvals=ecdf.variables[var]
#if season == 'fullrun':
if xvals.ndim ==  3:
      print('3D? Take sum')
      tvals=ecdf.variables[var][:,:,:]   # 1980-2010, 372 monthly, kg/m2/s
      if args.units.endswith('s'): 
        vals = np.mean(tvals,axis=0) # annual mean
      else:
        vals = np.sum(tvals,axis=0) # annual sum
#elif season == 'annual':
elif xvals.ndim==2:
      vals=ecdf.variables[var][:,:]   # 1980-2010, 372 monthly, kg/m2/s
else:
      vals = np.mean(tvals[3:9,:,:],axis=0) # summer
      tvals=0

var=shortvar(var)
  
esum = np.zeros([ny,nx])
tsum[var] = 0.0
for j in range(ny):
    for i in range(nx):
        e = vals[j,i]  # mgm2
        if e>0 :

           tsum[var] +=  e 
  
           # regional:
           n = 0
           for key in regions.keys():
             regsum[n,iVar] += e*km2[j]*regmask[n,j,i]
             n += 1

n=0; iVar=0
for key in regions.keys():
  print('SUM Area %2d %-6s %12.1f Emis %10.4f Tg' % ( n, key, area[n],  regsum[n,iVar] * unitfac ))
  n += 1
