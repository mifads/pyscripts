#!/usr/bin/env python3
from datetime import datetime, timedelta
import dateutil.parser

"""
EMEP 2012 netcdf has:
  double time(time) ;
    time:long_name = "time at middle of period" ;
    time:units = "days since 1900-1-1 0:0:0" ;
  40923.5, 40951.5, ...
"""
refdate='1900-01-01 00:00:00'
refdate_dt = dateutil.parser.parse(refdate)

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
