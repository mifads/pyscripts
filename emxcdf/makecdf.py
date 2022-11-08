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

""" UPDATED MAR 6 2022 to completely skip FillValues; my data don't use them so far
    xarray and _FillValue are very complex and confusing!!! See
      https://github.com/mmartini-usgs/MartiniStuff/wiki/Xarray-things-to-know
"""
def create_xrcdf(xrarrays,globattrs,outfile,timeVar='',sigfigs=-1,dbg=False):
  xrdatasets = []

  for a in xrarrays:
      varname = a['varname']
      if '_FillValue' in a['attrs']:
          del a['attrs']['_FillValue']
      field = xr.DataArray(a['data'],
                           dims=a['dims'],
                           coords=a['coords'],
                           attrs=a['attrs'])
      xrdatasets.append(xr.Dataset({varname: field}))

  outxr = xr.merge(xrdatasets)

  outxr.lon.attrs = {
        'long_name': 'longitude',
        'units': 'degrees_east',
        'standard_name': 'longitude'
  }
  outxr.lat.attrs = {
        'long_name': 'latitude',
        'units': 'degrees_north',
        'standard_name': 'latitude'
  }
  outxr.time.attrs = {
          'dtype': 'f4',
  }

  for key, val in globattrs.items():
    outxr.attrs[key] = val

  # compression settings:

  encoding=dict()
  data_comp = dict(zlib=True, complevel=5, shuffle=True,  # _FillValue=np.nan,
                     dtype='float32')

  for var in outxr.coords:
      if 'time' in var:
        encoding[var] = {'dtype': 'f4'} # f4 works better than float for ncview
#      print('COORDS encoding', var, encoding[var] )
#      encoding[var] = {'_FillValue': None}

  if sigfigs > 0:
      data_comp['least_significant_digit'] = np.int32(sigfigs)
      globattrs['least_significant_digit'] = np.int32(sigfigs)

  for var in outxr.data_vars:
      encoding[var] = data_comp
      encoding[var]['_FillValue'] = None
      if dbg: print('OUTXR vars ', var, data_comp)

  print('XRmake', outfile)
  outxr.to_netcdf(outfile, format='netCDF4',encoding=encoding)
  outxr.close()


def create_fvcdf(xrarrays,globattrs,outfile,timeVar='',skip_fillValues=False,sigfigs=-1,dbg=False):
  """
   Mar 2022: DEPRECATED!! FillValue was causing too much pain (was create_xrcdf)
   Mar 2021 - added FillValue treatment, based upon tips in https://stackoverflow.com/questions/45693688/xarray-automatically-applying-fillvalue-to-coordinates-on-netcdf-output#45696423
   Use always for coords, but user can choose for variables
   sigfigs: number significant figures in output. Set negative to skip
  """

  xrdatasets = []
  #FILL_VALUE =  None # or False. Seems to vary with system?

  print(len(xrarrays), type(xrarrays))
  haveFillValues = False # Some tricky xarray needs here
  for a in xrarrays:
      varname = a['varname']
      print('XR sub ', varname, a['attrs'], type(a['attrs']))
      if dbg:
        print('XR keys', varname, a.keys())
        print('XR coords', varname, a.keys())
        print('XR data', varname, np.max(a['data']) )
      print('XR attrs', varname, a['attrs'], '_FillValue' in a['attrs'] ) 
      if '_FillValue' in a['attrs']: haveFillValues = True
      field = xr.DataArray(a['data'],
                           dims=a['dims'],
                           coords=a['coords'],
                           attrs=a['attrs'])
      xrdatasets.append(xr.Dataset({varname: field}))

  outxr = xr.merge(xrdatasets)

  # Added following CAMS71/scripts testing.
  outxr.lon.attrs = {
        'long_name': 'longitude',
        'units': 'degrees_east',
        '_FillValue': False,
        'standard_name': 'longitude'
  }
  outxr.lat.attrs = {
        'long_name': 'latitude',
        'units': 'degrees_north',
        '_FillValue': False,
        'standard_name': 'latitude'
  }

  for key, val in globattrs.items():
    outxr.attrs[key] = val

      #for var in outxr.coords:  # Coordinates should never need FillValue!
    # was following https://stackoverflow.com/questions/45693688/xarray-automatically-applying-fillvalue-to-coordinates-on-netcdf-output#45696423
    # but didn't work. Added FillValue above
    #    print('OUTXR coords ', var)
    #    encoding[var] = {'zlib':False,'_FillValue': False}

    # compression settings:

  encoding=dict()
  data_comp = dict(zlib=True, complevel=5, shuffle=True,  # _FillValue=np.nan,
                     dtype='float32')

#F22  for var in outxr.coords:
#F22      if var=='lat': continue  # as defined aboe. Otherwise error
#F22      if var=='lon': continue
      #outxr[var]['attrs']['_FillValue'= False)
#F22      data_comp['_FillValue'] =False
#F22      encoding[var] = data_comp
#F22      print('OUTXR coords ', var, encoding[var] ) #  outxr[var]['attrs'] )

  if sigfigs > 0:
      data_comp['least_significant_digit'] = np.int32(sigfigs)
      globattrs['least_significant_digit'] = np.int32(sigfigs)

  if skip_fillValues is True: # Coordinates should never need FillValue!
     print('DATACOMP', data_comp.keys(), haveFillValues )
     if haveFillValues:
         pass  # Canno
     else:
         data_comp['_FillValue'] = False # None # TEST Mar3 False
  else:
     data_comp['_FillValue'] = np.nan
    # encoding[var] = {'_FillValue':False} # need to init encoding:w
    #if var=='time' and  timeVar == 'days_since_1990':
    #  encoding['time'] = dict()
    #  encoding['time']['units'] = timeVar

  for var in outxr.data_vars:
      encoding[var] = data_comp
      if dbg: print('OUTXR vars ', var, data_comp)

  #  if skip_fillValues is True:
  #    encoding[var]['_FillValue'] = False
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
  data = np.zeros([180,360],dtype=float)
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
  #FAILS:
  #xrtestFill =  create_nfcdf(xrarrays,globattrs={'AA':'AA'},outfile='fill_ntestXR2.nc',skip_fillValues=True)
  #sys.exit()

  # 2. Example of multiple scalar fields
  # nb order of variable names has to match data order

  data3 = np.zeros([3,180,360],dtype=float)
  for n in range(3):
       data3[n,:,:] = data[:,:]*(n**2+1)
  times = [ 0, 1, 2 ]

  # Better date handling:
  xrarrays = []
  xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'time':times, 'lat':lats,'lon':lons},data=data3 ) )

  xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='ntestXR3d.nc')
  #nctimes= [ cdft.days_since_1900(1997,mm,15) for mm in range(1,4)  ]
  # Better date handling:
  #import datetime as dt
  #https://docs.xarray.dev/en/stable/user-guide/time-series.html
  #https://stackoverflow.com/questions/55107623/create-netcdf-file-with-xarray-define-variable-data-types

  import pandas as pd # for cdf dates
  nctimes=pd.date_range("%d-01-01" % 2012,freq="3H",periods=3)
  #t0=dt.datetime(2012,1,1)
  # with nctimes
  xrarrays = []
  xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'time':nctimes, 'lat':lats,'lon':lons},data=data3 ) )
  # timeVar NOT USED ******
  xrtest =  create_xrcdf(xrarrays,globattrs={'BB':'BB'},outfile='bbtestXR3dnc.nc',timeVar='hours_since:2012-01-01 00:00:00') #days_since_1990')

  # DIRECT TEST:
  ds=xr.Dataset(
        {"x3d": (("time","lat","lon"),data3)},
        coords={
             "lat":lats,
             "lon":lons,
             "time":nctimes, #[0,1,2],
        }
  )
  ds.to_netcdf('aatest3d.nc',encoding={'time':{'dtype':'f4'}})

  #def ncreate_cdf(variables,lons,lats,nctimes,data):


  sys.exit()
  #xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='ntestXR3dnc.nc',timeVar='hours_since_2012-01-01')

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
  
