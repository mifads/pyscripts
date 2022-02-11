#!/usr/bin/env python3
"""
  Creates a netcdf file from a list of dictionaries containing name and 2-D data
  create_cdf - new and neater
  createCDF  - deprecated
"""
#N18 from datetime import datetime
#N18 import dateutil.parser
import netCDF4 as nc
import numpy as np
import time             # Just for creation date
import sys
import xarray as xr
import emxcdf.cdftimes as cdft

# Older code, without time possibilty. Kept just while testing
def xcreate_cdf(variables,ofile,typ,lons,lats,lonlatfmt='full',txt='',dbg=False):
  """
    Creates a netcdf file for a simple 2 or 3-D data sets and lonlat projection
    together with a variables dictionary containing names, units, etc.
    Variables lon,lat can be output in full format "float longitude(lon)"
    or short - set with lonlatfmt. (Not sure why this was needed!)
    Update: if full, don't see lon, lat with ncdump -c ! 
  """
  if dbg: print('OFILE ',ofile)
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
  #if lonlatfmt is 'full':
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
     #if key is 'data':
     if key == 'data':
       pass
     else:
       if dbg: print('ATTR', key, variables[var][key])
       datvar.setncattr(key,variables[var][key])

  if dbg: print( 'NX NY VAR ', nx, ny, np.max(cdf.variables[lonv][:]),
     np.max(cdf.variables[latv][:]))

  cdf.close()
####################

def create_cdf(variables,ofile,typ,lons,lats,times=None,nctimes=None,
                 lonlatfmt='short',txt='',dbg=False):
  """
    Creates a netcdf file for a simple 2 or 3-D data sets and lonlat projection
    together with a variables dictionary containing names, units, etc.
    Variables lon,lat can be output in full format "float longitude(lon)"
    or short - set with lonlatfmt. (Not sure why this was needed!)
    Update: if full, don't see lon, lat with ncdump -c ! 
   ADDING TIME
   Nov 2018. Adding optional nctime, whic is from 1900-01-01
  """
  if dbg: print('OFILE ',ofile)
  cdf=nc.Dataset(ofile,'w',format='NETCDF4_CLASSIC')
  cdf.Conventions = 'CF-1.6'
  cdf.projection = 'lon lat'
  cdf.history = 'Created by David Simpson (Met Norway) ' + time.ctime(time.time())
  cdf.description = 'From emxcdf.makecdf module '+ txt
  nx=len(lons)
  ny=len(lats)


  lon= cdf.createDimension('lon',nx)
  lat= cdf.createDimension('lat',ny)

  #print ('TEST TIMING ', times)
  timdim=False
  if times is not None:
    tim= cdf.createDimension('time',len(times))
    print ('DO TIMING ', times)
    timdim=True
#  sys.exit()
  if nctimes is not None:
    tim= cdf.createDimension('time',len(nctimes))
    timvar = cdf.createVariable('time','f4' ,('time',))
    timvar.long_name = 'time at middle of period'
    timvar.units = 'days since 1900-1-1 0:0:0'
    timdim=True
    timvar[:] = nctimes[:]
    print ('NC TIMING ', len(nctimes) )
#    sys.exit()

# typ can be e.g. u2, u8, f4
# where u2 = 16 bit unsigned int, i2 = 16 bit signed int, 
# f = f4, d = f8 
# CAREFUL. If file exists, or some problem, can get error
# "Can't add HDF5 file metadata"
# May 12th . changed longitude to lon in 1st. 2018-02-26 - added back full:
  lonv, latv = 'lon', 'lat' 
  if lonlatfmt == 'full':
  #if lonlatfmt is 'full':
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

   if dbg: print('VAR:', var, 'timdim:', timdim) #, variables[var])
   print('TMPVAR:', var, 'timdim:', timdim) #, variables[var])
   if timdim:
     #print('Shape times= ', np.shape( times)  )
     datvar = cdf.createVariable(var,typ ,('time','lat', 'lon',),zlib=True)
     x=variables[var]['data']
     print('SHAPEx', x.shape)
     if ( len(x.shape) == 3 ):
        datvar[:,:,:] = variables[var]['data'][:,:,:] # fill data
     else:
        datvar[0,:,:] = variables[var]['data'][:,:] # fill data
   else:
     #print('dbgVAR0 ', var, typ)
     datvar = cdf.createVariable(var,typ ,('lat', 'lon',),zlib=True)
     #dbgvar = variables[var]['data']
     #print('dbgVAR ', var, dbgvar.shape, datvar.shape)
     datvar[:,:] = variables[var]['data'][:,:] # fill data

   for key in variables[var].keys():
     #print('KEY', key)
     #if key is 'data':
     if key == 'data':
       pass
     else:
       if dbg: print('ATTR', key, variables[var][key])
       datvar.setncattr(key,variables[var][key])

  if dbg: print( 'NX NY VAR ', nx, ny, np.max(cdf.variables[lonv][:]),
     np.max(cdf.variables[latv][:]))

  cdf.close()

##################

#Depreated. create_cdf is neater
def createCDF(variables,ofile,typ,lons,lats,data,lonlatfmt='full',txt='',dbg=False):
  """
    Creates a netcdf file for a simple 2 or 3-D data sets and lonlat projection
    together with a variables dictionary containing names, units, etc.
    Variables lon,lat can be output in full format "float longitude(lon)"
    or short - set with lonlatfmt. (Not sure why this was needed!)
  """
  if dbg: print('OFILE ',ofile)
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

  print('TMPAPR5 ', variables)
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

  if dbg: print( 'NX NY VAR ', nx, ny, np.max(cdf.variables[lonv][:]),
     np.max(cdf.variables[latv][:]))

  cdf.close()
####################

def create_xrcdf(xrarrays,globattrs,outfile,timeVar='',skip_fillValues=False):
  """
   Mar 2021 - added FillValue treatment, based upon tips in https://stackoverflow.com/questions/45693688/xarray-automatically-applying-fillvalue-to-coordinates-on-netcdf-output#45696423
   Use always for coords, but user can choose for variables
  """

  xrdatasets = []

  print(len(xrarrays), type(xrarrays))
  for a in xrarrays:
    print('A  type', type(a))
    #if 'str' in type(a): print('STRING ', a )
    print('A  keys', a.keys())
    varname = a['varname']
    #print('XR VAR ', varname)
    print('XR sub ', varname, a['attrs'], type(a['attrs']) )
    print('XR keys', varname, a.keys())
    #c  = a['coords']
    #print('XR ckeys', varname, c.keys())
    #print('XR coords ', varname, c['lon'], type(c['lon']) )
    #print('XR digits %s %12.6f '% (varname, c['lon'][0]) )
    #print('XR sizes', varname, a['attrs'] ) 
    field = xr.DataArray(a['data'],dims=a['dims'],coords=a['coords'],
                           attrs=a['attrs'])
    xrdatasets.append( xr.Dataset({varname:field}) )

  outxr = xr.merge(xrdatasets)
  # Added following CAMS71/scripts testing.
  outxr.lat.attrs={'long_name':'latitude','units':'degrees_north','standard_name':'latitude'} # below: ,'_FillValue':False}
  outxr.lon.attrs={'long_name':'longitude','units':'degrees_east','standard_name':'longitude'} # below: ,'_FillValue':False}
  #print('GLOB', globattrs)
  #globattr = dict(aa='AA',bb='BB')
  #outxr.attrs['global'] = globattrs
  for key, val in globattrs.items():
    outxr.attrs[key] = val

  encoding=dict()

  print('OUTXR keys', outxr.keys())
  for var in outxr.coords:
    print('OUTXR:::::', var)
    # if skip_fillValues is True: # Coordinates should never need FillValue!
    encoding[var] = {'_FillValue':False} # need to init encoding:w

    #if var=='time' and  timeVar == 'days_since_1990':
    #  encoding['time'] = dict()
    #  encoding['time']['units'] = timeVar

  for var in outxr.data_vars:
    print('VARxr ', var)
    encoding[var]={ 'shuffle':True,
                    'dtype':'float32',
#                    'dtype':'float64',
#                   'chunksizes':[8, ny, 10],
                   'zlib':True,
                   'complevel':5}
    if skip_fillValues is True:
      encoding[var]['_FillValue'] = False
# Consider least_significant_digit=4 to get 4 sif figures? See
# Notes.Notes.netcdfCompression
  print('XRmake', outfile)
  outxr.to_netcdf(outfile, format='netCDF4',encoding=encoding)
  outxr.close()


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
  #create_cdf(TestVar,'tmp_create_cdf.nc','f4',lons,lats,data,dbg=True)
#  create_cdf2(TestVar,'tmp_create_cdf.nc','f4',lons,lats,times=[1., 2., 3.],dbg=True)

  xrarrays = []
  xrarrays.append( dict(varname='xrxr', dims=['lat','lon'],
      attrs = {'note':'test xx','sector':3,'NOTE':'test att'},
     coords={'lat':lats,'lon':lons},data=data ) )
#ds.time.encoding["dtype"] = "float64"

  #xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='ntestXR2.nc')
  xrtestFill =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='fill_ntestXR2.nc',skip_fillValues=True)
  sys.exit()

  # 2. Example of multiple scalar fields
  # nb order of variable names has to match data order

  data3 = np.zeros([3,180,360],dtype=np.float)
  for n in range(3):
       data3[n,:,:] = data[:,:]*(n**2+1)
  times = [ 0, 1, 2 ]

  xrarrays = []
  xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'time':times, 'lat':lats,'lon':lons},data=data3 ) )

  xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='ntestXR3d.nc')
  nctimes= [ cdft.days_since_1900(1997,mm,15) for mm in range(1,4)  ]
  # with nctimes
  xrarrays = []
  xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'time':nctimes, 'lat':lats,'lon':lons},data=data3 ) )
  xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='ntestXR3dnc.nc',timeVar='days_since_1990')

  # Better date handling:
  xrarrays = []

  tcoords={'time':nctimes}
  xrarrays.append(dict(varname='time',dims=['time'],
   attrs={'long_name':'time at middle of period', 'units':'days since 1900-1-1 0:0:0',
   'calendar':'gregorian','standard_name':'time'},coords=tcoords,data=nctimes))

  xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'time':nctimes, 'lat':lats,'lon':lons},data=data3 ) )
  xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='ntestXR3dnc2.nc',timeVar='days_since_1990')
  sys.exit()


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

  # older code for comp
  xcreate_cdf(variables,'tmp_create_cdf3.nc','f4',lons,lats,
             txt='Demo of 3 variables',dbg=False)
  # newer code with optional times
  create_cdf(variables,'tmp_create_cdfNOTIM.nc','f4',lons,lats,dbg=True)
  nctimes= [ cdft.days_since_1900(1887,12,15,dbg=True) ]
  create_cdf(variables,'tmp_create_cdf1NCTIM.nc','f4',lons,lats,nctimes=nctimes,dbg=True)

  # testing with time variable
  variables= odict()
  variables['VarT']= dict(units='ppb',long_name='test_variable with time',data=data3[:,:,:])
  create_cdf(variables,'tmp_create_simpleTIMES.nc','f4',lons,lats,times=[4.,5.,6.],dbg=True)
  nctimes = []
  for mm in range(4,7):
    nctimes.append( cdft.days_since_1900(2012,mm,15,dbg=True))

  create_cdf(variables,'tmp_create_cdfTIMES.nc','f4',lons,lats,nctimes=nctimes,dbg=True)
  
