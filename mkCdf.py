#!/usr/bin/env python3
import netCDF4 as nc
import numpy as np
import time             # Just for creation date


def createCDF(varname,ofile,typ,lons,lats,data,txt='',dbg=False):
  """
    Creates a netcdf file for a simple 2-D data set and lonlat projection
  """
  print('OFILE ',ofile)
  cdf=nc.Dataset(ofile,'w',format='NETCDF4_CLASSIC')
  cdf.projection = 'lon lat'
  cdf.history = 'Created ' + time.ctime(time.time())
  cdf.description = 'From mkCdf module '+ txt
  nx=len(lons)
  ny=len(lats)
  if dbg :
    print('NX NY ', nx, ny, lons.max(), lats.max())
    print('SHAPE data ', data.shape)


  lon= cdf.createDimension('lon',nx)
  lat= cdf.createDimension('lat',ny)
#lonvar = cdf.createVariable('longitude',typ ,('lon',))
# typ can be e.g. u2, u8, f4
# where u2 = 16 bit unsigned int, i2 = 16 bit signed int, 
# f = f4, d = f8 
# CAREFUL. If file exists, or some problem, can get error
# "Can't add HDF5 file metadata"
# May 12th . changed longitude to lon in 1st:
  lonvar = cdf.createVariable('lon','f4' ,('lon',))
  latvar = cdf.createVariable('lat', 'f4' ,('lat',))
  lonvar.units = 'degrees_east'
  latvar.units = 'degrees_north'
  print('LATS', latvar )

  #datvar = cdf.createVariable(varname,typ ,('lon', 'lat',),zlib=True)

  # Fill data
  lonvar[:] = lons[:]
  latvar[:] = lats[:]

  if isinstance(varname, str):
    print('TYPE ', type(varname)) #if type(varname) == 'str':
    print('STR ', varname)
    datvar = cdf.createVariable(varname,typ ,('lat', 'lon',),zlib=True)
    datvar[:,:] = data[:,:]
  else: # if isinstance(varname, list))
    print('ARRAY' , varname )
    print('SHAPE data ', data.shape)
    for n in range(len(varname)):
      datvar = cdf.createVariable(varname[n],typ ,('lat', 'lon',),zlib=True)
      datvar[:,:] = data[n,:,:]

  print( 'NX NY VAR ', nx, ny, np.max(cdf.variables['lon'][:]),
     np.max(cdf.variables['lat'][:]))

  cdf.close()
####################

if __name__ == '__main__':
  import matplotlib.pyplot as plt
  lons = np.linspace(-179.5,179.5,360)
  lats = np.linspace(-89.5,89.5,180)
  data = np.zeros([180,360],dtype=np.float)
  for j in range(180): #len(lats)): # 150,170):  # upper 
    for i in range(360): #len(lons)): # 30,60):  # left 
       data[j,i] = lats[j] # j*1000.0 + i

  #print( 'LONS ', lons[0], lons[-1], lons[1]-lons[0], len(lons))
  #print( 'lats ', lats)
  #plt.imshow(data)
  #plt.show()

  # 1. Example of simple scalar field
  createCDF('TestVar','tmp_mkCdfm.nc','f4',lons,lats,data,dbg=False)

  # 2. Example of multiple scalar fields
  # nb order of variable names has to match data order

  data3 = np.zeros([3,180,360],dtype=np.float)
  for n in range(3):
       data3[n,:,:] = data[:,:]*(n+1)

  createCDF(['Var1','Var2','Var3'],'tmp_mkCdfm3.nc','f4',lons,lats,data3,
             txt='Demo of 3 variables',dbg=False)
