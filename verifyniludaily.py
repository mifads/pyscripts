#!/usr/bin/env python3
"""
  Used to compare modelled daily average concentrations of inorganic pollutants
 (NO2, SO2, etc., but not O3) with EMEP/CCC observations. The latter are stored in
 a pre-processed directory, which on Dave's systems is at:
     ~/Data/PROCESSED/NILU/Main_daily
  Main_daily/
  2000, 2001, ... 2014
  TabNilu
  README.md
  LIST
"""
import argparse
from   collections import OrderedDict as odict
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import emxmisc.emepstats as emepstats
import emxplots.plotdaily as plotdaily
import emxplots.plotscat  as plotscat
import emxcdf.readcdf as readcdf   # Reads netcf
from   emxverify.ebas_flags import get_ebasflags

#------------------ arguments  ----------------------------------------------
# This script assumes files are in the default locations specified...
# Only dealt with O3 so far, since other pollutants are obrtained from
# daily file processing, not hourly metrics

parser=argparse.ArgumentParser()
parser.add_argument('-i','--ifile',help='Input model day.nc file',required=True)
parser.add_argument('--ObsDir',help='Directory with TabNiluMain.txt (and yyyy sub-directories). Needed if not in ~/Data/PROCESSED/NILU/Main_daily',required=False)
parser.add_argument('-o','--odir',help='Output directory', default='TMPPLOTS',required=False)
parser.add_argument('-r','--runlabel',help='Run label',required=True)
parser.add_argument('-n','--noplots',help='Skip daily plots',required=False)
parser.add_argument('-y','--year',help='year',required=True)
args=parser.parse_args()
#args=vars(parser.args())
#print('ARGS', args)
emepfile = args.ifile


#------------------ directory setup -----------------------------------------

year = args.year #  2012
home=os.getenv('HOME')
cdir=os.getcwd()
ymax = { 'o3':140.0, 'co':600.0, 'no2':32.0} # plotting limits
if args.ObsDir is None:
  tdir='%s/Data/PROCESSED/NILU/Main_daily' % home
else:
  tdir=args.ObsDir
obs_dir='%s/%s/' % ( tdir, year )
niluTab='%s/TabNiluMain.txt' % tdir  # site locations, names, altitudes, etc
obs_flags = get_ebasflags()


#------------------ component definitions -----------------------------------------
nilumap=odict()
# Give in likeliest order
# consistent with 1ppb O3=2.0 ug/m3
nilumap['nh3']=dict( obs='NH3_air',obsUnit='ugN/m3' , 
                  modvars=[ 'ug_NH3', 'ugN_NH3', 'ppb_NH3'],
                  modconv=[  14.0/17,     1.0,    0.708   ])
nilumap['nhx']=dict( obs='NH3+NH4_air+aerosol',obsUnit='ugN/m3' , 
                  modvars=[ 'ugN_RDN', ], modconv=[    1.0,    ] )
nilumap['no2']=dict( obs='NO2_air',obsUnit='ugN/m3' , 
                  modvars=[ 'ug_NO2', 'ugN_NO2', 'ppb_NO2'], 
                  modconv=[  14.0/46,     1.0,    1.92    ]  )
nilumap['no3']=dict( obs='NO3_aerosol',obsUnit='ugN/m3' , 
                  modvars=[ 'ug_NO3_F', 'ugN_NO3_F', 'ppb_NO3_F'], 
                  modconv=[  14.0/62,     1.0,    2.583   ]  )
nilumap['hno3']=dict( obs='HNO3_air',obsUnit='ugN/m3' , 
                  modvars=[ 'ug_HNO3', 'ugN_HNO3', 'ppb_HNO3'],
                  modconv=[  14.0/63,     1.0,    2.625   ])
nilumap['so2']=dict( obs='SO2_air',obsUnit='ugS/m3' , 
                  modvars=[ 'ug_SO2', 'ugS_SO2', 'ppb_SO2'], 
                  modconv=[  14.0/64,     1.0,    2.67    ]  )
#Only have non-seasalt from model
#nilumap['so4']=dict( obs='SO4_aerosol',obsUnit='ugS/m3' , 
#                       modvars=[ 'ug_SO4' ], modconv=[  32.0/96 ] )
nilumap['so4nss']=dict( obs='XSO4_aerosol',obsUnit='ugS/m3' , 
                       modvars=[ 'ug_SO4' ], modconv=[  32.0/96 ])

# CHECK ugN_OXN ugN_OXN????
# CAN'T DO properly? Model has ug/m3, but HNO3 and NO3 are extremely
# similar in MW. Use NO3
nilumap['tno3']=dict( obs='HNO3+NO3_air+aerosol',obsUnit='ugN/m3' , 
                       modvars=[ 'ug_TNO3', ],
                       modconv=[  14.0/62,  ] 
)
nilumap['wno3']=dict( obs='NO3_precip',obsUnit='ugN/m2' , 
                       modvars=[ 'WDEP_OXN', ],
                       modconv=[  14.0/46,  ] 
)

out_dir=args.odir   # for output
if not os.path.exists(out_dir):
  os.makedirs(out_dir)

#------------------ get observatio site details from file ------------
intab=np.genfromtxt(niluTab,names=True,dtype=None)
outtab=open('Res_%s_%s.txt' % ( year, args.runlabel ), 'w')  # Keep Res_ style for scanVerify
outtab.write('RESULTS: Year %s\n%s\n' %(year, "="*50 ))

for poll in  nilumap.keys(): # 'no2', :

  #if poll != 'no2':
  #  continue
  obs_comp=nilumap[poll]['obs']
  obs_unit=nilumap[poll]['obsUnit']

  # Prepare output table headers and arrays
  outtab.write( obs_comp + '  ' + obs_unit + '\n' )
  outtab.write("-"*78 + '\n' )
  outtab.write("  Period DC   Ns    Np   pc<30% pc<50%      Obs      Mod    Bias  Rmse  Corr   IOA\n")

  obs_stat = []  # for all stations
  mod_stat = []
  obs_site = []  # for all stations

 # Get emep concentrations for full grid, all days
  modFound=False
  for nvar, var in enumerate( nilumap[poll]['modvars'] ) :
       surf_var=var
       if not 'precip' in obs_comp:
          surf_var='SURF_' + var
       print('Search for ', nvar, obs_comp, surf_var )
       EmepFile = readcdf.readcdf( emepfile, surf_var, getVals = True ) # 180 from ECHAM day.nc
       if EmepFile == 'VarNotFound':
          print('Notfound ', nvar, obs_comp, surf_var )
          continue # try again
       else:
          modFound = True
          convfac = nilumap[poll]['modconv'][nvar] 
          break
       
  if not  modFound:
      print('PROBLEM cannot find ',poll, obs_comp, ' in ', nilumap[poll]['modvars'] )
      sys.exit()
  print('Found  ', surf_var, ' Conv ', convfac )

  ########## Now, the stations ##########################################
  for code, name, degN, degE, alt in zip( intab['code'], intab['name'], 
      intab['degN'], intab['degE'], intab['alt'] ) :

    scode=code.decode('utf-8')
    if alt > 500.0:
      print('SKIP too high ', scode, alt )
      continue

    obsfile="%s/%s_%s_%s.txt" % ( obs_dir, scode, obs_comp, year )
    if not os.path.exists(obsfile):
      continue
    print(scode, poll, obsfile, degN, degE)
    #if scode=='SE14': sys.exit()
    #PROBLEMS obsdata = np.genfromtxt(obsfile)  #   1 2012  1  1    1.80   000000000
    # dtype setting is hard!
    jdays = []; obs=[]; flags=[]
    with open(obsfile,'r') as ob:
       lines = ob.readlines()
       for nl, line in enumerate(lines):
          jd, conc, flag4 = line.split()
          flag=flag4[:3] # NILU MAin has 4 digits, ending in zero
          jdays.append(int(jd))
          flags.append(flag)
          conc=float(conc)
          
          # NILU data have -99(9) flags as well as Ebas-style:
          if int(flag)> -1 and  obs_flags[flag] == 'V' and conc > -0.0001 : 
             obs.append(conc)
              #  print(nl, jd, obs[nl] )
          else:
             obs.append(np.nan)

    #mod, modmin, modmax  = getEmepVal(degE,degN,EmepFile,minmax=True) 
    mod, modmin, modmax  = readcdf.get_vals(degE,degN,EmepFile,minmax=True) 
               # e.g. MaceHead is at 53.3, -9.89 

    mod    *= convfac
    modmin *= convfac
    modmin *= convfac
   
    print(scode, len(obs),len(mod), var, convfac )

    stats=emepstats.obsmodstats(obs,mod,dbg=True)
    if stats['dc'] > 75:
       print('POLL ', poll, nilumap )

       if not args.noplots:
          title='Daily %s (%s), %s, %s' % ( obs_comp, obs_unit, scode, year )
          note  = '%s\n' % name.decode('utf-8')
          note += '%.2f degE %.2f degN %5dm\n' % ( degE, degN, alt )
          note += 'Run: %s\n' % args.runlabel
          note += 'Bias %d R=%4.2f' % ( stats['bias'], stats['R'] ) 
          ofile='%s/Daily_%s_%s_%s_%s.png' % ( out_dir, obs_comp, scode, year, args.runlabel )
          print('DPLOT ' , scode, ofile )
          plotdaily.plotdaily(jdays,obs,mod,title=title,
             notetxt=note,ynote=0.75,ofile=ofile,dbg=False)

       obs_site.append( scode )
       obs_stat.append( stats['meanx'] )
       mod_stat.append( stats['meany'] )
       print('NOBS ' , scode, len(obs_site))
    else:
       print('XOBS ' , scode, len(obs_site))
       continue

  print('OBS ' , obs_site)
  #outtab.write("  Period CDays   Ns    Np   pc<30% pc<50%        Obs      Mod     Bias  Rmse  Corr   IOA\n")
  outtab.write("  Annual %d   %d    Np   pc<30 pc<50     %6.2f   %6.2f  %6.1f  Rmse  %6.2f   IOA\n" % (
    stats['dc'], len(obs_site), stats['meanx'], stats['meany'], stats['bias'], stats['R'] )
  )
  outtab.write("-"*78 + '\n' )

  # Scatter plots:
  if len(obs_site) > 2:
    #title='%s (%s), %s, %s' % ( obs_comp, obs_unit, year, args.runlabel )
    title='%s, %s' % ( args.runlabel, year )
    ofile='%s/ScatPlot_%s_%s_%s.png' % ( out_dir, obs_comp, year, args.runlabel )
    plotscat.emepscatplot(obs_stat,mod_stat,xlabel='Obs.',ylabel='Mod.',
       title=title,
       pcodes=obs_site,addStats=True,
       label='%s (%s)' % (obs_comp, obs_unit), ofile=ofile )

#NN#------------------ metrics and log files -----------------------------------
#NNLog = {}
#NNline="="*96
#NN
#NNsortkey='degN'
#NN#sorted_codes=sorted(db.items(), key=lambda x: x[1][sortkey],reverse=True)
#NN
#NNfor kk in skeys:
#NN
#NN  Log[kk]=open('%s/LOG_%s_%s_%s.txt'% ( out_dir, kk, run, year), 'w' )
#NN  Log[kk].write('%-20s %-20s %5sN %6sE %5s %5s %3s %7s %7s %5s%% %5s\n' %
#NN  ( 'Site', 'Country', 'Lat', 'Lon', 'Alt', 'Ind', 'DC', \
#NN    'Obs', 'Mod', 'Bias', 'Corr'))
#NN  Log[kk].write('%s\n' % line )
#NN
#NN#------------------ site       ----------------------------------------------
#NN
#NN  #DB for s in range(0,len(sorted_codes)):
#NN  for icode in range(len(db)):
#NN     S=db.loc[icode]  # one row of site data
#NN     name, code, lat, continent, alt = S.name, S.code, S.degN, S.Cont, S.alt
#NN     #code= sorted_codes[s][0]
#NN     #lat = db[code]['degN']
#NN     xcode = continent + '_' + code
#NN     print('TEST SORT ', code, lat )
#NN#------------------------------------
#NN 
#NN     if code == 'ATEST': continue
#NN     dbgSite = (code == 'ALG')
#NN     if alt > 300:
#NN       print('Skipped high elev., ', xcode, name, alt)
#NN       continue
#NN     country, lon, Ind, tz = S.Country, S.degE, S.Ind, S.tz 
#NN
#NN     print('OBS ',  code, alt, lat, lon )
#NN
#NN
#NN#------------------ metrics    ----------------------------------------------
#NN
#NN     obs_file=obs_dir + '/Daily%s_%s_%s.dat' % ( kk, xcode, year )
#NN     if  not os.path.isfile(obs_file):
#NN         print('NO FOLE !!!', kk, xcode ); continue  # TMP 
#NN     obs_data =np.loadtxt(obs_file)
#NN
#NN     mod_file=mod_dir + '/EMEP_Daily%s_%s_%s.dat' % ( kk, code, year )
#NN
#NN     if os.path.isfile(mod_file):
#NN       mod_data =np.loadtxt(mod_file)
#NN       if mod_data.shape[0] < 365 or mod_data.shape[1] == 3:
#NN         print('NOT YET PROCEESED ', code); continue  # TMP 
#NN     else:
#NN         print('NOT YET PROCEESED ', code, mod_file); continue  # TMP 
#NN
#NN     if os.path.isfile(obs_file):
#NN       jday   = obs_data[:,0]
#NN       obs_dc = obs_data[:,1]
#NN       obs    = obs_data[:,2]
#NN     else:
#NN       sys.exit('FILE SHOULD EXIST ', obs_file)
#NN
#NN     jday   = mod_data[:,0]
#NN     mod_dc = mod_data[:,1]
#NN     mod    = mod_data[:,2]
#NN     modmin = mod_data[:,3]
#NN     modmax = mod_data[:,4]
#NN
#NN     f    = np.isfinite(obs)
#NN     nbad = np.isnan(obs).sum()
#NN     dc = (len(jday)-nbad)/(0.01*len(jday))
#NN
#NN     meanobs = np.nanmean(obs)
#NN     meanobs2= np.mean(obs[f])
#NN     meanmod = np.mean(mod[f])
#NN
#NN     bias = -999; r= -99.0
#NN     if meanobs > 0:
#NN       bias = int( 0.5+  100*(meanmod - meanobs)/meanobs )
#NN       r=np.corrcoef(obs[f],mod[f])[0,1]
#NN
#NN     print('MEANS ', meanobs, meanobs2, meanmod, bias, r)
#NN
#NN     #if  'Alert' in name:
#NN     if alt > -1: # All stations!  < 10.0:
#NN       plt.clf()
#NN       if ( dc < 190.0 ): # Add markers
#NN          #plt.plot(jday,obs,lw=1.5,color='g',label='Obs',marker='o')
#NN          plt.plot(jday,obs,lw=1.5,color='g',label='Obs')
#NN          plt.plot(jday,obs,lw=1.5,color='g',label=None)
#NN          #plt.plot(jday,obs,lw=1.5,color='g',label=None,marker='o')
#NN          #f = np.isnan(obs)
#NN          #plt.plot(jday[f],obs[f],lw=1.5,color='g',label=None,marker='o')
#NN          xmarks = []; ymarks = []
#NN          for i in range(1,365):
#NN              if np.isfinite( obs[i] ):
#NN                 if np.isnan(obs[i-1]) and np.isnan(obs[i+1]):
#NN                   xmarks.append(i); ymarks.append( obs[i] )
#NN          if len(xmarks)>0:
#NN              plt.plot(xmarks,ymarks,linestyle='None',color='r',label=None,marker='+',markersize=5)
#NN                    
#NN          #      print('MBI ',iday,jday[iday],obs[iday], f[iday] )
#NN          #  sys.exit('MBI')
#NN       else:
#NN          plt.plot(jday,obs,lw=1.5,color='g',label='Obs')
#NN           #plt.plot(jday[f],obs[f],lw=1.5,label='Obs')
#NN          print("CPOMP ", name, len(jday), len(mod))
#NN       plt.plot(jday,mod,'--',lw=1.5,color='b',label='Mod')
#NN       plt.fill_between(jday,modmin,modmax,color='b',alpha=0.1)
#NN       plt.title('Daily %s (%s), %s, %s'% ( kk, poll, name, year) )
#NN       plt.xlim([1,366])
#NN       #ymax=140.0
#NN       #if( poll == 'co' ) : ymax = 600.0
#NN       #if( poll == 'no2' ) : ymax = 32.0
#NN       plt.ylim([0.0,ymax[var]])
#NN       plt.figtext(0.15,0.85,'%s: %s (%s)' % ( country, code , continent ))
#NN       plt.figtext(0.15,0.80,'%5.1fN %5.1fE %5dm' % ( lat, lon, alt ))
#NN       plt.figtext(0.15,0.75,'Run: %s' %  run )
#NN       plt.figtext(0.15,0.70,'Bias %3d%%   R=%4.2f' % ( bias, r) )
#NN       plt.figtext(0.15,0.65,'Ind. %5.1f' % Ind )
#NN       plt.legend()
#NN       srun=run
#NN       #png='%s/Daily_%s_%s_%s_%s_%s.png'% ( out_dir, kk, country[0:11], xcode, srun, year)
#NN       png='%s/Daily_%s_%s_%s_%s_%s.png'% ( out_dir, kk, xcode, country[0:11], srun, year)
#NN       plt.savefig( png )
#NN       plt.close()
#NN
#NN       print('%-20s %-20s %6.1f %7.1f %5d %3d %7.1f %7.1f %5d %6.2f\n' %
#NN          ( kk + name[0:18], country[0:18], lat, lon, alt, dc, meanobs, meanmod, bias, r) )
#NN       Log[kk].write('%-20s %-20s %6.1f %7.1f %5d %5.1f %3d %7.1f %7.1f %5d %6.2f\n' %
#NN          ( name[0:18], country[0:18], lat, lon, alt, Ind, dc, meanobs, meanmod, bias, r) )
#NN     
#NN
#NN  Log[kk].close()
#NN  # --- all sites done now.
#NN
#NN#------------------ EMEP input ----------------------------------------------
#NN
