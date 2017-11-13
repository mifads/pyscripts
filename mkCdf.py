#!/usr/bin/env python3
import netCDF4 as nc
import numpy as np
import time             # Just for creation date
import sys

def createCDF(variables,ofile,typ,lons,lats,data,txt='',dbg=False):
  """
    Creates a netcdf file for a simple 2-D data set and lonlat projection
    together with a variables dictionary containing names, units, etc
  """
  print('OFILE ',ofile)
  cdf=nc.Dataset(ofile,'w',format='NETCDF4_CLASSIC')
  cdf.Conventions = 'CF-1.6'
  cdf.projection = 'lon lat'
  cdf.history = 'Created ' + time.ctime(time.time())
  cdf.description = 'From mkCdf module '+ txt
  nx=len(lons)
  ny=len(lats)

  lon= cdf.createDimension('lon',nx)
  lat= cdf.createDimension('lat',ny)
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
  lonvar.long_name = 'longitude'
  latvar.long_name = 'latitude'

  if dbg :
    print('NX NY ', nx, ny, lons.max(), lats.max())
    print('SHAPE data ', data.shape)
    print('LATS', latvar )

  # Fill coord  data
  lonvar[:] = lons[:]
  latvar[:] = lats[:]


  # We need a list of dictionaries. If variables is just a single
  # dict, we make it into a list

  if isinstance(variables, dict):

    variables = [ variables, ]
    varname=variables[0]['name']

  for n, var in enumerate(variables):
     varname=var['name']
     datvar = cdf.createVariable(varname,typ ,('lat', 'lon',),zlib=True)
     if len(data.shape) == 2:
       datvar[:,:] = data[:,:]
     else:
       datvar[:,:] = data[n,:,:]

     for key in var.keys():
       if key == 'name' : continue # alrady done
       datvar.setncattr(key,var[key])

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
  TestVar=dict( name='TEST1', units='uuu' )
  createCDF(TestVar,'tmp_mkCdfm.nc','f4',lons,lats,data,dbg=True)

  # 2. Example of multiple scalar fields
  # nb order of variable names has to match data order

  data3 = np.zeros([3,180,360],dtype=np.float)
  for n in range(3):
       data3[n,:,:] = data[:,:]*(n+1)

  variables= [   
     dict(name='Var1',units='ppb',long_name='test_variable with CF-illegal units'), 
     dict(name='Var2',units='ug/m3'), 
     dict(name='Var3',units='m s-1')
  ]
  createCDF(variables,'tmp_mkCdfm3.nc','f4',lons,lats,data3,
             txt='Demo of 3 variables',dbg=False)
