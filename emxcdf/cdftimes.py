#!/usr/bin/env python3
from datetime import datetime, timedelta
import dateutil.parser
import pandas as pd

"""
EMEP 2012 netcdf has:
  double time(time) ;
    time:long_name = "time at middle of period" ;
    time:units = "days since 1900-1-1 0:0:0" ;
  40923.5, 40951.5, ...
"""
refdate='1900-01-01 00:00:00'
refdate_dt = dateutil.parser.parse(refdate)


# Nov 2023 update. midmonth_year():
# https://practicaldatascience.co.uk/data-science/how-to-pandas-date-range-to-create-date-ranges

def set15th_month(year):
  dt1st = pd.date_range("%s-01-01" % year,"%s-12-01" % year, freq="MS") # => 1st of month
  return [ j+pd.Timedelta('14d') for j in dt1st ]  # gives 15th

def set15th_month_ref1900(year):
  dt1st = pd.date_range("%s-01-01" % year,"%s-12-01" % year, freq="MS") # => 1st of month
  return [ j+pd.Timedelta('14d') - refdate_dt  for j in dt1st ]  # gives 15th

#def mid_month(year):
#  dt1st = pd.date_range("%s-01-01" % year,"%s-12-01" % year, freq="MS") # => 1st of month
#  return [ j+pd.Timedelta('14d') for j in dt1st ]  # gives 15th

# Future - use pddate_time, but date_range tricky, see e.g.
# https://stackoverflow.com/questions/34915828/pandas-date-range-to-generate-monthly-data-at-beginning-of-the-month#34915951
# https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
#ok:    nctimes = pd.date_range("%d-01-01" % year,freq="MS",periods=12)
#not ok:    nctimes = pd.date_range("%d-01-01" % year,freq="M",periods=12)
#not ok:    nctimes = pd.date_range("%d-01-15" % year,freq="M",periods=12)
#
# see: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
# e.g. MS = month start freq, M = month end freq, SMS = semi-month start frequency (1st and 15th)



def days_since_1900(year,mm,dd,dbg=False): # do hours later
    inpdate='%s-%2.2d-%2.2d 00:00:00' % ( year, mm, dd )
    if dbg: print('Inp', inpdate)
    inpdate_dt = dateutil.parser.parse(inpdate)
    dt = inpdate_dt - refdate_dt
    return float(dt.days)

if __name__ == '__main__':
  year=2012
  for mm in range(1,6):
    print( mm, days_since_1900(year,mm,15,dbg=True))
  t=days_since_1900(year,6,15)
#    mid_month='%s-%2.2d-15 00:00:00' % ( year, mm )
#    print(mm, mid_month)
#    mid_month_dt = dateutil.parser.parse(mid_month)
#    dt = mid_month_dt - start_dt
#    print('DT ', mm, dt.days )

  print( set15th_month(2012) )
  print( set15th_month_ref1900(2012) )
