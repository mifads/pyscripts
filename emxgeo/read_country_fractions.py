#!/usr/bin/env python3
from collections import OrderedDict as odict
import numpy as np
import xarray as xr
import sys

cells=odict()

"""   float cell_area(lat, lon) ;
            cell_area:units = "km^2" ;
      byte CC_407(lat, lon) ;
             CC_407:long_name = "Kattegat" ;
             CC_407:area_km2 = 23659.4f ;
"""

def get_country_fractions(ccodes,res='0302',smallNorway=True,dbg=False): # eg IE, BG
  """ For Norway we usually exclude Svalbard """

  import os
  tdir='/lustre/storeB/users/davids/Data_Geo/'
  if not os.path.exists(tdir):
    tdir= tdir.replace('storeB','storeA')
  if 'ppi' not in  os.uname().nodename:
    tdir='/home/davids/Data/'
  assert os.path.exists(tdir),'NO INPUT DIR:'+tdir
  print('TDIR:', tdir)

  ifile= f'{tdir}/EMEP_CountryStuff/emep_ll_gridfraction_{res}degCEIP_2018.nc'
  #ifile=f'/home/davids/Data/EMEP_CountryStuff/emep_ll_gridfraction_{res}degCEIP_2018.nc'
  ds=xr.open_dataset(ifile)
  km2=ds.cell_area.values

  countries= dict()
  countries['lats'] = ds.lat.values    # 260 
  countries['lons'] = ds.lon.values    # 400 
  countries['cell_km2']  = km2
  idbg=119; jdbg=111

  for cc in ds.variables:   # eg CC_14 for IE
    if cc.startswith('CC'):  
       ccode=ds[cc].long_name
       txt, num = cc.split('_')
  
       if ccode in ccodes:
         countries[ccode] = dict()
         countries[ccode]['fractions'] =  np.full_like(km2,0.0)
         countries[ccode]['area_km2'] =  0.0

         c=ds[cc].values  
         if ccode=='NO' and  smallNorway: 
           for j, lat in enumerate(ds.lat.values):
             if lat > 72.0:
              break
           print('FIX NORWAY', j, ds.lat.values[j]  )
           c[j:,:] = 0.0
         if dbg: print('CCODE', cc, ccode, np.max(c), np.min(c) )
         countries[ccode]['fractions'][:,:] =  0.01* c
         countries[ccode]['area_km2'] = np.sum(km2*countries[ccode]['fractions'],where=c>0.0)
  
         f = countries[ccode]['fractions'] 
         if dbg: print( 'IN', ccode, countries[ccode]['area_km2'], np.shape(f), np.max(f), np.min(f) )
  return countries

if __name__ == '__main__':

  codes='NL DK NO SE FI'.split()
  ccdata=get_country_fractions(codes)
  print( ccdata.keys())
  for cc in codes:
    f = ccdata[cc]['fractions'] 
    print( cc, ccdata[cc]['area_km2'], np.max(f), np.min(f) )



