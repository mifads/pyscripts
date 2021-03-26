#!/usr/bin/env python3
""" codes
  16, 17 = Artic areas
  2 = sea
  3 = NAM, 4=EUR
"""
import numpy as np
import sys
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib as mpl

hdir='/home/davids/Data/HTAP_v2/'
ds=xr.open_dataset(hdir+'HTAP_Phase2_tier1NC05x05_v2.nc') #receptorNC.nc')
xlons=ds.long.data   # 0.25 .. 359.75
lons=np.roll(xlons,360)
for i, lon in enumerate(lons):
  if lon > 180:
    lons[i] = lon-360   # now -179.75 .. 179.75

lats=ds.lat.data    # 89.75 .. -89.75
codes=ds.region_code.values.astype(int)
codes=np.roll(codes,360,axis=1)
lats=np.flipud(lats)   # now -89.75 .. 89.75
codes=np.flipud(codes)
uniq = np.unique(codes)
#print(uniq) # 2..17
dlon=lons[1]-lons[0]
dlat=lats[1]-lats[0]
lon0 =  lons[0]-0.5*dlon
lat0 =  lats[0]-0.5*dlat

regions=dict(NAM=3, EUR=4, SAS=5, EAS=6, PAN=8, NAF=9, SAF=10, SAM=13, RBU=14, GLOB=999 )

regLL=dict(
   NAM=[-105.,48.0],  EUR=[0.0,45.0], SAS=[75.0,20.0], EAS=[110.0,30.0],
   PAN=[152.0,-38.0], NAF=[0.0,20.0], SAF=[20.0,-15.0], 
   SAM=[-60.0,-15.0], RBU=[90.0,60.0] )



def getRegionMasks(reg):
  print(regions[reg])
  if reg == 'GLOB':
    out=np.full_like(codes,1)
  else:
    out=np.full_like(codes,0.0)
    mask = ( codes == regions[reg] )
    out[mask] = 1
  #print('OUT ', out[2,2], out[300,300] )
  return out

def getNearestRegion(xlat,xlon):
  j = int( (xlat-lat0)/dlat )
  i = int( (xlon-lon0)/dlon )
  #print('CODES', j, i, xlat, lat0, dlat, xlon,lon0, dlon,  codes.shape, codes[j,i])
  return codes[j,i] 


def get_cmaps(ctest):
  v = [ i-0.5 for i in range(1,19) ]

  cmap= plt.cm.get_cmap(ctest,len(v))
  #cmap.set_under('0.15')
  #cmap.set_over('0.15')
  norm=mpl.colors.BoundaryNorm(v, cmap.N)
  ncodes=codes.copy()

  unset = 20
  undef=ncodes< 3
  ncodes[undef] = unset
  undef=ncodes> 15
  ncodes[undef] = unset

  return ncodes, cmap, norm, v

def plotRegions():

  ncodes, cmap, norm, v = get_cmaps()
  plt.pcolormesh(ncodes,cmap=cmap,norm=norm) # fails:,extend='both')
  plt.colorbar()
  plt.ylim(ymin=100)
  plt.show()

def plotCRegions(map):
  import cartopy.crs as ccrs
  import cartopy.feature as cfeature
  from  matplotlib.gridspec import GridSpec #see http://worksofscience.net/matplotlib/colorbar

  ncodes, cmap, norm, v = get_cmaps(map)
  #proj=ccrs.PlateCarree()
  fig=plt.figure(figsize=[16,12])
  #gs = GridSpec(100,100,bottom=0.05,left=0.05,right=0.88)
  proj_used='Mercator'
  proj_used='PlateCarree'
  if proj_used=='Mercator':
    ax=plt.axes(projection=ccrs.Mercator())
  else:
    ax=plt.axes(projection=ccrs.PlateCarree())
  #ax1=fig.add_subplot(gs[:,0:85],projection=proj)
  ax.contourf(lons,lats,ncodes,v,cmap=cmap,norm=norm) #,boundaries=v)
  for reg, coords in regLL.items():
    x=coords[0]; y=coords[1]
    print(reg, x,y)
    ax.text(x,y,reg,bbox=dict(facecolor='yellow')) # , alpha=0.5))
  #ax1.pcolormesh(ncodes,cmap=cmap,norm=norm)
  #ax1.set_ylim(ymin=100)
  ax.coastlines(resolution='10m')
  ax.add_feature(cfeature.BORDERS)
  ax.add_feature(cfeature.COASTLINE)
  plt.tight_layout
  #plt.show()
  plt.savefig('PlotHTAP_Regions_%s_%s.png' % (proj_used, map ))

if __name__ == '__main__':

  import matplotlib.pyplot as plt

  for map in 'tab20 tab20c Paired'.split():
    p=plotCRegions(map)
    sys.exit()
  for reg in 'EUR GLOB'.split():
    m=getRegionMasks(reg)
    #plt.pcolormesh(m)
    #plt.show()
    #plt.clf()

