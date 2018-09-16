#!/usr/bin/env python3
"""
 Code to compare and plot daily O3, diurnal O3
 Produces e.g.:
    Daily_ppb_DmaxO3_EUR_MHD_rv4_32a_2012.png
    Diurn_O3_EUR_MHD_rv4_32a_2012.png
    TableOzoneMetrics_Dmax, AOT40, M6, ....

 was mkModObsMetrics.py
 Nov 2017. From Work/RESULTS/MAPS/Etzold2017/scripts_stallo/CdfCompAOT40.py
 From Work/RESULTS/O3_work_2016 but now using EmepCdf and not getEmepPt
 Inspired a little my mkGawOzoneMetrics
"""
import argparse
import calendar
from collections import OrderedDict as odict
import glob
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import sys
# Own:
import emxcdf.readcdf as readcdf
from emxdata.nilu_ozone_reader import read_nilu_ozone 
from emxplots.plotscat import emepscatplot 
from emxplots.plotdaily import plotdaily
from emxplots.plotdiurnal import plotdiurnal, makediurnal
from emxozone.dailymetrics import defmetrics, get_metrics, accumulated #, tzo3
from emxozone.seasonalmetrics import getSeasonalMetrics, getDayNightIndex

dtxt='comp_ozone_metrics:'
Dummy=False  # will use fake model values, 

#---------- read filename, variable name and year
#
# The system uses assumes that a file TabSites_O3_YYYY.txt exists
# in the obs_dir, and hourly data are collected in 
# yYYYY/ files


parser = argparse.ArgumentParser()
parser.add_argument("--mod", help="model filename",required=True)
parser.add_argument("--obs_dir", help="obs directory",required=True)
parser.add_argument("-d","--dbgSite", help="site-code for debug eg MHD",default=None)
parser.add_argument("-e","--expr", 
     help='expression for sites (eg. "site.startswith(NO)" or alt<300', type=str)
parser.add_argument("--expr2",  # Two expressions allowed so far
     help='expression for sites (eg. "alt<300', type=str)
parser.add_argument("-H","--hourly",help="using hourly file",action='store_true')
parser.add_argument("-n","--network", help="NILU or GAW", required=True)
parser.add_argument("--diurnalseason", help="season for diurnal data  (S=summer only so far)")
parser.add_argument("-t","--table", help="Table with site data ", required=True)
parser.add_argument("-y","--year", help="give year", type=int,required=True)
parser.add_argument("--label", help="label text",type=str,required=True)
#parser.add_argument("-o","--odir", help="output dir",nargs='?',const='./',default='./')
parser.add_argument("-o","--odir", help="output dir",default='.')
args = parser.parse_args()
print(args)
year     = args.year
emepfile = args.mod
network  = args.network
obsTable = args.table
obs_dir  = args.obs_dir      #obsTable='%s/TabSites_O3_%s.txt' % ( obs_dir, year )
if args.odir:
  os.makedirs(args.odir,exist_ok=True)
odir     = args.odir + '/'
dbgSite  = args.dbgSite
if( not os.path.isfile(obsTable) ):
  sys.exit(dtxt+"File %s doesn't exist!"% obsTable )

modvar='EUAOT40_Forests'
if args.hourly: modvar='SURF_ppb_O3'
# Metrics:
skeys = sorted(list(defmetrics.keys()))  # sort list to avoid radomness!
if Dummy:
  skeys = ['Dmax'] # .splot

#---------- reads NILU  AOT40 values
# #Tabulated from ../DATA_O3/stations_ozone_Sep2018.txt ..
# scode  code       name                       degN       degE       alt
# AM01   AM0001R    Amberd                  40.3844    44.5211   2080.00
# AT02   AT0002R    Illmitz                 47.7667    17.5333    117.00
# AT03   AT0003R    Achenkirch              47.5500    12.4333    960.00


# For some reason, 'comments' didn't work
sites=np.genfromtxt(obsTable,dtype=None,names=True,comments='#',skip_header=1)
#scodes=[ x.decode('utf-8') for x in sites['Site'] ]
#sName=[ x.decode('utf-8') for x in sites['Name'] ]
#sReg=[ x.decode('utf-8') for x in sites['Region'] ]
#slon=sites['Lon']
#slat=sites['Lat']
#sAlt=sites['Alt']
scodes = [ x.decode() for x in sites['scode'] ]  # eg NO01
codes  = [ x.decode() for x in sites['code'] ]   # eg NO0001R
sName  = [ x.decode() for x in sites['name'] ]
sReg   = [ 'EMEP' for x in sites['alt'] ]  # No regions defined for NILU
slon   = [ x          for x in sites['degE'] ]
slat   = [ x          for x in sites['degN'] ]
sAlt   = [ x          for x in sites['alt'] ]


sRegCodes = []
for n, s in enumerate(scodes):
  if network == 'GAW':
    sRegCodes.append( sReg[n]+'_'+s )
  else:
    sRegCodes.append( s )
  print('CODING ', n, s, sReg[n], sRegCodes[n] )

mout=dict()
for kk in skeys:
   olabel = '%s_%s'% ( kk, args.label)
   mout[kk]=open(odir+'TableOzoneMetrics_%s' % olabel,'w')
   mout[kk].write('SITE             dN     dE    Alt      Obs   dc      Mod\n')

#for line in open(obsTable,'r'):
#  #             CODE   dN    dE    Alt  AOT  AOTco  dc
#  #r=re.match('\s*(\w+)\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d',line)
#  r=re.match('\s*(\w+)\s+(\d+).*',line)
#  if r: # print r.groups() code= r.groups()[0] nums=re.findall(r'\s+[-+]?[\d\.\d]+',line) if nums: print nums
#    tokens=line.split()
#      fullcode = r.groups()[0]
#      scode.append( fullcode[0:2] + fullcode[4:6] ) # e.g AT0031R -> AT31

print(dtxt+"Testing  ", emepfile)
if( not os.path.isfile(emepfile) ):
   sys.exit(dtxt+"File %s doesn't exist!"% emepfile )

# Get EMEP data structure
if Dummy:
  emep='Dummy'
else:
  emep  = readcdf.readcdf( emepfile, modvar, getVals = True )
if emep=='VarNotFound':
  sys.exit(':'.join([dtxt,modvar,emep,emepfile]))

#emep.printme()

# for seasonal work

nmdays = calendar.mdays   # -> 0, 31, 28, ...
if calendar.isleap(year) : nmdays[2] = 29
nydays = sum ( nmdays )
# FAILED; see https://stackoverflow.com/questions/15516413/dict-fromkeys-all-point-to-same-list#15516482
#obsout = odict.fromkeys(skeys,[]) # Will have AOT40  y1 y2
# could also try obsout = {key: [] for key in skeys }
obsout = dict((key, []) for key in skeys ) # Will have AOT40  y1 y2
modout = dict((key, []) for key in skeys ) # Will have AOT40  y1 y2
codeout = dict((key, []) for key in skeys ) # Will have AOT40  y1 y2

MIN_DATA_CAPTURE = 75.0  # threshold for % acceptable values

# --- loop over sites ---------------

#for nsite, scode in  enumerate(scodes):
for regcode  in  sorted(sRegCodes):
   nsite = sRegCodes.index(regcode) # Sorting has changed order
   scode=scodes[nsite]
   code =codes[nsite]
   alt  =sAlt [nsite]

   if args.dbgSite:
     if scode != dbgSite: continue
   print ('DBG ', dbgSite, scode )

   if args.expr:
    if eval(args.expr): print("!! MATCH: EXPR ", args.expr, scode)
    else:
       print("NO MATCH: EXPR ", args.expr, scode)
       continue

   if args.expr2:
    if eval(args.expr2): print("PASSES: EXPR2 ", args.expr2, scode)
    else:
       print("FAILS: EXPR2 ", args.expr2, scode)
       continue
   print('PROCESSING ', scode)


   if network == 'GAW':
     obs_files=glob.glob('%s/y%s/%s*O3_%s.txt' % ( obs_dir, year, scode, year ))
     obs_file=obs_files[0]
     if( not os.path.isfile(obs_file) ):
        sys.exit(dtxt+"File %s doesn't exist!"% obs_file )
     if len(obs_files) > 1 : sys.exit(dtxt+'Too many matching files!')
     obs=np.genfromtxt(obs_file,dtype=None,names=True)
     o3obs=obs['ppb']
     print('OBS ',  obs_file)
   else:
     obs_file='%s/%s/%s_%s.dat' % ( obs_dir, year, code, year )
     if( not os.path.isfile(obs_file) ):
        continue
     o3obs=read_nilu_ozone(obs_file,year,flat=True)

   if( not os.path.isfile(obs_file) ):
      sys.exit(dtxt+"NILU File %s doesn't exist!"% obs_file )


   #if sAlt[nsite] > 600: 
   #   print('Too high, skip : ', nsite, scode, regcode, 
   #          sName[nsite], sAlt[nsite]  )
   #   continue
   #print('Proceeding with: ', nsite, scode, regcode, sName[nsite]  )

   #for fake in range(5):
   if Dummy:
     o3mod = 41.0*np.ones(nydays*24)
   else:
     o3mod = readcdf.get_vals( slon[nsite], slat[nsite], emep,minmax=False, dbg=False )

   if o3mod[0] == np.nan:
     print('WARNING: scode out of domain ',scode)
     continue
   if (len(o3mod) < 10 ):
     print('!!!! WARNING: out of domain ',scode, o3mod)
     continue
   timezone = int( slon[nsite]/15.0 )
   if args.dbgSite: 
     for h in range(32):
       print('HHDBG', h, o3obs[h], o3mod[h], timezone )
   if timezone>0:
     #print('TZ corr0', scode, timezone, o3obs[:12] )
     o3obs = np.roll(o3obs, timezone )
     o3obs[:timezone] = np.nan
     #print('TZ corr1', scode, timezone, o3obs[:12] )
     o3mod = np.roll(o3mod, timezone )

   print( 'O3MOD ', scode, len(o3obs), len(o3mod),
           ' Lon:', slon[nsite],' Lat:', slat[nsite] )
   assert len(o3obs) == len(o3mod), 'O3 unequal lengths %d %d!!' % (len(o3obs), len(o3mod))

   # ---- diurnal plots april-sept --------------
   if args.diurnalseason: # only summer 6 months coded so far
     dstart= sum(nmdays[:4]) + 1 # doy of 1st April
     dend  = sum(nmdays[:10])    # doy of 30th Sep
   else:
     dstart = 1
     dend   = nydays
   obs24, mod24, dc24 = makediurnal(o3obs,o3mod,dstart,dend)
   dcMean = np.nansum(dc24)/24.0 
   #if args.dbgSite:
   for h in range(24):
     print(dtxt+' diurn O,M:',scode, h, obs24[h], mod24[h], dc24[h] )
     print(dtxt+'mean diurn O,M, dc:',scode, np.nanmean(obs24), np.mean(mod24), dcMean )

   # plotlabel is e.g. EUR_MHD_2012_rv4_16feb7
   plotlabel='%s_%s_%s' % ( sRegCodes[nsite], args.label, year )

   note = '%s %s (%dm)\n days %d - %d\n DC %d(%%)' % ( 
           scode, sName[nsite], int(sAlt[nsite]), dstart, dend, int(0.5+dcMean) )
   ofile = odir+'Diurn_O3_%s.png' % plotlabel
  # plotdiurnal(odict(mod=mod24,obs=obs24), yaxisMin=0.0,
  # Sadly, the ordering of odict needs step-by-step. Give obs first
   plotinputs=odict()
   plotinputs['obs'] = obs24
   plotinputs['mod'] = mod24
   plotdiurnal(plotinputs, yaxisMin=0.0, notetxt=note, ynote=0.75,notefont=18,
     title=args.label,ofile=ofile)
   # ---- end diurnal ----------------------------


   obs_daily = dict( (key, []) for key in skeys )
   mod_daily = dict( (key, []) for key in skeys )
   dc_daily  = dict( (key, []) for key in skeys )

   nhh = 0  # tracks hours

  # -- loop over months collecting sums and nums
   for jd in range(nydays): 

    # Get_metrics will take care of -999 etc to np.nan
     #print('O3obs ',scode, o3obs[nhh], o3obs[nhh+23], np.max(o3obs[nhh:nhh+24]) )
     #print('O3obs ',scode, mm, dd, nhh, len(o3obs[nhh:nhh+23]) )
     #print('O3mod ',scode, mm, dd, nhh, len(o3mod[nhh:nhh+23]) )

    # timezone? we keep O3 values within each day, but cycle them to get
    # right period for eg AOT40

     #if dbgSite: print('OBS KEYS', skeys)
     obs_metrics = get_metrics( o3obs[nhh:nhh+24],keys=skeys, dbg=False )
     mod_metrics = get_metrics( o3mod[nhh:nhh+24],keys=skeys, dbg=False )

     #if dbgSite: print('OBS_METR', obs_metrics)

     for kk, vvpp in obs_metrics.items():  # e.g. dmean [34.5, 97]
         vv, pp = vvpp # value and percentage valid hours
         if pp < MIN_DATA_CAPTURE :
             vv = np.NaN
         elif accumulated[kk] == True :
             vv = vv * 100.0/pp   # Sums need to be scaled for eg AOT40

         obs_daily[kk].append( vv )
         dc_daily[kk].append( int(0.5+pp) )

     for kk, vvpp in mod_metrics.items():  # e.g. dmean [34.5, 97]
         vv, pp = vvpp # value and percentage valid hours
         mod_daily[kk].append( vv )
         #print('VV ',kk, vv, len( mod_daily[kk]))

     nhh += 24

   # ---- daily   plots -------------------------
   jdays=list(range(1,nydays+1))

   ofile=odir+'Daily_ppb_DmaxO3_%s.png' % plotlabel
#   note = '%s %s (%dm)' % ( scode, sName[nsite], int(sAlt[nsite]) )
   note='%s %s %s\n%5.1fN %5.1fE %5dm' % ( sReg[nsite], scode, 
         sName[nsite], slat[nsite], slon[nsite], sAlt[nsite])
   if scode == dbgSite:
      for tmpn, tmpobs in enumerate(obs_daily['Dmax']):
         print('MHD', tmpn, tmpobs, mod_daily['Dmax'][tmpn])
   plotdaily(jdays,obs_daily['Dmax'],mod_daily['Dmax'],
             yaxisMin=0.0,
             notetxt=note, ynote=0.85,notefont=18,
             addStats=True,dcLimit=50, 
             title=args.label,ofile=ofile)

#   sys.exit()
   # ---- end daily plots -------------------------
  # Now, annual stats

   dbgS = scode == 'MHD'
   for kk in skeys:

       mm1=1; nmm=12
       if 'AOT' in kk or kk.startswith('M'): # M7, M12, AOT40
          mm1 = 4; nmm = 6
          if slat[nsite]  < 0.0: mm1 = 10

      # Seasonal metrics will return the full-season value
      # for each metric, typically corrected for missing
      # days, but with strict criteria (least 75% each month)

       mod_full, seasonDC = getSeasonalMetrics(year, \
             mod_daily[kk], kk, mm1,nmm,accumulated[kk],dbg=False)

       obs_year,seasonDC = getSeasonalMetrics(year, \
             obs_daily[kk], kk, mm1,nmm,accumulated[kk],dbg=dbgS)

       if dbgS:
           day=61
           print('MHDDAYa'+kk,day, obs_daily[kk][day],mod_daily[kk][day])

       if np.isfinite(obs_year):

           print('TEST kk S   ', kk, regcode, obs_year  )
           if 'AOT' in kk:
               obs_year *= 0.001
               mod_full *= 0.001
#NO!           seasonal_corr  = seasonal_obs[kk]* 100.0/seasonDC

           #regcode= sReg[nsite]+'_'+scode
           mout[kk].write('%-12s %6.1f %6.1f %6.1f %8.3g %4d %8.3g\n' % (
               regcode, slat[nsite], slon[nsite], sAlt[nsite],
               obs_year, seasonDC, mod_full ))

           obsout[kk].append( obs_year)
           modout[kk].append( mod_full)
           codeout[kk].append( regcode )

       print('KK', scode,  regcode, kk, obs_year, mod_full, seasonDC )

for kk in skeys:
  x=obsout[kk][:]
  y=modout[kk][:]
  c=codeout[kk][:]
  print(dtxt+'PLOTTING LENS ',kk,len(x), len(y), len(c), type(x), type(y) )
  if len(x) < 2:
    print(dtxt+'SKIPPING ', kk)
    continue
  
  label=kk
  label = '%s:%s'% ( kk, args.label)
  olabel = '%s_%s'% ( kk, args.label)
  ofile=odir+'ScatPlot%s_%s.png' % ( olabel, year )
  print('PLOTTING ',ofile, kk,  x[:3], y[:3], c[:3], type(x), type(y) )
  print('PLOTTING ',kk,  x[:3], y[:3], c[:3], np.max(x), np.max(y) )
  #sys.exit()
  assert len(x) == len(y), 'XY ERROR %d %d!!' % (len(x), len(y))

  slope, const, rcoeff = emepscatplot(x,y,xlabel='Obs.', ylabel='Mod.',
  label=label,labelx=0.01,labely=0.93,
  addStats=True,pcodes=c,ofile=ofile)

  ofile=odir+'Stats%s_%s.txt' % ( olabel, year )
  f=open(ofile,'w')
  f.write('%7.2f %7.2f %8.3f\n' % ( slope, const, rcoeff ))
  f.close()
#if args.ofile:
#  ofile=args.ofile
#else:
#  ofile='ScatPlot%d.png' % year

#if args.label:
#  txtlabel=  r"%s" % args.label
# Sruggling here, see
# https://www.reddit.com/r/learnpython/comments/661qpp/print_newline_n_python3/
# https://stackoverflow.com/questions/46769234/python-print-newline-sometimes-does-not-work-why
#  f"Name is {txtlabel!s}"
# Checking 
#  print("txtlabel %s"%txtlabel, type(txtlabel))
#  print("txtlabel %s"%str(txtlabel), type(txtlabel))
#  print("txtlabel", txtlabel[1])
#  print(0,'\nhello\nworld')#[1]
#  print(0, type(txtlabel))
#  print(txtlabel)
#  print(('%s' % (txtlabel)))
##  print(('%s' % txtlabel.decode('utf8')))
##  sys.exit()
#else:
#  txtlabel = 'Year %d' % year

#plt.scatter(obsaot,modaot,xlabel='Obs. AOT40', ylabel='Mod. AOT40') #,txt=emepfile) #,addStats=True)
#for n, m in enumerate(modaot):
#  print('NMM', n, obsaot[n], m, obscode[n] )
#EmepScatPlots.EmepScatPlot(obsaot,modaot,xlabel='Obs. AOT40', ylabel='Mod. AOT40',
#  label=txtlabel,labelx=0.01,labely=0.93,
#  addStats=True,pcodes=obscode,ofile=ofile)
#  #NOV2017 txt='Year %d '%year,addStats=True,pcodes=scode,ofile=ofile)
#  #OCT2017  txt=emepfile,addStats=True,pcodes=scode)
#if args.ofile:
# plt.savefig(args.ofile)
#else:
# plt.show()
