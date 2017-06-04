#!/usr/bin/python3
# -*- coding: utf8 -*-

import numpy as np
import calendar
import sys
dtxt='getSeasonalMetrics'

#=============================================================================
def getDiurnal(xo3,year,season=None,dbg=None):
   """ takes a vector of hourly or  365(6)x24 matrix of o3 and returns 24 mean
        hourly values """

   mo3 = np.zeros(24)
   no3 = np.zeros(24)

   ileap= 1 if calendar.isleap(year) else 0
   ndays = 365 + ileap
   if dbg: print('ND ', year, ndays )

   #M16 if len(xo3) ==  24*ndays:
   if dbg: print('PRE-SHAPE ', len(xo3), xo3.size, xo3.shape, np.nanmax(xo3), np.nanmin(xo3) )
   if xo3.size ==  24*ndays:
      xo3 = xo3.reshape(ndays,24)
   if dbg: print('IN-SHAPE ', len(xo3), xo3.size, xo3.shape )
   if dbg: print('POS-SHAPE ', len(xo3), xo3.size, xo3.shape, np.nanmax(xo3), np.nanmin(xo3) )

   if season == 'summer':
     jd1=91+ileap; jd2=271+ileap
   else:
     jd1 = 1; jd2 = 365 + ileap

   for jd in range(jd1,jd2+1):
     #if jd< 31: print('JD ', ndays, jd )
     for hh in range(24):
       o3 = xo3[jd-1,hh]
       if np.isfinite(o3):
         mo3[hh] = mo3[hh] + o3
         no3[hh] += 1.0
       if hh==0 and jd < 20 : print('JDo3 ', jd, hh, o3, mo3[hh], no3[hh] )

   for hh in range(24): # Up to 50% DC? Not so serious for diurnal, for most sites
     tmp = mo3[hh]
     if no3[hh] > 0.5*(jd2-jd1):
       mo3[hh] /= no3[hh]
     else:
       mo3[hh] = np.NaN
     if dbg: print('GetDiurnal ', hh, tmp, no3[hh], 0.5*(jd2-jd1),  mo3[hh] )

   return mo3.copy()

#=============================================================================
def getDayNightIndex(o3,dbg=False):
  """ expects a diurnal set (24 values) of O3 (from e.g. getDiurnal above)
     and calculates ratio di24 = dmax/dmin 
  """

  dbg=True
  if dbg: print("DI24 IN DI ", len(o3), o3.shape, o3) 
  if len(o3) > 364:
     year = 1999 # Fake non-leap year
     if  len(o3) == 366:
        year = 2012  # Fake leap
        if dbg: print("FAKE LEAP? ", len(o3),  year) 
     o3 = getDiurnal(o3,year,season=None,dbg=True)
  if dbg:
    print("DI24 NEXT", len(o3), o3.shape ) 
    for h in range(0,24):
      print("DI24 VALS", h, o3[h] ) 

  pValid = ( o3 > -999).sum()  # crude way to count number of non-NaNs
  if pValid>0.75*24: 
    if np.nanmin(o3) < 0.001 :
       print ("NAN??? ", pValid, np.nanmin(o3), o3)
       sys.exit('NAN')
    di24 = np.nanmax(o3) / np.nanmin(o3)
    if dbg: print('DI24:', len(o3), np.nanmax(o3) , np.nanmin(o3), di24 )
  else:
    di24 = np.nan

  return di24
#-----------------------------------------------------------------------------

def getSeasonalMetrics(yr, x, metric,mm1,nmm,accumulate,dbg=False):
  """ expects a year full of daily values of some metric x (e.g. O3 conc, 
     AOT, M7)  and outputs either sum or average (with data-capture testing).
     Returns seasonal and monthly values
  """

  year= int(yr)  # needed in case yr is str
  nmdays =  calendar.mdays   # -> 0, 31, 28, ...
  nmdays = np.array(nmdays)  # eases summations below
  if calendar.isleap(year) : nmdays[2] = 29
  nydays = sum ( nmdays )
  MIN_DAY_FRACTION = 0.75

  d1  = calendar.datetime.datetime(year,mm1,1)
  t1  = d1.timetuple()
  #12 monthg now: day = t1.tm_yday - 1  # start day in x
  day = 0
  if dbg: print('Day 1:',t1, day)

  assert len(x) == nydays, print('Wrong length! ', len(x), year)

  #S msum=np.zeros(nmm)
  msum=np.zeros(13)
  nsum=np.zeros(13)
  frac=np.zeros(13)
  monthlyDC=np.zeros(12,dtype=int)
  monthlyOut=np.zeros(12)

  nActiveMonths = 0
  nValidDays   = 0
  nActiveDays  = 0

  ValidSeason = True

  # Screen for active seasons. DANGER. Need to define as np array to allow use
  # as mask. Otherwise, problems, see http://stackoverflow.com/questions/
  # 17779468/numpy-indexing-with-a-one-dimensional-boolean-array

  in_season= np.array( [ False ] * 13 )

  for imm in range(nmm):
     mm = mm1 + imm
     if mm > 12: mm = mm - 12
     in_season[mm] = True 
     if dbg: print(dtxt+' Screen active: ', metric, imm, mm, in_season[mm] )

  for mm in range(1,13):

     #mm = mm1 + imm
     #if mm > 12: mm = mm - 12

     for dd  in range(1,nmdays[mm]+1):
         #if dbg: print(dtxt, metric, day, mm,dd, x[day], np.nansum(msum), \
         #      in_season[mm], nmdays[mm] )
         if np.isfinite( x[day] ):
             msum[mm] += x[day]
             nsum[mm] += 1.0
             nValidDays += 1

         if in_season[mm] : nActiveDays += 1
         day += 1
         #S if day >= nydays:  day = day - nydays

     frac[mm-1] = nsum[mm] / nmdays[mm]
     if dbg: print('\n'+dtxt+' Date ', day,  mm, dd, msum[mm], nsum[mm],
                      nActiveDays, nValidDays )
     if frac[mm-1] > MIN_DAY_FRACTION:
         if dbg: print(dtxt+'   Valid month ', mm, msum[mm], msum[mm]/frac[mm-1] )
         msum[mm] *= 1.0/frac[mm-1]
     else:
        # need all months to get valid seasonal
         if in_season[mm] : ValidSeason = False 
         if dbg: print(dtxt+' Invalid month ', mm, nsum[mm] )
         msum[mm] = np.nan

     monthlyOut[mm-1] =  msum[mm]
     monthlyDC[mm-1]  =  int(0.5+100.0*nsum[mm]/nmdays[mm])
     if  not accumulate :
        monthlyOut[mm-1]  /=  nmdays[mm]

  # End of year. We make seasonal sums or averages, weighting the
  # latter by nmdays

  if ValidSeason: 
        seasonal  = np.sum( msum[ in_season ]  )
        sumdays   = np.sum( nmdays[ in_season ]  )
        #print('IN SEA SUM ', metric, mm1, nmm, nActiveDays, seasonal, sumdays, np.sum(msum) )
        #print('IN SEA ??? ',  msum, '\n', 'IN SEA SUM ', in_season )
        if  not accumulate :
          seasonal  /= nActiveDays
  else:
        seasonal  = np.nan

#  with np.errstate(all='ignore'):
#        mdivs = np.divide( msum, nsum )   # gives inf for /0.0

  #if mfile:
  #  try:
  #    with open(mfile,'w') as f:
  #      #print('MFILE ', mfile)
  #      for mm in range(12):
  #        #print('%2d  %12.3f\n' % ( mm+1, monthlyOut[mm] ) )
  #        f.write('%2d  %12.3f\n' % ( mm+1, monthlyOut[mm] ) )
  #  except IOError:
  #    sys.exit('FAILED TO OPEN MONTHLY %s' % mfile )
  #  else:
  #    f.close()

  return seasonal, monthlyOut, monthlyDC

if __name__ == '__main__':

  year = 2012
  ndays = 366
  o3 =  np.ones(ndays)
  seasonal, monthlyOut, monthlyDC = getSeasonalMetrics(year,o3,'AOT40',4,6,True,dbg=True)

  print('Seasonal = ', seasonal )
  print('Monthly = ', monthlyOut )

  o3 = np.full([ndays,24],40.0)
  o3[:,12] = 50.0
  print('DN = ', getDayNightIndex(o3) )
#def getSeasonalMetrics(lat, year, x, metric,accumulate):
#def getSeasonalMetrics(year, x, metric,mm1,nmm,accumulate):

  print(' Into Diurnals ', o3.size, o3.shape )
  ho3 = getDiurnal(o3,year)
  print(' Diurnals ', ho3[0], ho3[23] )
  o3 = np.linspace(30.0,50.0,num=ndays*24)
  ho3 = getDiurnal(o3,year)
  print(' HH Diurnals ', ho3[0], ho3[23] )

