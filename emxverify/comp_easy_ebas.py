#!/usr/bin/env python3
#import calendar
# was mkSiteComps.py from NMR-RWC
from dateutil.relativedelta import relativedelta
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import xarray as xr
import readEbas as ebas
import emxmisc.emepstats as emepstats
from pathlib import Path

moddir='/home/davids/MDISKS/Betzy/work/EECCA/'
polls='PMFINE PM_OM25 PM_POM_f_ffuel PM_POM_f_wood PM_CPOM_f_ffuel PM_CPOM_f_wood Levo'.split()
polls='NO2 O3 PMFINE PM_OM25 PM_POM_f_wood PM_CPOM_f_wood Levo'.split()
grid='EECCA'
runs='Emep i1 i2   i3  s3'.split()
ls = 'r--  b-- g-- m-- g:'.split()
label='IS3runs' # Inert POA

obspoll='EC'
modpoll = 'SURF_ug_ECFINE'
#obspoll='Levo'
#modpoll = 'SURF_ug_Levo'
#runs=' i1 i2   i3'.split() # Levo doesn't care about svoc. Missing from Emep
##runs=' i2'.split() # DBG Levo doesn't care about svoc. Missing from Emep
#ls = ' b-- g-- m--'.split()
obspoll='PM2.5'
modpoll = 'SURF_ug_PM25_rh50'
obspoll='OC'   # ; wanted_polls='PM_OM25'.split()
modpoll = 'SURF_ugC_PM_OM25'


years=range(2010,2019)
years=range(2005,2019)
years=range(2010,2019)
#years=range(2013,2014)
nyears = years[-1] - years[0] + 1
tstart = dt.datetime(years[0],1,1)
tend   = dt.datetime(years[-1],12,31)

sites=dict(      
      CH0002R =[ 67, 37],
      CH0005R =[ 69, 39],
      CZ0003R =[ 72, 50],
      DE0002R =[ 62, 51],
      DE0003R =[ 67, 40],
      DE0007R =[ 64, 54],
      DE0008R =[ 66, 48],
      ES1778R =[ 68, 22],
      FR0022R =[ 63, 39],
      IT0004R =[ 71, 37],
      NO0002R =[ 51, 59],
      NO0039R =[ 46, 66],
      NO0056R =[ 51, 64],
      PL0005R =[ 70, 65],
      SI0008R =[ 79, 44]
      )
#sites = dict(CZ0003R=[72, 50]) #  dict(IT0004R =[ 71, 37] )
#sites = dict(NO0002R=[51,59] )   # order i, j, from PS runs
#sites = dict(DE0003R=[67,40])
#sites = dict(CH0002R=[67,37])
#sites = dict(DE0002R=[62,51])


for site in sites.keys():
  print('STARTING ', site)
  outlabel = '%s_%s_%s_%s_%d_%d' % ( grid, obspoll, site, label,  years[0], years[-1] )
  i = sites[site][0] - 1
  j = sites[site][1] - 1
  modout=dict()
  dmod = dict() # all daily vals
  dbg=site=='NO0002R'
  for run in runs:
    ofile = 'D_AsciiOut/asciimod_%s_%s_%s_rv4_45nmr%s_%d_%d.txt' % ( grid, obspoll, site, run, years[0], years[-1] )
    mypath = Path(ofile)
    if os.path.isfile(ofile) and mypath.stat().st_size >  0: # check for empty file also
      dmod[run]  = np.loadtxt(ofile)[:,2]
      assert len(dmod[run])> 1, 'Empty ascii file:'+ofile
    else: # read new data:
      modout[run] = open(ofile,'w')
      dmod[run]   =np.array([])
      for n, year in enumerate( years ):
         print('Reading model nc data:', modpoll, year, run )
         ds=xr.open_dataset(moddir+'rv4_45nmr%s/%d/Base_day.nc' % (run, year) )
         vals = ds[modpoll][:,j,i].values
         dmod[run] = np.append( dmod[run], vals )
         if dbg: print('MODin', run, year, vals[0] )
         for jd in range(len(vals)):
           modout[run].write('%d %3d %8.4f\n' % ( year, jd, vals[jd] ) )

  print('Reading obs ', site)
  obs = ebas.read_ebas(site,obspoll,years[0],years[-1] )  # OBS in ugC/m3

  s = obs[site]
  dobs=s['vals']
  print('DOBS size', len(dobs), site)
  #sys.exit()
  nobs = len(dobs)
  if np.count_nonzero(~np.isnan(dobs)) < 10: # 0.75*nobs: 
      print('MANY NANs:', site, np.count_nonzero(~np.isnan(dobs))  )
      continue

  sAlt =int( float(s['Station altitude'].replace("m","") ))  # can't do int diretc!
  if sAlt > 600: continue

  last_year = -999

  xtime = []
  mmtime = np.full(nyears*12,np.nan)  #  [None] * (nyears*12)
  obsvals=[]

  monmod  =dict()   # winter means for each [run]
  monobs  = np.full(nyears*12,np.nan)
  nmon    = np.zeros(nyears*12)
  
  djfmod =dict()   # winter means
  djfobs = np.full(nyears,np.nan)
  ndjf   =  np.zeros(nyears)

  modvals = dict() # modvals matches obs periods

  for run in runs:
      modvals[run] = []
      monmod[run] = np.full(nyears*12,0.0) # np.nan)
      djfmod[run] = np.full(nyears,0.0) # np.nan)

  for n in range(nobs):
      obsval = dobs[n]
      if obsval >= 0.0:
          t1=s['t1'][n]
          t2=s['t2'][n]

          if t1.year > 2019: break
          if t1.year != last_year:  # Open model data:
              jan1 = dt.datetime(t1.year,1,1)

          period=s['period'][n]
          jd1  = (t1-tstart).days  # query +1. Ascii mod started at zero
          jd2  = (t2-tstart).days
          doy1  = (t1-jan1).days + 1
          doy2  = (t2-jan1).days
          nmonth = (t1.year-tstart.year)*12 + (t1.month-tstart.month)
          iyr = t1.year- years[0]
          xtime.append(t1)
          obsvals.append(obsval)

          if np.isnan( monobs[nmonth] ) : monobs[nmonth] = 0.0
          monobs[nmonth] += obsval
          nmon[nmonth] += 1

          if t1.month < 3 or t1.month == 12:
            if np.isnan(djfobs[iyr]) : djfobs[iyr] = 0.0
            djfobs[iyr] += obsval
            ndjf[iyr] += 1

          #print('%d %3d %3d %2d %2d %2d  %s  %8.3f   %d' % ( t1.year, doy1, doy2, t1.month, t1.day, t1.hour,  period,  obsval, s['flag'][n]   ) )

          if 'ng/m3' in s['Unit']:
             ufac = 1000.0
          elif 'ug/m3' in s['Unit'] or 'ug C/m3' in s['Unit']:
             ufac = 1.0
          else:
             sys.exit('Unknown unit '+obspoll+s['Unit'])
          if 'Levo' in obspoll:
              ufac *= 1.3/1.7  # correct for emission assumptions

          for run in runs:
            if period=='1w':
              #modval = np.mean(dmod[run][doy1:doy2+1])
              modval = np.mean(dmod[run][jd1:jd2+1])
            elif period=='1d':
              #modval = dmod[run][doy1]
              modval = dmod[run][jd1]
            elif period=='2d': # Weird KOS behaviour
              #modval = dmod[run][doy1]
              modval = dmod[run][jd1]
            else:
              sys.exit('Wrong period:%s' % period)
            modval *= ufac

            modvals[run].append(modval)
            monmod[run][nmonth] += modval

            if t1.month < 3 or t1.month == 12:
              djfmod[run][iyr] += modval

          #print('DBG%d %3d %3d %2d %2d %2d  %s  %8.3f   %d' % ( t1.year, doy1, doy2, t1.month, t1.day, t1.hour,  period,  obsval, s['flag'][n]   ) )
            if dbg: print('DBG%s %d %3d %3d %2d %2d %2d iyr: %d %d %s  %8.3f %8.3f   %d' % ( run, t1.year, 
              t1.month, t1.day, t1.hour, nmonth, nmon[nmonth], iyr, ndjf[iyr],  period,  obsval, modval, s['flag'][n]   ) )

  #sys.exit()
  
  
  if len(obsvals) < 1: continue
  

 # Daily stats tabs and plots:
  tab = open('D_Tabs/TabDaily_%s.txt' % outlabel, 'w')
  tab.write('OBS%8s %12.3f %d\n' % ( obspoll, np.mean(obsvals), len(obsvals)  ) )

  dcLimit=75
  plt.plot(xtime,obsvals,'k-',label='Obs')
  for n, run in enumerate(runs):
    plt.plot(xtime,modvals[run],ls[n],label=run)
    stats=emepstats.obsmodstats(obsvals,modvals[run],dcLimit=dcLimit)
    tab.write('MOD%8s %12.3f   Bias %2d%%  R=%4.2f\n' % ( run, np.mean(modvals[run]), stats['bias'], stats['R']  ) )
  tab.close()

  #if stats['dc'] < dcLimit:  useMarkers = True (see dailyplots)
  oplot = 'D_Plots/PlotDaily_%s.png' % outlabel 
  plt.ylim(bottom=0.0)
  plt.legend()
  plt.xticks(rotation=45)
  sname=s['Station name'].replace(" ","")
  sname=sname.replace("ObservatoirePerennedel'Environnement","ObsPerenne")

  title='%s (%s), %sm, %s %d--%d' % (site, sname, sAlt, obspoll, years[0], years[-1] )
  plt.title('%s (%s)' % ( title, 'Daily mean') )
  plt.tight_layout()
  #plt.show()
  plt.savefig(oplot)
  plt.clf()


 # monthly
  montimes= []
  t0mid=dt.datetime(years[0],1,15)
  for nmonth in range(nyears*12): 
      tmm = t0mid + relativedelta(months=nmonth)
      montimes.append(tmm)
      if nmon[nmonth] > 0:
        monobs[nmonth] /= nmon[nmonth]
        for run in runs:
          monmod[run][nmonth] /= nmon[nmonth]
      else:
        for run in runs:
          monmod[run][nmonth] = np.nan

  plt.plot(montimes,monobs, 'k-',lw=2,label='Obs')
  for n, run in enumerate(runs):
    plt.plot(montimes,monmod[run],ls[n], label=run)
  oplot = 'D_Plots/PlotMonthly_%s.png' % outlabel 
  plt.ylim(bottom=0.0)
  plt.legend()
  plt.xticks(rotation=45)
  plt.title('%s (%s)' % ( title, 'Monthly mean') )
  plt.tight_layout()
  plt.savefig(oplot)
  plt.clf()


 #DJF stats tabs and plots:
  dcLimit=0.5*nyears
  if np.count_nonzero(~np.isnan(dobs)) < dcLimit: 
      continue

 # emepstats and np didn't like integer years
  xyears=np.array(years,dtype=float)
  f = ~np.isnan(djfobs)
  if len(djfobs[f]) < 3 : continue
  #trend = 100 * np.polyfit(xyears[f],djfobs[f],deg=1)[0]
  trend= -999.
  tab = open('D_Tabs/TabDJF_%s.txt' % outlabel, 'w')
  tab.write('OBS%8s %12.3f   Nvalid=%3d            Trend:%12.3f%%/yr\n' % ( obspoll,  np.nanmean(djfobs), len(djfobs) ,  trend  ) )
  djftimes= []
  t0mid=dt.datetime(years[0],1,15)
  for iyr in range(nyears):
      tmm = t0mid + relativedelta(years=iyr)
      djftimes.append(tmm)
      if ndjf[iyr] > 2: # Need at least 3 samples :
        djfobs[iyr] /= ndjf[iyr]
        for run in runs:
          djfmod[run][iyr] /= ndjf[iyr]
      else:
        for run in runs:
          djfmod[run][iyr] = np.nan

  plt.plot(djftimes,djfobs,'k-',lw=2, label='Obs')
  for n, run in enumerate(runs):
    plt.plot(djftimes,djfmod[run],ls[n], label=run)
    stats=emepstats.obsmodstats(djfobs,djfmod[run],dcLimit=dcLimit)
    #trendstats=emepstats.obsmodstats(xyears,djfmod[run],dcLimit=dcLimit)
  #  trend = 100 * np.polyfit(xyears[f],djfmod[run][f],deg=1)[0]
    trend= -999.
    tab.write('MOD%8s %12.3f   Bias %3d%%    R=%5.2f  Trend:%12.3f%%/yr\n' % ( run, np.nanmean(djfmod[run]), stats['bias'], stats['R'], trend  ) )
  tab.close()
  oplot = 'D_Plots/PlotDJF_%s.png' % outlabel 
  plt.ylim(bottom=0.0)
  plt.legend()
  plt.xlim([tstart,tend])
  plt.xticks(rotation=45)
  plt.ylabel('Conc. %s' % s['Unit'].replace(" ",""),fontsize=14)
  plt.title('%s (%s)' % ( title, 'DJF mean') )
  plt.tight_layout()
  #plt.show()
  #sys.exit()
  plt.savefig(oplot)
  plt.clf()


 
  
