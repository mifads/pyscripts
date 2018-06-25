#!/usr/bin/env python3
"""
  Creates a netcdf file from a list of dictionaries containing name and 2-D data
  create_cdf - new and neater
  createCDF  - deprecated
"""
import netCDF4 as nc
import numpy as np
import time             # Just for creation date
import sys

def create_cdf(variables,ofile,typ,lons,lats,lonlatfmt='full',txt='',dbg=False):
  """
    Creates a netcdf file for a simple 2 or 3-D data sets and lonlat projection
    together with a variables dictionary containing names, units, etc.
    Variables lon,lat can be output in full format "float longitude(lon)"
    or short - set with lonlatfmt. (Not sure why this was needed!)
    Update: if full, don't see lon, lat with ncdump -c ! 
  """
  print('OFILE ',ofile)
  cdf=nc.Dataset(ofile,'w',format='NETCDF4_CLASSIC')
  cdf.Conventions = 'CF-1.6'
  cdf.projection = 'lon lat'
  cdf.history = 'Created ' + time.ctime(time.time())
  cdf.description = 'From emxcdf.makecdf  module '+ txt
  nx=len(lons)
  ny=len(lats)

  lon= cdf.createDimension('lon',nx)
  lat= cdf.createDimension('lat',ny)

# typ can be e.g. u2, u8, f4 where u2 = 16 bit unsigned int, i2 = 16 bit signed
#  int, f = f4, d = f8 
# CAREFUL. If file exists, or some problem, can get error
# "Can't add HDF5 file metadata"
# May 12th . changed longitude to lon in 1st. 2018-02-26 - added back full:
  lonv, latv = 'lon', 'lat' 
  #if lonlatfmt == 'full':
  if lonlatfmt is 'full':
     lonv, latv = 'longitude', 'latitude'
  lonvar = cdf.createVariable(lonv,'f4' ,('lon',))
  latvar = cdf.createVariable(latv,'f4' ,('lat',))
  lonvar.units = 'degrees_east'
  latvar.units = 'degrees_north'
  lonvar.long_name = 'longitude'
  latvar.long_name = 'latitude'

  if dbg :
    print('NX NY ', nx, ny, lons.max(), lats.max())
    #print('SHAPE data ', data.shape)
    print('LATS', latvar )

  # Fill coord  data
  lonvar[:] = lons[:]
  latvar[:] = lats[:]

  for var in variables.keys():

   if dbg: print('VAR:', var) #, variables[var])
   datvar = cdf.createVariable(var,typ ,('lat', 'lon',),zlib=True)
   datvar[:,:] = variables[var]['data'][:,:] # fill data

   for key in variables[var].keys():
     #print('KEY', key)
     if key is 'data':
       pass
     else:
       if dbg: print('ATTR', key, variables[var][key])
       datvar.setncattr(key,variables[var][key])

  print( 'NX NY VAR ', nx, ny, np.max(cdf.variables[lonv][:]),
     np.max(cdf.variables[latv][:]))

  cdf.close()
####################

#Depreated. create_cdf is neater
def createCDF(variables,ofile,typ,lons,lats,data,lonlatfmt='full',txt='',dbg=False):
  """
    Creates a netcdf file for a simple 2 or 3-D data sets and lonlat projection
    together with a variables dictionary containing names, units, etc.
    Variables lon,lat can be output in full format "float longitude(lon)"
    or short - set with lonlatfmt. (Not sure why this was needed!)
  """
  print('OFILE ',ofile)
  cdf=nc.Dataset(ofile,'w',format='NETCDF4_CLASSIC')
  cdf.Conventions = 'CF-1.6'
  cdf.projection = 'lon lat'
  cdf.history = 'Created ' + time.ctime(time.time())
  cdf.description = 'From emxcdf.makecdf module '+ txt
  nx=len(lons)
  ny=len(lats)

  lon= cdf.createDimension('lon',nx)
  lat= cdf.createDimension('lat',ny)
# typ can be e.g. u2, u8, f4
# where u2 = 16 bit unsigned int, i2 = 16 bit signed int, 
# f = f4, d = f8 
# CAREFUL. If file exists, or some problem, can get error
# "Can't add HDF5 file metadata"
# May 12th . changed longitude to lon in 1st. 2018-02-26 - added back full:
  lonv, latv = 'lon', 'lat' 
  if lonlatfmt == 'full':
     lonv, latv = 'longitude', 'latitude'
  lonvar = cdf.createVariable(lonv,'f4' ,('lon',))
  latvar = cdf.createVariable(latv,'f4' ,('lat',))
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

  print( 'NX NY VAR ', nx, ny, np.max(cdf.variables[lonv][:]),
     np.max(cdf.variables[latv][:]))

  cdf.close()
####################

if __name__ == '__main__':
  import matplotlib.pyplot as plt
  from collections import OrderedDict as odict
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
  #TestVar=dict( name='TEST1', units='uuu' )
  #createCDF(TestVar,'tmp_mkCdfm.nc','f4',lons,lats,data,dbg=True)

  TestVar=odict()
  TestVar['TEST2D'] = dict(units='uuu', data=data )
  create_cdf(TestVar,'tmp_create_cdf.nc','f4',lons,lats,data,dbg=True)

  # 2. Example of multiple scalar fields
  # nb order of variable names has to match data order

  data3 = np.zeros([3,180,360],dtype=np.float)
  for n in range(3):
       data3[n,:,:] = data[:,:]*(n+1)

  #variables= [   
  #   dict(name='Var1',units='ppb',long_name='test_variable with CF-illegal units'), 
  #   dict(name='Var2',units='ug/m3'), 
  #   dict(name='Var3',units='m s-1')
  #]
  #createCDF(variables,'tmp_mkCdfm3.nc','f4',lons,lats,data3,
  #           txt='Demo of 3 variables',dbg=False)

  variables= odict()
  variables['Var1']= dict(units='ppb',long_name='test_variable with CF-illegal units',data=data3[0,:,:])
  variables['Var2']= dict(units='ug/m3',data=data3[1,:,:])
  variables['Var3']= dict(units='m s-1',data=data3[2,:,:])
  create_cdf(variables,'tmp_create_cdf3.nc','f4',lons,lats,
             txt='Demo of 3 variables',dbg=False)
  
