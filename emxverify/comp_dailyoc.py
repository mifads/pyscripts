#!/usr/bin/env python3
"""
 Code to compare and plot daily
 Was CompDailyOC.py
"""
import argparse
import calendar
from glob import glob
import matplotlib.pyplot as plt
import netCDF4 as cdf
import numpy as np
import os
import sys
# Dave's scripts
import emxcdf.readcdf as readcdf
from emxmisc.daily2meanvalues import daily2meanValue
from emxplots.plotscat import emepscatplot

# import datetime as dt
# d=dt.datetime(yyy,mm,dd)
# dd=d.timetuple()
# dd.tm_mon -> 2 etc., tm_yday, tm_mday ...

#---------- read filename, variable name and year
#

parser = argparse.ArgumentParser()
parser.add_argument("--mod", help="model filename",required=True)
parser.add_argument("--obs_dir", help="obs dir (RB_OC_...)",required=True)
parser.add_argument("--label", help="label text",type=str,required=True)
parser.add_argument("-d","--dbg", help="extra debug  info",default=None)
parser.add_argument("--hmax", help="altitude limit (m)",type=int,default=500)
parser.add_argument("--period", help="period (Summer, Winter, Annual)",type=str,required=True)
parser.add_argument("--case", help="OC or OM)",type=str,required=True)
parser.add_argument("-o","--odir", help="output dir",default='.')
parser.add_argument("-y","--year", help="year",type=int,required=True)
args = parser.parse_args()
emepfile=args.mod
year    =args.year
period  =args.period
label   =args.label
dbg     =args.dbg
obs_dir =args.obs_dir
print(args)

ydays = 365
if calendar.isleap(year): ydays = 366

# outputs:_
if args.odir:
  os.makedirs(args.odir,exist_ok=True)
odir = args.odir + '/'

resTime='day'
case='OC'
if case=='OC':
  modvar='SURF_ugC_PM_OM25'
  #var='SURF_ug_PM_ASOA'
  obsvar='OMCf'
  unit=r'$\mathrm{\mu}$g C /m$^3$'
else:
  #TMP var='SURF_ugC_PM_OM25'
  modvar='SURF_ug_PM_OM25'
  obsvar='OCf'
  unit=r'$\mathrm{\mu}$gC/m$^3$'


# Observations:
# AM0001R  AM01   40.384444444444448        44.260555555555555             2080
# AT0002R  AT02   47.766666666666666        16.766666666666666              117
# python 3.6 unicode to get rid of b'..' 

#obs_dir = '/home/mifads/Data/RB_OC_stallo/SimpleTimeSeriesData_OC/'
obstable=np.genfromtxt(obs_dir+'/ResGetNILU_LL_2009x.LL',dtype='unicode')

sites=dict()
for code, cc, lat, lon, alt in obstable:
  print('CODETAB',code, lat, cc, alt)
  sites[code,'lat'] = float(lat)
  sites[code,'lon'] = float(lon)
  sites[code,'alt'] = float(alt)
  sites[code,'code'] = cc

obsfiles = glob(obs_dir+"/Data%d/*%d*OC25.txt" % ( year, year) )
print(obsfiles)
mod=[]
obs=[]
c4=[]  # short code
jday=range(1,ydays+1)

n = 0
#srun=run
#if scen != 'Base': srun=scen
#ptab=open('DayTableEbas_vs_%s_%s_%s_h%d.txt' % ( srun, var, period, hmax ),'w')
#ptab.write('#%-19s %8s  %8s  %5s\n' % ( srun, 'obs', 'mod', 'n' ))

emep  = readcdf.readcdf( emepfile, modvar, getVals = True )
emep.printme()

for ff in obsfiles:
  f=os.path.basename(ff)
  if 'uncorrected' in f: continue
  code, yrtxt, txt = f.split('.')
  print ( 'START ', f, code, sites[code,'alt'])
  alt = sites[code,'alt']
  if alt > args.hmax:
    print ( 'Exclude, >%d m:  '% args.hmax, code, alt, f)
    continue
  print ( 'RUNS  ', f, code, alt )
    
  try:
    print ( 'HAVE LatLon ', code, sites[code,'lat'], sites[code,'lon'], f)
  except:
    print ( 'PROBLEM ', code, f)
    continue

  # Model tables have sometimes irregular times, e.g.
  #   starttime endtime OC25 flag
  #   2.958333 3.958333 0.84 0
  # can use daily2meanValue

  m=np.loadtxt(ff,skiprows=1)
  lon, lat = sites[code,'lon'], sites[code,'lat']
  vv, minv, maxv = readcdf.get_vals(lon, lat, emep,minmax=True)
  assert len(vv)> 360, 'Need full year of data, got only %d days' % len(vv)
  oo = np.full_like(vv,np.nan)

  nVals=0
  sumObs=0.0
  sumMod=0.0
  nydays = len(vv) # easy way to find number of days in year

  for record in m:  # daily, or weekly samples (for NO)

    sday, eday, oc, flag = record
    delta_day = eday - sday 
    dd1=int(sday); dd2=int(eday)

    if oc > 0.0:

      # Most sites have just one value spanning 2 days,starting ca. 7am (?)
      # Assign to start or middle day (for weekly)
      if delta_day > 1.1:
         if dbg: print('LONGDAY ', ff, sday, eday )  #NO0002R and NO0039R
         mday = int( 0.5*(sday+eday))
      else:
         mday = dd1  # use start day for 24h samples

      if  mday > ydays:   #NO0002 has sample from 365-372!
        print('WARNING (ignored) LONG ', code, sday, eday, mday )
        continue

      oo[mday] = oc
      vv[mday] = daily2meanValue(sday,min(eday,nydays-1),vv,dbg=False) # copes with non-int days

      if dbg: print( 'OO ', code, sday, eday, mday, oc, oo[mday], vv[mday] )

    # Accumulate crude summer/winter averages:
      if period == 'Annual' or \
          (period == 'Summer' and (sday >= 0.25*ydays and sday < 0.75*ydays)) or \
          (period == 'Winter' and (sday <  0.25*ydays or  sday >= 0.75*ydays)) :
         nVals += 1
         sumObs += oc
         sumMod += vv[mday]
         #print('CALL DM ', code, oc,  sday, eday, vv[mday] )

  print('Test ',  period, code, sday, oc, nVals)

  if nVals > 0:  # Tricky!
    print('ADDing ',  code, sday, nVals, sumObs, lon, lat)
    print(' Mean minv ', np.mean(minv), minv.size )
    print(' Mean   vv ', np.mean(  vv),   vv.size )
    print(' Mean maxv ', np.mean(maxv), maxv.size )
    print(' jday      ', len(jday)  )

    obs.append(sumObs/nVals)
    mod.append(sumMod/nVals)
    c4.append( sites[code,'code'] ) # short codes for scatter plots

    plt.plot(vv,label='Mod.')
    plt.fill_between(jday,minv,maxv,color='b',alpha=0.1)
    plt.plot(oo,'rx',label='Obs.')
    plt.title('%s    Alt.=%dm' % ( code, alt) )

    f= oo > 0.0
    meanobs = np.mean( oo[f] )   # Will fail for Norway so far
    meanmod = np.mean( vv[f] )
    print('MEABS ',code, meanobs, meanmod )
    if code == 'NO0002R':
      for jd in range(ydays):
        print ('NO2:', jd, oo[jd], vv[jd] )
    bias = int( 0.5+(100*(meanmod - meanobs)/meanobs ))
    r=np.corrcoef(oo[f],vv[f])[0,1]
    plt.figtext(0.15,0.85,'Run %s' % label )
    plt.figtext(0.15,0.80,'Bias %3d%%   R=%4.2f' % ( bias, r) )
    plt.legend()
    plt.savefig('%s/PlotDaily%s_%s.png' % ( odir, code, label ) )
    plt.clf()

    #ptab.write(' %-20s %8.3f  %8.3f  %5d\n' % ( code, obs[n], mod[n], nVals ))
    n += 1
#ptab.close()
    

print('NOW, SCATTER ', len(mod), len(obs))
xlabel='Observed %s, %s' % ( case, unit )
ylabel='Modelled %s, %s' % ( modvar, unit )
ofile=odir+'ScatEbas_vs_%s_%s_%s_hmax%d.png' % ( label, modvar, period,  args.hmax )

slope, const, rcoeff = emepscatplot(obs,mod,xlabel='Obs.', ylabel='Mod.',
  label=label+':'+period,labelx=0.01,labely=0.93, minv=0.0,plotstyle='ggplot',
  pcodes=c4,
  addStats=True,ofile=ofile)

