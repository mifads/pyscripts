#!/usr/bin/env python3
# -*- coding: utf8 -*-

import numpy as np
import calendar
import sys
dtxt='getSeasonalMetrics'
#=============================================================================
def getDiurnal(xo3,year,season=None,dbg=None):
   """ takes a vector of hourly or  365(6)x24 matrix of o3 and returns 24 mean
        hourly values """

   dtxt='getD:'

   mo3 = np.zeros(24)
   no3 = np.zeros(24)

   ileap= 1 if calendar.isleap(year) else 0
   ndays = 365 + ileap
   if dbg: print(dtxt+'ND ', year, ndays )

   #M16 if len(xo3) ==  24*ndays:
   if dbg: print(dtxt+'PRE-SHAPE ', len(xo3), xo3.size, xo3.shape, np.nanmax(xo3), np.nanmin(xo3) )
   if xo3.size ==  24*ndays:
      xo3 = xo3.reshape(ndays,24)
   if dbg: print(dtxt+'IN-SHAPE ', len(xo3), xo3.size, xo3.shape )
   if dbg: print(dtxt+'POS-SHAPE ', len(xo3), xo3.size, xo3.shape, np.nanmax(xo3), np.nanmin(xo3) )

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
       if hh==0 and jd < 20 : print(dtxt+'JDo3 ', jd, hh, o3, mo3[hh], no3[hh] )

   for hh in range(24): # Up to 50% DC? Not so serious for diurnal, for most sites
     tmp = mo3[hh]
     if no3[hh] > 0.5*(jd2-jd1):
       mo3[hh] /= no3[hh]
     else:
       mo3[hh] = np.NaN
     if dbg: print(dtxt+'Res ', hh, tmp, no3[hh], 0.5*(jd2-jd1),  mo3[hh] )

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

def getSeasonalMetrics(yr, x, metric,mm1,nmm,accumulate,
   monthlyWanted=False,  # returns seasonal and monthly if True
   min_days_fraction=0.75,dbg=False,extra_dbg=False):
  """ expects a year full of daily values of some metric x (e.g. O3 conc, 
     AOT, M7)  and outputs either sum or average (with data-capture testing).
     Returns seasonal and monthly values
  """
  dtxt='getSM:'

  year= int(yr)  # needed in case yr is str
  nmdays =  calendar.mdays   # -> 0, 31, 28, ...
  nmdays = np.array(nmdays)  # eases summations below
  if calendar.isleap(year) : nmdays[2] = 29
  nydays = sum ( nmdays )

  assert len(x) == nydays, print(dtxt+'Wrong length! ', len(x), year)

  d1  = calendar.datetime.datetime(year,mm1,1)
  t1  = d1.timetuple()

  msum=np.zeros(13)
  nsum=np.zeros(13)
  frac=np.zeros(13)
  monthlyDC=np.zeros(13,dtype=int) # Will use [0] for seasonal
  monthlyOut=np.zeros(13)

  nActiveMonths = 0
  nValidDays   = 0
  nActiveDays  = 0

  # Screen for active seasons. DANGER. Need to define as np array to allow use
  # as mask. Otherwise, problems, see http://stackoverflow.com/questions/
  # 17779468/numpy-indexing-with-a-one-dimensional-boolean-array

  ValidSeason = True
  in_season= np.array( [ False ] * 13 )

  dtxt='getSM:'
  mtxt=dtxt+metric+':'  # eg getSM:AOT40:
  day = 0
  if dbg: print(mtxt+'Day 1:',t1, day)

  for imm in range(nmm):
     mm = mm1 + imm
     if mm > 12: mm = mm - 12
     in_season[mm] = True 
     if dbg: print(dtxt+' Screen active: ', metric, imm, mm, in_season[mm] )

  for mm in range(1,13):

     for dd  in range(1,nmdays[mm]+1):
         if extra_dbg: print(mtxt+'dd:', day, mm,dd, x[day], \
              np.nansum(msum),in_season[mm], nmdays[mm] )

         if in_season[mm] :

           nActiveDays += 1
           if np.isfinite( x[day] ):
             msum[mm] += x[day]
             nsum[mm] += 1.0
             nValidDays += 1
         day += 1

     frac[mm] = nsum[mm] / nmdays[mm]
     if dbg: print('\nMM'+mtxt+' Date ', day,  mm, dd, 
       ' Msum=', msum[mm], ' Nsum=', nsum[mm], 
       ' nActive=', nActiveDays, ' nValid=', nValidDays )

     if frac[mm] > min_days_fraction:
         if dbg: print('VM'+mtxt+'   Valid month ', mm, 
           ' Msum=', msum[mm], ' MsumCorr=', msum[mm]/frac[mm] )
         msum[mm] *= 1.0/frac[mm]   # Correct here for data-capture
     else:
        # need all months to get valid seasonal
         if in_season[mm] : ValidSeason = False  # Invalid if any one month wrong!?
         if dbg and in_season[mm]: 
            print('VM'+mtxt+' Invalid month,season ', mm, nsum[mm] )
         msum[mm] = np.nan

     monthlyOut[mm] =  msum[mm]
     monthlyDC[mm]  =  int(0.5+100.0*nsum[mm]/nmdays[mm])
     if not accumulate :
        monthlyOut[mm]  /=  nmdays[mm]

  # End of year. We make seasonal sums or averages, weighting the
  # latter by nmdays

  monthlyDC[0]  =  int(0.5+100.0*nValidDays/nActiveDays )
  if ValidSeason: 
        monthlyOut[0]  = np.sum( msum[ in_season ]  )
        #OLD monthlyDC[0]   = np.sum( nmdays[ in_season ]  )
        #print('IN SEA SUM ', metric, mm1, nmm, nActiveDays, seasonal, sumdays, np.sum(msum) )
        #print('IN SEA ??? ',  msum, '\n', 'IN SEA SUM ', in_season )
        if  not accumulate :
          monthlyOut[0]  /= nActiveDays
  else:
        monthlyOut[0]  = np.nan

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

  #OLD return seasonal, monthlyOut, monthlyDC
  if monthlyWanted:
    return monthlyOut, monthlyDC
  else:
    return monthlyOut[0], monthlyDC[0]


if __name__ == '__main__':

  year = 2012
  ndays = 366
  aot40 =  np.ones(ndays) # 1 ppb h per day
  #OLD seasonal, monthlyOut, monthlyDC = getSeasonalMetrics(year,aot40,'AOT40',4,6,True,dbg=True)

  for n in [ 127, 137 ]: # blanks first 5 then 10 days

     aot40[122:n] = np.nan # blank May 2nd-6th

     seasonOut, seasonDC = getSeasonalMetrics(year,aot40,'AOT40',4,6,
                                   accumulate=True,dbg=True)
     print('Test Seasonal   skip 127:', n, ' => ', seasonOut, seasonDC)

  # Test with monthly putputs
  monthlyOut, monthlyDC = getSeasonalMetrics(year,aot40,'AOT40',4,6,
        accumulate=True,monthlyWanted=True,dbg=True)
  print('Test Seasonal   skip 127:', n, ' => ', monthlyOut[0] ) # [0] is now full-period
  print('Test SeasonalDC skip 127:', n, monthlyDC[0] )
  print('Test Monthly    skip 127:', n, monthlyOut[1:] )
  print('Test MonthlyDC  skip 127:', n, monthlyDC[1:] )
  
  #sys.exit('XXX')

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

