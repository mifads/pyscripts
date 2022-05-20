#!/usr/bin/env python3
""" Should test further against template from
   https://ebas-submit.nilu.no/templates/master/master
"""

import calendar
import datetime as dt
import glob
import numpy as np
import os
import sys


flags=[]
invalid= [ 251, 256, 259, 260,  277, 278, 389, 391, 393, 395, 451, 452, 456, 459,
 460, 471, 477, 478, 530, 533, 534, 540, 541, 549, 565, 566, 567, 568,
 578, 591, 593, 599, 620, 635, 641, 646, 658, 659, 663, 664, 666, 669,
 670, 677, 681, 682, 683, 684, 685, 686, 687, 699, 701, 750, 783, 784,
 799, 890, 899, 900, 980, 990, 999 ]


# e.g. SI0008R.20140101073000.20210615130447.low_vol_sampler.organic_carbon.pm25.1y.1d.SI01L_ARSO_pm25vz_2.SI01L_ARSO_ECOC_1.lev2.nas

def read_ebas_site(ifile,poll_wanted,syear,eyear,dbg=False):

   assert os.path.isfile(ifile)
   print('SITEBB', poll_wanted )
   site=dict()
   """
   starttime endtime OC flag_OC
     3   4  1.942 0.470
     7   8  1.657 0.470
   """
   # we base start time on input request
   startdate=dt.datetime(syear,1,1)
   enddate  =dt.datetime(eyear,12,31)
   if poll_wanted=='eBCbb':
     startdate=dt.datetime(2017,12,1)
     enddate  =dt.datetime(2018,3,1)
   ndays= (enddate-startdate).days + 1
   nhours= (enddate-startdate).total_seconds()/3600. + 1
   hourlyData = False
   if dbg: print('NDAYS ', ndays, nhours)

   assert os.path.isfile(ifile),'ebasFILE MISSING!'+fname

   fname=os.path.basename(ifile)
   print('IN:', fname)
   if poll_wanted=='eBCbb':
       code = fname.replace('_absorption_20171201_3mo_PMF_lev3.nas','')
       hourlyData = True
   else:
       code=fname[:7]
     #if code != 'ES1778R': continue
     #print(site_wanted, code ); sys.exit()

   nvals = ndays
   if hourlyData: nvals *= 24  # No. hours
   if dbg: print('SITE CODES',  code)

   site['code']   = code
   site['vals']   = np.full(nvals,np.nan)  #  store data here
   site['flag']   = np.full(nvals,999,dtype=int)    #  zero -> valid flag
   site['t1']     =  [None] * nvals # np.full(ndays,np.nan)  # 
   site['t2']     =  [None] * nvals # p.full(ndays,np.nan)  # 
   site['period'] =  [None] * nvals
   site['dc']     = 0.0
   
   indata = False
   
   syy=-1;eyy=-1
   with open(ifile) as f:
   
         lines=f.read().splitlines()
         
         for nline, line in enumerate(lines):
           if dbg: print(nline, line)

           fields=line.split()
           if nline == 6:  # reference start and end date
               [ syy, smm, sdd, eyy, emm, edd ] = [ int(k) for k in line.split() ]
               print('START EBAS',  syy, eyy,  syear, eyear )
               if syy<syear and eyy<syear: break
               if syy>eyear and eyy>eyear: break
               t0 = dt.datetime(syy,smm,sdd)
               continue

           if not indata:
              if line.startswith('starttime') or line.startswith('start_time'): # EIMPS had start_time
                indata=True
                s = site
                sitelon = float(s['Station longitude'])
                sitelat = float(s['Station latitude'])
                sitealt = int(s['Station altitude'].replace('m','').replace('.0','') )
                sitename= code + '_' + '_'.join(s['Station name'].split()) # copes with \t too
      
                # often one is missing. Sample dur better for sample length,
                # Res. should be better for data capture
                resCodes=[ 'Sample duration', 'Resolution code' ]
                sample='UNDEF'
                for rc in resCodes:
                 if rc in site.keys():
                   sample = site[rc].replace(" ","")
                   print('SAMPLING ', code, rc, sample )

              elif ':' in line: #  nline  > 18:
                 lhs, rhs = line.split(':',maxsplit=1)
                 site[lhs] = rhs  # NB can be 2 values, e.g. Station lat or Measurement lat. Confusing!
              continue
   
           print(line)
           if poll_wanted=='eBCbb':
              print(line, site_wanted)
              stime, etime, Babs_bb, Babs_ff, val, eBCff = [ float(k) for k in line.split() ]
              flag=0
              if val > 999:
                  val=np.nan
                  flag=0.999999
           else:
              stime, etime, val, flag = [ float(k) for k in line.split() ]

           flag1 = int(1000000*flag+0.001)//1000 # e.g. 0.467666 = flags 467 666
           flag2 = int(1000000*flag+0.001)% 1000
           if flag1 in invalid: continue
           if flag2>0 and flag2 in invalid: continue
           print('I:', code, t0, stime, val, flag, flag1, flag2 )
   
           if flag1 not in flags: flags.append(flag)
           if flag2 not in flags: flags.append(flag)
   

           #try:
           #  #print('CHECK Sample duration', site['Sample duration'] )
           #  sample = site['Sample duration'].replace(" ","")
           #except: # e.g. IT0004R
           #  #print('KEYERRS?', code, site.keys() )
           #  if poll_wanted=='eBCbb':
           #    sample = '1h'
           #  else:
           #    try:
           #      sample = site['Resolution code'].replace(" ","")
           #    except:
           #      print('NO RES CODE', code, site.keys() )
           if sample=='UNDEF': sys.exit('SAMPLE ERROR :'+ifile)
                

           if sample == '1d' or sample == '15h' or \
              sample == '2d': # Weird, KOS  has 2d, but anyway starttime-endtime=1d!
               t1=t0+dt.timedelta(days=stime)
               t2=t0+dt.timedelta(days=(stime+1)) # FIX, since e.g. ES used integer for 3, 4 
               txt='dmean'
           elif sample == '1w':
               t1=t0+dt.timedelta(days=stime)
               t2=t0+dt.timedelta(days=etime)
               txt='wmean'
           elif sample == '1h':
               t1=t0+dt.timedelta(hours=stime)
               t2=t0+dt.timedelta(hours=etime)
               txt='hmean'
           else:
               print('UNRECOGNISED Sample duration', sample,  fname, site.keys())
               #print('UNRECOGNISED Sample duration', site[code]['Sample duration'], fname )
               sys.exit()
           if dbg: print('ebasHERE ', code, sample,  txt, stime, val, t1, t2 )
   
           if t1<startdate: continue
           if t1>enddate: continue
           if t1.year < syear : continue
           if t1.year > eyear : continue
           if dbg: print('ebasTHROUGH',nline,  syy, eyy, val, t1, t2 )
   
           if val>199.0: # ARGH! F...ing Ebas
               print('VERROR:', os.path.basename(f.name))
               print('VERROR:', line)
               print('VERROR:', code, t0, stime, val, flag1, flag2 )
               continue
   
           if val > 0.0:
             n= (t1-startdate).days
             if hourlyData: n= int( (t1-startdate).total_seconds()/3600.0 )
             if dbg: print('ebasSETVAL',nline, n, val, t1, t2 )
             site['vals'][n] = val
             site['flag'][n] = flag
             site['period'][n] = sample
             site['t1'][n] = t1
             site['t2'][n] = t2
             site['dc']  += 1
             if poll_wanted=='eBCbb':
               site['Unit']  = 'ug/m3' 
   
             jan1 = dt.datetime(t1.year,1,1)
             doy1  = (t1-jan1).days + 1
             doy2  = (t2-jan1).days    # seems to work better without +1
   
   # end files for this site
             if dbg: print('>> %d %3d %3d %2d %2d %2d  %s  %8.3f   %d' % ( t1.year, doy1, doy2, t1.month, t1.day, t1.hour,  sample,  val, int(1.0e6*flag+0.001)  ) )
             #print('END', code, len(
   return site
   
#============================================================================

def read_ebasMulti(nasdir,site_wanted,poll_wanted,syear,eyear,dbg=False):

   #pmf='../EIMP2017-2018/EIMPs_winter2017-2018_data/EIMPs_winter2017_2018_absorption_PMF'
   assert os.path.exists(nasdir),'WRONG NAS?:'+nasdir
   if poll_wanted=='OCf':
     files=glob.glob("../Ebas_WA_20220309/%s*organic_carbon.pm25*.nas" % site_wanted )
   elif poll_wanted=='PMf':
     files=glob.glob("../Ebas_WA_20220309/%s*pm25_mass*.nas" % site_wanted )
   elif poll_wanted=='ECf':
     files=glob.glob("../Ebas_WA_20220309/%s*elemental_carbon.pm25*.nas" % site_wanted )
   elif poll_wanted=='Levo':
     files=glob.glob("../Ebas_WA_20220309/%s*levogl*.nas" % site_wanted )
   elif poll_wanted=='eBCbb':
     files=glob.glob(nasdir+"/*%s*PMF*.nas" % site_wanted ) # Now e.g. AT0002R_Illmitz_ab...
     print('SITEBB', site_wanted, poll_wanted, len(files) )
   else:
     sys.exit('INCORRECT OBS '+poll_wanted+site_wanted)
   sites=dict()
   """
   starttime endtime OC flag_OC
     3   4  1.942 0.470
     7   8  1.657 0.470
   """
   # we base start time on input request
   startdate=dt.datetime(syear,1,1)
   enddate  =dt.datetime(eyear,12,31)
   if poll_wanted=='eBCbb':
     startdate=dt.datetime(2017,12,1)
     enddate  =dt.datetime(2018,3,1)
   ndays= (enddate-startdate).days + 1
   nhours= (enddate-startdate).total_seconds()/3600. + 1
   hourlyData = False
   if dbg: print('NDAYS ', ndays, nhours, len(files) )
   assert len(files) > 0,'NO FILES!' + nasdir
   
   
   for ifile in files:
     fname=os.path.basename(ifile)
     print('IN:', fname)
     if poll_wanted=='eBCbb':
       code = fname.replace('_absorption_20171201_3mo_PMF_lev3.nas','')
       hourlyData = True
     else:
       code=fname[:7]
     #if code != 'ES1778R': continue
     #print(site_wanted, code ); sys.exit()

     nvals = ndays
     if hourlyData: nvals *= 24  # No. hours
     if code not in sites:
         sites[code] = dict()
         #sites[code]['code']   = code
         if dbg: print('SITE CODES', site_wanted, code)
         sites[code]['vals']   = np.full(nvals,np.nan)  #  store data here
         sites[code]['flag']   = np.full(nvals,999,dtype=int)    #  zero -> valid flag
         sites[code]['t1']     =  [None] * nvals # np.full(ndays,np.nan)  # 
         sites[code]['t2']     =  [None] * nvals # p.full(ndays,np.nan)  # 
         sites[code]['period'] =  [None] * nvals
         sites[code]['dc']     = 0.0
   
     indata = False
   
     syy=-1;eyy=-1
     with open(ifile) as f:
   
         lines=f.read().splitlines()
   
         for nline, line in enumerate(lines):
           fields=line.split()
           if nline == 6:  # reference start and end date
               [ syy, smm, sdd, eyy, emm, edd ] = [ int(k) for k in line.split() ]
               if syy<syear and eyy<syear: break
               if syy>eyear and eyy>eyear: break
               t0 = dt.datetime(syy,smm,sdd)
               continue

           if not indata:
              if line.startswith('starttime') or line.startswith('start_time'): # EIMPS had start_time
                indata=True
                # often one is missing. Sample dur better for sample length,
                # Res. should be better for data capture
                 #??? Sample duration:               e.g. EIMP has sample dur 1d  res code 4d
                resCodes=[ 'Sample duration', 'Resolution code' ]
                sample='UNDEF'
                for rc in resCodes:
                 if rc in sites[code].keys():
                   sample = sites[code][rc].replace(" ","")
                   print('SAMPLING ', code, rc, sample )
                if poll_wanted=='eBCbb':
                   sample = '1h'

              elif ':' in line: #  nline  > 18:
                 lhs, rhs = line.split(':',maxsplit=1)
                 sites[code][lhs] = rhs  # NB can be 2 values, e.g. Station lat or Measurement lat. Confusing!
              continue
   
           print(line)
           if poll_wanted=='eBCbb':
              print(line, site_wanted)
              stime, etime, Babs_bb, Babs_ff, val, eBCff = [ float(k) for k in line.split() ]
              flag=0
              if val > 999:
                  val=np.nan
                  flag=0.999999
           else:
              stime, etime, val, flag = [ float(k) for k in line.split() ]

           flag1 = int(1000000*flag+0.001)//1000 # e.g. 0.467666 = flags 467 666
           flag2 = int(1000000*flag+0.001)% 1000
           if flag1 in invalid: continue
           if flag2>0 and flag2 in invalid: continue
           print('I:', code, t0, stime, val, flag, flag1, flag2 )
   
           if flag1 not in flags: flags.append(flag)
           if flag2 not in flags: flags.append(flag)
   



           if sample == '1d' or sample == '15h' or \
              sample == '2d': # Weird, KOS  has 2d, but anyway starttime-endtime=1d!
               t1=t0+dt.timedelta(days=stime)
               t2=t0+dt.timedelta(days=(stime+1)) # FIX, since e.g. ES used integer for 3, 4 
               txt='dmean'
           elif sample == '1w':
               t1=t0+dt.timedelta(days=stime)
               t2=t0+dt.timedelta(days=etime)
               txt='wmean'
           elif sample == '1h':
               t1=t0+dt.timedelta(hours=stime)
               t2=t0+dt.timedelta(hours=etime)
               txt='hmean'
           else:
               print('UNRECOGNISED Sample duration', sample, fname, sites[code].keys())
               #print('UNRECOGNISED Sample duration', sites[code]['Sample duration'], fname )
               sys.exit()
           if dbg: print('ebasMHERE ', code, sample,  txt, stime, val, t1, t2 )
           #sys.exit)
   
           if t1<startdate: continue
           if t1>enddate: continue
           if t1.year < syear : continue
           if t1.year > eyear : continue
   
           if val>199.0: # ARGH! F...ing Ebas
               print('VERROR:', os.path.basename(f.name))
               print('VERROR:', line)
               print('VERROR:', code, t0, stime, val, flag1, flag2 )
               #sys.exit()
               continue
   
           if val > 0.0:
             n= (t1-startdate).days
             if hourlyData: n= int( (t1-startdate).total_seconds()/3600.0 )
             if dbg: print('ebasVHERE',nline, n, val, t1, t2 )
             sites[code]['vals'][n] = val
             sites[code]['flag'][n] = flag
             sites[code]['period'][n] = sample
             sites[code]['t1'][n] = t1
             sites[code]['t2'][n] = t2
             sites[code]['dc']  += 1
             if poll_wanted=='eBCbb':
               sites[code]['Unit']  = 'ug/m3' 
   
             jan1 = dt.datetime(t1.year,1,1)
             doy1  = (t1-jan1).days + 1
             doy2  = (t2-jan1).days    # seems to work better without +1
   
   # end files for this site
             if dbg: print('>> %d %3d %3d %2d %2d %2d  %s  %8.3f   %d' % ( t1.year, doy1, doy2, t1.month, t1.day, t1.hour,  sample,  val, int(1.0e6*flag+0.001)  ) )
             #print('END', code, len(
   return sites
   
    
if __name__ == '__main__':

  code='NO0002R'
  sites = read_ebas(code,poll_wanted='OC',syear=2015,eyear=2015)
  s = sites[code]
  vals = s['vals']

  for n in range(len(vals)):
      val = vals[n]
      if val >= 0.0:
          t1=s['t1'][n]
          t2=s['t2'][n]
          period=s['period'][n]
          jan1 = dt.datetime(t1.year,1,1)
          doy1  = (t1-jan1).days + 1
          doy2  = (t2-jan1).days
          #print(n,s['vals'][n], s['flag'][n] )
          print('%d %3d %3d %2d %2d %2d  %s  %8.3f   %d' % ( t1.year, doy1, doy2, t1.month, t1.day, t1.hour,  period,  val, s['flag'][n]   ) )

