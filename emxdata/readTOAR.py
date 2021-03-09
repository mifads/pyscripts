#!/usr/bin/env python3
import datetime as dt
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from emxozone.seasonalmetrics import getDiurnal
#import emxozone.dailymetrics as eday

def getDailyTOAR(times,concs,year,txt,timeshift=0):
  ndays = 365
  if times[0].is_leap_year : ndays = 366

  vals=np.full([ndays,24], np.nan) # 2016 

  dmean=np.full(ndays, np.nan) # 2016 
  dmax =np.full(ndays, np.nan) # 2016 

  for t, o3 in zip(times, concs):
    if t.year != year: continue
    vals[ t.dayofyear - 1, t.hour ] = o3

  for jd in range(ndays):
    x= vals[jd,:]
    pValid = np.sum(~np.isnan(x)) #  count number of valid
    if pValid > 0.75:
      dmean[jd] = np.nanmean(x)
      dmax[jd]  = np.nanmax(x)

  return dmax, dmean


def plot_hourly(times,concs,txt,timeshift=0):
  hourly = np.zeros(24)
  nhourly = np.zeros(24)
  for t, o3 in zip(times, concs):
    if t.year==2016:
       if o3>0.0:
        hh=int(t.hour) + timeshift
        if hh>23: hh -= 24
        hourly[hh] += o3
        nhourly[hh] += 1
  hourly /= nhourly
  plt.plot(hourly)
  plt.title(txt)
  plt.show()

def readTOAR(ifile,param, sep=',', year=None, daily=False, headersOnly=False):

  toar=dict()
  with open(ifile,'r') as f: # Get Headers first
    for n, row in enumerate(f):
       if row.startswith('#'): row = row.replace('#','',1) # In Xu data
       if param in  row:
          nheaders = n
          toar['dataparam'] = row.rstrip().split(',')
          #print('EXITS with param:', n,  toar['dataparam'])
          break
       #print('ROW:',n,row)
       key, val  = row.rstrip().split(sep,maxsplit=1)
       key = key.replace('#','') # In Xu data
       val = val.replace(' ','')
       try:
         nval = float(val)
       except:
         nval=val

      # Now, harmonise for key variables
       key=key.replace('station_longitude','station_lon')
       key=key.replace('station_latitude','station_lat')
       key=key.replace('station_altitude','station_alt')
       key=key.replace('station_etopo_min_alt_5km_year2012', # Xu
                       'station_etopo_min_alt_5km')

       toar[key] = nval

  
  if not headersOnly: # Values: pandas makes dates easier
    x=pd.read_csv(ifile,header=nheaders,parse_dates=[0])

    # Argh, changing columns names wasn't obvious, but:
    new=x.columns.values.copy()
    new[0] = 'TIME' # eg DE had time, Xu had #time
    x.columns=new
    #tparam = x.columns.values[0]
    if year is not None:
      x=x[x.TIME.dt.year.eq(year)]
      assert len(x)>0, 'no data found for year %s!'% year

    #  t[0] Timestamp('2003-09-07 16:30:00')
    toar['times'] = list( pd.to_datetime( x.TIME)) 
    toar['concs'] = x[param].values
    if daily==True:
      dmax, dmean = getDailyTOAR(toar['times'],toar['concs'],2016,
           txt='XuX',timeshift=0)
      toar['dmax']  = dmax.copy()
      toar['dmean'] = dmax.copy()
    toar['Nused'] = len(x)
    print('VALS ', toar['concs'][0], toar['times'][0] )

  return toar
  
def getallTOARdaily(idir):
   files=glob.glob('%s/*.csv' % idir)
   print(files)

   toars = [] # dict()

   for ifile in files:
     d=readTOAR(ifile,param='value',sep=':',year=2016,daily=True)
     print(ifile, len(d), type( d['dmax']) ) #toar.keys())
     #sys.exit()
     toars.append(d.copy())

   return toars
  
if __name__ == '__main__':

  if len(sys.argv) == 1:

   idir='/home/davids/Data/TOAR/Xu'
   dd=getallTOARdaily(idir)

   #ifile='/home/davids/Data/TOAR/Xu/CMA_SDZ54421_O3_2003-2016_v1-0.csv'
   #toar = readTOAR(ifile,param='value',sep=':') # ,headersOnly=True)
   #tt = toar['times'][99]

   #plot_hourly(toar['times'],toar['concs'],ifile,timeshift=6)

   #units=toar['units(o3)']  # nmole mol-1

  else:

   ifile= sys.argv[1]
   #ifile='/home/davids/Data/TOAR/Germany_daily/DEHH047_O3.csv'
   toar =  readTOAR(ifile,param='daytime_avg',year=2012) # ,headersOnly=True)
   dmax, dmean = getDailyTOAR(toar['times'],toar['concs'],2012,txt='y2012',timeshift=0)
   #plt.plot(toar['times'],toar['concs'])
   #plt.show()

   units=toar['parameter_original_units']  # :,µg/m3]


# OLD
  #y=pd.read_csv(ifile,header=57)
  #y['value']
  #u=pd.to_datetime( y['#time']) # t[0] Timestamp('2003-09-07 16:30:00')
  # Crashes when  more than one :
  #z=pd.read_csv(ifile,sep=':',skipfooter=113910,engine='python')
  #for zz in z.iterrows():
  #   code = zz[0][0]
  #   val  = zz[0][1]
