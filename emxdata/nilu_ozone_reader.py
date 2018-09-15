#!/usr/bin/env python3
""" 
   gets one ýear of hourly O3 data from nilu file. 
   Corrections for ug/m3 to ppb done for Swiss sites
"""
import calendar
import numpy as np
import os
import re
import sys

# 2016 NILU files look like:
#165083869  MK0007R  ozone  air  1h  MK01L_ThermoUV_Labs  MK01L_uv_abs  2012-01-01T00:00:00  2012-12-31T01:00:00  EMEP
#
#2012-01-01T00:00:00    2012-01-01T01:00:00             NaN    699    invalid

def read_nilu_ozone(ifile,year,flat=False,dbgSite=None):
  """ Reads a requested NILU ascii file, and returns a 365(6)x24 array or 8640 (with flat=True)
      with O3 in ppb. (Corrections done for Swiss sites.) """

  if not os.path.isfile(ifile):
    print('FILE does not exist. Skip')
    badvals = np.full([2],np.nan)  # couldn't get None to work :-(
    return  badvals

  bname=os.path.basename(ifile)
  #r=re.match( r'.*\/(\d{4})\/(.*)_.*', bname)   # '/x/y/2012/NO0001R_2012.dat'
  r=re.match( r'(.*)_(\d{4}).dat', bname)   # 'NO0001R_2012.dat'
  code=r.groups()[0]  # e.g. NO...
  print(bname, 'RCODE?  ', r.groups(), 'CODE  ', code)

  nmdays = calendar.mdays   # -> 0, 31, 28, ...
  if calendar.isleap(year) : nmdays[2] = 29
  nydays = sum ( nmdays )
  print('START  of ',ifile, " code ", code, " year", year) #, "Ndays : ", nmdays)

  dbg = dbgSite

  #o3j24 = np.full([nydays+1,24],np.nan) # Jan1st=1
  o3j24 = np.full([nydays,24],np.nan)    # Jan1st=0

  with open(ifile,'r') as f:
    
    for line in f: 

       s=re.match('(\d{4})-(\d{2})-(\d{2})T(\d{2}):.*',line)
       if not  s:
          print('S MATCH skip:'+line)
          continue
    
       yy= np.int( s.groups()[0] )
       mm= np.int( s.groups()[1] )
       dd= np.int( s.groups()[2] )
       hh= np.int( s.groups()[3] )

       d1=  d1  = calendar.datetime.datetime(yy,mm,dd)
       t1  = d1.timetuple()
       jday = t1.tm_yday
       #12 monthg now: day = t1.tm_yday - 1  # start day in x

       fields = line.split()
       if 'CH0001' in ifile:  
         o3 = 1/1.42 *  np.float( fields[2] ) # Jungfr., -8C, 653 hP - mail from Hjellbrekke/Sabine
       else:
         o3 = 0.5 *  np.float( fields[2] )   # May be value or NaN

       if 'invalid' in line: o3 = np.nan
       if o3 < 0.0:  o3 = np.NaN

       if np.isfinite(o3):

          o3j24[jday-1,hh] = o3  # python indexing

       if dbg and hh==23: print('o3 ', jday, mm,dd,hh, o3 ) # , np.nansum(no3_24h))

       if hh == 24:
          sys.exit('24h HOURS . RECODE')
       if hh == 23:
          if ifile.find('AT0002R') > -1:
            print("o3h ", jday, np.nanmax( o3j24[jday-1,:]) )

  if flat:
    return o3j24.flatten()
  else:
    return o3j24

if __name__ == '__main__':

  import os
  home=os.getenv('HOME')
  year=2016
  site = 'NO0001R_%d.dat' % year # 2012 has just to May
  site = 'NO0039R_%d.dat' % year
  ifile="%s/Data/NILU/DATA_O3/%d/%s" % ( home, year, site )

  o3=read_nilu_ozone(ifile,year,dbgSite='NO0039R')
  fo3=read_nilu_ozone(ifile,year,flat=True,dbgSite='NO0039R')

