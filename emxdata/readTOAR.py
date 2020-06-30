#!/usr/bin/env python3
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

def plot_hourly(times,concs,txt,timeshift):
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

def readTOAR(ifile,param,headersOnly=False,sep=','):

  toar=dict()
  with open(ifile,'r') as f: # Get Headers first
    for n, row in enumerate(f):
       if row.startswith('#'): row = row.replace('#','',1) # In Xu data
       #if ':' not in  row:
       if param in  row:
          nheaders = n
          toar['dataparam'] = row.rstrip().split(',')
          print('EXITS with param:', n,  toar['dataparam'])
          break
       key, val  = row.rstrip().split(sep,maxsplit=1)
       key = key.replace('#','') # In Xu data
       try:
         nval = float(val)
       except:
         nval=val
       toar[key] = nval
  
  if not headersOnly:
    # Values: (pandas makes dates easier)
    x=pd.read_csv(ifile,header=nheaders,parse_dates=[0])
    toar['concs'] = x[param].values
    tparam = x.columns.values[0] # eg Xu had #time
    toar['times'] = list( pd.to_datetime( x[tparam]))  # t[0] Timestamp('2003-09-07 16:30:00')
    print('VALS ', toar['concs'][0], toar['times'][0] )
    #sys.exit()
  return toar
  
  
if __name__ == '__main__':

  if len(sys.argv) == 1:
   ifile='../Xu/CMA_SDZ54421_O3_2003-2016_v1-0.csv'
   toar =  readTOAR(ifile,param='value',sep=':') # ,headersOnly=True)
   plot_hourly(toar['times'],toar['concs'],ifile,timeshift=6)

   lon=toar['station_longitude']
   lat=toar['station_latitude']
   alt=toar['station_altitude']
   alt5=toar['station_etopo_min_alt_5km_year2012']
   units=toar['units(o3)']  # nmole mol-1

  else:
   ifile= sys.argv[1]
   toar =  readTOAR(ifile,param='daytime_avg') # ,headersOnly=True)
   plt.plot(toar['times'],toar['concs'])
   plt.show()

   lon=toar['station_lon']
   lat=toar['station_lat']
   alt=toar['station_alt']
   alt5=toar['station_etopo_min_alt_5km']
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
