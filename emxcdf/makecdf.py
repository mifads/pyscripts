#!/usr/bin/env python3
"""
  Creates a netcdf file from a list of dictionaries containing name and 2-D data
  create_cdf - new and neater
  createCDF  - deprecated
"""
import numpy as np
import os
import pandas as pd # for cdf dates
import time             # Just for creation date
import sys
import xarray as xr
import emxcdf.cdftimes as cdft

""" UPDATED MAR 6 2022 to completely skip FillValues; my data don't use them so far
    xarray and _FillValue are very complex and confusing!!! See
      https://github.com/mmartini-usgs/MartiniStuff/wiki/Xarray-things-to-know
"""
dtxt='xrcdf:'

def check_xrcdf(xrtest, xrenc, xrfile):
  if xrtest=='OK':
    print('XRTEST SUCCESS: '+xrfile, xrtest)
  else:
    print('XRTEST FAIL: '+xrfile, xrenc)
    sys.exit('FAIL'+xrfile)

def create_xrcdf(xrarrays,globattrs,outfile,timeVar='',sigfigs=-1,stop_if_error=True,dbg=False):
  #dbg =True  # TMP
  dtxt='dbg:xrcdf:'
  if dbg: print(dtxt+outfile)
  xrdatasets = []
  assert len(xrarrays) >0, 'create_xrcdf:NO XRDATA!'

  for a in xrarrays:
      varname = a['varname']
      if dbg:
        print(dtxt+'XRARRAY='+varname)
        print(dtxt+'ATTR=', a['attrs'])
        print(dtxt+'KEYS=', a.keys())
      
      if '_FillValue' in a['attrs']:
          if dbg: print(dtxt+'FILL', varname)
          #del a['attrs']['_FillValue']
          #Nov 2023
          a['attrs']['_FillValue'] = None   # NB: None is 2022 update
      field = xr.DataArray(a['data'],
                           dims=a['dims'],
                           coords=a['coords'],
                           attrs=a['attrs'])
      if dbg: print(dtxt+'FIELD', varname, np.shape(a['data']), np.max(a['data'])  )
      #if dbg: print(dtxt+'FIELD', field)
      xrdatasets.append(xr.Dataset({varname: field}))

  outxr = xr.merge(xrdatasets)

  outxr.lon.attrs = {
        'long_name': 'longitude',
        'units': 'degrees_east',
        '_FillValue': False,       # 2023-11-24 None won't work here!
        'standard_name': 'longitude'
  }
  outxr.lat.attrs = {
        'long_name': 'latitude',
        'units': 'degrees_north',
        '_FillValue': False,
        'standard_name': 'latitude'
  }

  #if 'time' in outxr.keys():
  #  outxr.time.attrs = { 'dtype': 'float', '_FillValue': False, }
  #  if dbg: print(dtxt+'TIMEKEYS', outxr.time.attrs)
  #  sys.exit('WRNG?')

  for key, val in globattrs.items():
    outxr.attrs[key] = val
    if dbg: print(dtxt+'VAL', key)

  # compression settings:

  encoding=dict()
  data_comp = dict(zlib=True, complevel=5, shuffle=True,  # _FillValue=np.nan,
                     dtype='float32')
  #Nov 2023
  data_comp = dict(zlib=True, complevel=5, shuffle=True, _FillValue=np.nan,
                     dtype='float32')
  data_comp = dict(zlib=True, complevel=5, shuffle=True, _FillValue=None,
                     dtype='float32')

  for var in outxr.coords:
      #encoding[var] = {'dtype': 'f4'} # f4 works better than float for ncview
      if 'time' in var:
       #CF complaint: https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#time-coordinate
        if dbg: print(dtxt+'TIMEOUT', var, outfile)
        #F25
        encoding[var] = {'_FillValue':None}
        #FAIL encoding[var] = {'dtype': 'f4','standard_name':'time', 'units':'days since 1900-1-1 0:0:0', 'decode_times':False, '_FillValue':None}
        encoding[var] = {'standard_name':'time', 'units':'days since 1900-1-1 0:0:0', 'decode_times':False, '_FillValue':None}
        encoding[var] = {'standard_name':'time', 'units':'days since 1900-1-1 0:0:0', '_FillValue':None}
        encoding[var] = {'standard_name':'time', 'unit':'days since 1900-1-1 0:0:0'}
        encoding[var] = {'_FillValue':None} # works
        encoding[var] = {'_FillValue':None,'units':'days since 1900-1-1'} # works! PHEW!
        #FAILS encoding[var] = {'standard_name':'time', '_FillValue':None}
        #FAILS encoding[var] = {'standard_name':'time','_FillValue':None} # works
        #FAILS encoding[var] = {'standard_name':'time', 'unit':'days since 1900-1-1 0:0:0', '_FillValue':None}

      else:

        encoding[var] = {'dtype': 'f4', '_FillValue':None}
        #F25b encoding[var] = {'dtype': 'f4','decoding_times':False, 'units':'days since 1900-1-1 0:0:0', '_FillValue':None}
        #F25failedencoding[var] = {'dtype': 'datetime64[ns]', 'units':'days since 1900-1-1 0:0:0', '_FillValue':None}
#https://stackoverflow.com/questions/45485745/python-xarray-loses-the-units-attribute-for-time-variable?rq=3
#FAILS        encoding[var] = {'dtype': 'f4', 'units':'days since 1900-1-1 0:0:0', 'decoding_times':False, '_FillValue':None}
#FAILS
#          'standard_name':'time',
#          'long_name':"time at middle of month", 


      if dbg: print('COORDS encoding', var, encoding[var] )
#      encoding[var] = {'_FillValue': None}
#  sys.exit()

  if sigfigs > 0:
      data_comp['least_significant_digit'] = np.int32(sigfigs)
      globattrs['least_significant_digit'] = np.int32(sigfigs)

  for var in outxr.data_vars:
      encoding[var] = data_comp
      if dbg: print('OUTXR vars ', var, data_comp)

  if dbg: print('XRmake', outfile)
  try:
    #outxr.to_netcdf(outfile, format='netCDF4',decode_times=False,encoding=encoding)
    outxr.to_netcdf(outfile, format='netCDF4',encoding=encoding)
  except:
    print(dtxt+' OUTCDF FAILED', outfile)
    print(dtxt+' OUTCDF FAIL ENC.', encoding)
    print(dtxt+' OUTCDF FAIL ofile.', outfile)
    if stop_if_error: sys.exit('!!!! makecdf: OUTXR fail'+outfile)
    return outxr, encoding, os.path.basename(outfile)
  outxr.close()
  return 'OK', encoding, os.path.basename(outfile)  # just for status report


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

def fastcdf(lons,lats,data,var='VAR',txt='TXT',ofile='tstcdf_fastcdf.nc'):
  xrarrays = []
  xrarrays.append( dict(varname=var, dims=['lat','lon'],
      attrs = {'note':txt,'NOTE':'test att'},
     coords={'lat':lats,'lon':lons},data=data ) )
  xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile=ofile)


if __name__ == '__main__':

  import matplotlib.pyplot as plt
  from collections import OrderedDict as odict

  lons = np.linspace(-179.5,179.5,360)
  lats = np.linspace(-89.5,89.5,180)
  data = np.zeros([180,360],dtype=float)
  for j in range(180): #len(lats)): # 150,170):  # upper 
    for i in range(360): #len(lons)): # 30,60):  # left 
       data[j,i] = lats[j] # j*1000.0 + i

  x= fastcdf(lons,lats,data,'VAR','TXT','fast.nc')

  # 1. Example of simple scalar field

  TestVar=odict()
  TestVar['TEST2D'] = dict(units='uuu', data=data )

  xrarrays = []
  xrarrays.append( dict(varname='xrxr', dims=['lat','lon'],
      attrs = {'note':'test xx','sector':3,'NOTE':'test att'},
     coords={'lat':lats,'lon':lons},data=data ) )

#TMP  xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='tstcdf_scalar2d.nc')

  # 2. Example of 2d + crude time
  # nb order of variable names has to match data order

  data3 = np.zeros([3,180,360],dtype=float)
  for n in range(3):
       data3[n,:,:] = data[:,:]*(n**2+1)
  times = [ 0, 1, 2 ]

  xrarrays = []
  #Jan2024 - change to month, since "time" now expects pandas time
  #xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
  #   attrs = {'note':'test xx','NOTE':'test att'},
  #   coords={'time':times, 'lat':lats,'lon':lons},data=data3 ) )
  xrarrays.append( dict(varname='xr3d', dims=['month', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'month':times, 'lat':lats,'lon':lons},data=data3 ) )

#TMP
  xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='tstcdf_scalar2dt.nc')
  #sys.exit()   #  JAN 2024, gives month = 0,1,2 - all ok


  #nctimes= [ cdft.days_since_1900(1997,mm,15) for mm in range(1,4)  ]
  # Better date handling:
  #import datetime as dt
  #https://docs.xarray.dev/en/stable/user-guide/time-series.html
  #https://stackoverflow.com/questions/55107623/create-netcdf-file-with-xarray-define-variable-data-types
  # or pandas:

  # Date handling with pandas
  # will output with time:units = "hours since 2012-01-01 00:00:00" ; time:calendar = "proleptic_gregorian" ;

  # BUT: note that date_range is tricky for e.g. mid-month, see e.g. 
  # https://stackoverflow.com/questions/34915828/pandas-date-range-to-generate-monthly-data-at-beginning-of-the-month#34915951
  # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html

  nctimes=pd.date_range("%d-01-01" % 2012,freq="3H",periods=3)
  #t0=dt.datetime(2012,1,1)
  # with nctimes
  xrarrays = []
  xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'time':nctimes, 'lat':lats,'lon':lons},data=data3 ) )
  # timeVar NOT USED ******
#TMP  xrtest =  create_xrcdf(xrarrays,globattrs={'BB':'BB'},outfile='tstcdf_2dnct.nc',timeVar='hours_since:2012-01-01 00:00:00') #days_since_1990')

  # Nov2023 - testing set15th_month
  # rel to 2011-01-01 though
  #nctimes= cdft.set15th_month_ref1900(2011)

  nctimes= cdft.set15th_month(2011)

  xrarrays = []
  xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'time':nctimes[:3], 'lat':lats,'lon':lons},data=data3 ) )
  # timeVar NOT USED ******
  xrtest, xrenc, xrfile =  create_xrcdf(xrarrays,globattrs={'BB':'BB'},outfile='tstcdf_2dpdt.nc',dbg=True) #days_since_1990')
  check_xrcdf(xrtest, xrenc, xrfile)

  xrtest, xrenc, xrfile =  create_xrcdf(xrarrays,globattrs={'BB':'BB'},outfile='tstcdf_2dpdt6fig.nc',sigfigs=6,dbg=True) #days_since_1990')
  check_xrcdf(xrtest, xrenc, xrfile)

  ############
  # All ok, gives float time(time) ;
  #              time:units = "days since 1900-01-01" ;
  #              time:calendar = "proleptic_gregorian" ;
  sys.exit()
  ############



  # Nov2023 - testing
  nctimes= [ cdft.days_since_1900(2015,12,dd) for dd in [ 1,2,3] ]
  print('NCTIMES ', nctimes)
  xrarrays = []
  xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'time':nctimes, 'lat':lats,'lon':lons},data=data3 ) )
  xrtest =  create_xrcdf(xrarrays,globattrs={'BB':'BB'},outfile='bbtestXR3dnc_nov2023.nc',timeVar='days since 1900-1-1 0:0:0',dbg=True) #days_since_1990')

  sys.exit()

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


  #NOV2023 sys.exit()
  #xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='ntestXR3dnc.nc',timeVar='hours_since_2012-01-01')

  xrarrays = []

  tcoords={'time':nctimes}
  xrarrays.append(dict(varname='time',dims=['time'],
   attrs={'long_name':'time at middle of period', 'units':'days since 1900-1-1 0:0:0',
   'calendar':'gregorian','standard_name':'time'},coords=tcoords,data=nctimes))

  xrarrays.append( dict(varname='xr3d', dims=['time', 'lat','lon'],
     attrs = {'note':'test xx','NOTE':'test att'},
     coords={'time':nctimes, 'lat':lats,'lon':lons},data=data3 ) )
  xrtest =  create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile='ntestXR3dnc2.nc',timeVar='days_since_1990',dbg=True)


  #NOV2023
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
  #NOV2023 xcreate_cdf(variables,'tmp_create_cdf3.nc','f4',lons,lats,
  #NOV2023            txt='Demo of 3 variables',dbg=False)
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
  
