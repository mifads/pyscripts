#!/usr/bin/env python3
from collections import OrderedDict as odict
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
home=os.environ['HOME']

# Mar 2019, not used (yet)
#KG_boreal = 1
#KG_temperate = 2
#KG_medit = 3
#KG_tropical = 4
#KG_list = []


def getKoeppenGeigerBeck(tdir,groupsWanted=[],plotsWanted=False,dbg=False):

  import xarray as xr
  import emxgeo.check_coord_deltas as crd
  ds=xr.open_dataset(f'{tdir}/Beck2023/Beck2023_0p5fracs_from_0p1.nc')

  kgb = dict()
  kgb['lons'] = ds.lon.values
  kgb['lats'] = ds.lat.values
  dx = crd.check_coord_deltas(kgb['lons'])
  dy = crd.check_coord_deltas(kgb['lats'])
  lat0=kgb['lats'][0]-0.5*dy
  lon0=kgb['lons'][0]-0.5*dx
  print(f'KGLONS {lon0} {kgb['lons'][0]} {kgb['lons'][-1]} {dx} {len(kgb['lons'])}')
  print(f'KGLATS {lat0} {kgb['lats'][0]} {kgb['lats'][-1]} {dy} {len(kgb['lats'])}')
  for var in ds.keys():
    kgb[var]= 100 * ds[var].values[:,:]
    if dbg: print('K-G', var, np.max(kgvals[var]) )  # max 1.0

  kgb['grid_desert']  = kgb['BWh_Arid_desert_hot'] + kgb['BWk_Arid_desert_cold']
  kgb['grid_tropics'] = kgb['Af_Tropical_rainforest'] + kgb['Am_Tropical_monsoon']
  kgb['grid_boreal']  = kgb['Dfc_Cold_no_dry_season_cold_summer'] + kgb['Dfd_Cold_no_dry_season_very_cold_winter']
  kgb['grid_tundra']  = kgb['EF_Polar_frost'] + kgb['ET_Polar_tundra']
  ds.close()

  return kgb


def getKoeppenGeigerOrig(groupsWanted=[],plotsWanted=False):
   """ File has:
      Lat      Lon      Cls
   -89.75  -179.75       EF
   -89.75  -179.25       EF
   -89.75  -178.75       EF
  
   By default returns all 29 flags (Af, A...)
   but can ask for just main, e.g. [A, B ]
   """
   ifile= home + '/Work/LANDUSE/KoeppenGeiger/Koeppen-Geiger-ASCII.txt'
   x=np.genfromtxt(ifile,names=True,dtype=None)
   xlat=x['Lat']
   xlon=x['Lon']
   CLs = x['Cls'].astype('str')  # default was S3
   clu_list = list( np.unique(CLs) )
   long_name = clu_list.copy()  # Can expand one day
   if len(groupsWanted) > 0:
     nOut = 1  # Will merge eg. A+B+C
     outList = [ ''.join(groupsWanted) ]  # e.g. AB from A+B
   else:
     for n, c in enumerate(clu_list):
       outList = clu_list.copy()
       nOut = len(clu_list)
   print('Wanted clus:', nOut, ':', outList)
   #sys.exit()
   
   lons = np.linspace(-179.75,179.75,720)
   lats = np.linspace(-89.75,89.75,360)
   print(type(clu_list), len(clu_list), len(lons), len(lats) )
  # Could use bool, but int may simplify import one day
   KoppenGieger=np.zeros([nOut,len(lats),len(lons)]) #,dtype=np.int)
   
   #KG = np.zeros([360,720], dtype=np.int)
   for n in range(len(xlat)):
     ix = int ( (xlon[n]+180)*2 )
     iy = int ( (xlat[n]+ 90)*2 )
     c  = CLs[n] # eg Dfc
     c_index = clu_list.index(c)
     if nOut == 1:
       for code in groupsWanted:
         if c.startswith(code):
           #print( 'CODE ', c, c_index, code)
           KoppenGieger[0,iy,ix] += 1 
     else:
       KoppenGieger[c_index,iy,ix] += 1 
   
#     if c.startswith(('E','Dfc')): #         typ= KG_boreal  # polar, snow -> boreal
#     elif c.startswith(('A','BWh','BSh')): #          typ= KG_tropical  # equatorial, arid-desert-hot -> trop
#     elif c.startswith(('Csa','Csb')): #           typ= KG_medit  # Medit
#     elif c.startswith(('C','D','B')):   # B..s? steppe, 
#           typ= KG_temperate # temperate
#     else:
#       sys.exit()
     #KG[iy,ix] = typ

   outputs = odict()
   #for n, clu in enumerate( clu_list ):
   for n, clu in enumerate( outList ):
     print('SUM ', n, clu, np.sum(KoppenGieger[n,:,:]) )
     outputs[clu]=dict(units='frac',long_name=long_name[n],
        data=KoppenGieger[n,:,:])
     if plotsWanted:
       plt.imshow(KoppenGieger[n,:,:],origin='lower',vmin=0.0,vmax=1.0)
       plt.title(clu)
       #plt.colorbar(shrink=0.5)
       plt.savefig('PlotKoppenGieger_%s.png' % clu )
       plt.close()
   print('END', type(outputs), len(outputs) )

 #   return lons, lats, KG
   return lons, lats, outputs

if __name__ == '__main__':

#   import emxcdf.makecdf as emx # Creates cdf file for a simple lonlat projection
#   lons, lats, kgdata = getKoeppenGeiger()
#   emx.create_cdf(kgdata,'Koeppen-Geiger-Mar2019.nc','i4',lons,lats,dbg=False)
#   # just test emx.create_cdf(kgdata,'Koeppen-Geiger-Aug2020.nc','i4',lons,lats,dbg=False)
##   print('KG ', KG_boreal)

  import os
  import emxplots.plotmap as plot

  tdir='/lustre/storeB/users/davids/Data_Geo/KoeppenGeiger'
  if not os.path.exists(tdir):
    tdir= tdir.replace('storeB','storeA')
  if 'ppi' not in  os.uname().nodename:
    tdir = '/home/davids' + tdir
  assert os.path.exists(tdir),'NO INPUT DIR:'+tdir

  kgb = getKoeppenGeigerBeck(tdir,groupsWanted=[],plotsWanted=False,dbg=False)
  plot.plotmap(kgb['grid_desert'],'KGB-De')

