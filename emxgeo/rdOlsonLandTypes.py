#!/usr/bin/env python3
import pandas as pd
import sys
import xarray as xr

Olson="""
<p>There are actually 73 land types, not 74, in both the 1992 and 2001 
Olson land maps. The table below shows the translation between the Olson
 2001 and Olson 1992 land maps:
</p>
<pre>	Olson 2001				Olson 1992 	# in
LC #	Description		        	Equivalent      Dry deposition
==============================================================================
1	Urban					1		2
..
13	Wooded Wet Swamp			13		14
=>
LC;name;O92;Dep
1;Urban;1;2
2;Low Sparse Grassland;2;3

"""

#-----------------------------------------------------------------------------
def getOlsonCodes(idir,oDepWanted=False):
  """ not sure first if we wanted Olson1992 or DryDep code.
      but it is the Olson1992 we need. """
  
  ds=pd.read_csv(f'{idir}/OlsonLandTypes.csv',sep=';')
  olsonO92  = dict()
  if oDepWanted: olsonDep = dict()
  for n, row in ds.iterrows():
    nname= '_'.join( c for c in row.LCname.split() )
    olsonO92[int(row.O92)] = nname
    if oDepWanted: olsonDep[int(row.Dep)] = nname
  if oDepWanted:
    return olsonO92, olsonDep
  else:
    return olsonO92

#-----------------------------------------------------------------------------
def getOlsonData(tdir,lcnum):
  olson = dict()
  o92 = getOlsonCodes(tdir)
  ds=xr.open_dataset(tdir+'/v2019-02/Olson_2001_Land_Type_Masks.025x025.generic.nc')
  olson['vals']   = ds[f'LANDTYPE{lcnum:02d}'].values[0,:,:]  # e.g. 8 = Bare desert
  olson['txt']  = o92[lcnum]
  olson['lons'] = ds.lon.values
  olson['lats'] = ds.lat.values
  return olson
#-----------------------------------------------------------------------------
def getOlsonDesert4emep(tdir):
  """
    We use just 8=Base desert. Also have 11=semi desert, 50=sand desert,
    51,52=semi desert xxx, 69=Alpine desert, 
  """
  #ds=xr.open_dataset(tdir+'/v2019-02/Olson_2001_Land_Type_Masks.025x025.generic.nc')
  #desert = ds.LANDTYPE08.values[0,:,:]  # 8 = Bare desert
  #lons=ds.lon.values
  #lats=ds.lat.values
  desert = getOlsonData(tdir,8)['vals']
  #print('LATS', lats[0], lats[-1]) # LATS -89.875 89.875
  dy = 0.25  # Olson data
  j60N = int( (60.0+90)/dy )
  desert[j60N:,:] = 0.0
  return desert

#def mapOlsonLCtoGrid(lons,lats,lc):
#  """ for desired in put grid export fractional cover of LC """
  
#-----------------------------------------------------------------------------
if __name__ == '__main__':
  import os
  import emxplots.plotmap as plot

  tdir='/lustre/storeB/users/davids/Data_Geo/OLSON_MAP'
  if not os.path.exists(tdir):
    tdir= tdir.replace('B','A')
  if 'ppi' not in  os.uname().nodename:
    tdir = '/home/davids' + tdir
  assert os.path.exists(tdir),'NO INPUT DIR:'+tdir

  #o92, oDep = getOlsonCodes()

  de =  getOlsonDesert4emep(tdir)
  plot.plotmap(de,'OlsonDe')
  #de2 =  getOlsonData(tdir,8)
  #plot.plotmap(de2['vals'],'OlsonDe')
