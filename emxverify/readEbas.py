#!/usr/bin/env python3
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

def read_ebas(site_wanted,poll_wanted,syear,eyear):

   pmf='../EIMP2017-2018/EIMPs_winter2017-2018_data/EIMPs_winter2017_2018_absorption_PMF'
   print('SITEAA', site_wanted, poll_wanted )
   if poll_wanted=='OCf':
     files=glob.glob("../Ebas_WA_20220309/%s*organic_carbon.pm25*.nas" % site_wanted )
   elif poll_wanted=='PMf':
     files=glob.glob("../Ebas_WA_20220309/%s*pm25_mass*.nas" % site_wanted )
   elif poll_wanted=='ECf':
     files=glob.glob("../Ebas_WA_20220309/%s*elemental_carbon.pm25*.nas" % site_wanted )
   elif poll_wanted=='Levo':
     files=glob.glob("../Ebas_WA_20220309/%s*levogl*.nas" % site_wanted )
   elif poll_wanted=='eBCbb':
     print('SITEBB', site_wanted, poll_wanted )
     files=glob.glob(pmf+"/%s*PMF*.nas" % site_wanted )
   else:
     print('SITECC', site_wanted, poll_wanted )
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
   ndays= (enddate-startdate).days + 1
   print('NDAYS ', ndays)
   
   
   for ifile in files:
     fname=os.path.basename(ifile)
     #print('IN:', fname) sys.exit()
     code=fname[:7]
     #if code != 'ES1778R': continue
     #print(site_wanted, code ); sys.exit()
     if code not in sites:
         sites[code] = dict()
         sites[code]['vals']   = np.full(ndays,np.nan)  #  store data here
         sites[code]['flag']   = np.full(ndays,999,dtype=int)    #  zero -> valid flag
         sites[code]['t1']     =  [None] * ndays # np.full(ndays,np.nan)  # 
         sites[code]['t2']     =  [None] * ndays # p.full(ndays,np.nan)  # 
         sites[code]['period'] =  [None] * ndays
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
              if line.startswith('starttime'):
                indata=True
              elif nline  > 18:
                 lhs, rhs = line.split(':',maxsplit=1)
                 sites[code][lhs] = rhs  # NB can be 2 values, e.g. Station lat or Measurement lat. Confusing!
              continue
   
           if code=='eBC_bb':
              stime, etime, val, eBCff = [ float(k) for k in line.split() ]
              flag=0
           else:
              stime, etime, val, flag = [ float(k) for k in line.split() ]
           print('HERE ', code, stime, val )
           sys.exit()

           flag1 = int(1000000*flag+0.001)//1000 # e.g. 0.467666 = flags 467 666
           flag2 = int(1000000*flag+0.001)% 1000
           if flag1 in invalid: continue
           if flag2>0 and flag2 in invalid: continue
           #print('I:', code, t0, stime, val, flag, flag1, flag2 )
   
           if flag1 not in flags: flags.append(flag)
           if flag2 not in flags: flags.append(flag)
   
           try:
             #print('CHECK Sample duration', sites[code]['Sample duration'] )
             sample = sites[code]['Sample duration'].replace(" ","")
           except: # e.g. IT0004R
             sample = sites[code]['Resolution code'].replace(" ","")
           if sample == '1d' or sample == '15h' or \
              sample == '2d': # Weird, KOS  has 2d, but anyway starttime-endtime=1d!
               t1=t0+dt.timedelta(days=stime)
               t2=t0+dt.timedelta(days=(stime+1)) # FIX, since e.g. ES used integer for 3, 4 
               txt='dmean'
           elif sample == '1w':
               t1=t0+dt.timedelta(days=stime)
               t2=t0+dt.timedelta(days=etime)
               txt='wmean'
           else:
               print('UNRECOGNISED Sample duration', fname, sites[code].keys())
               #print('UNRECOGNISED Sample duration', sites[code]['Sample duration'], fname )
               sys.exit()
   
           if t1<startdate: continue
           if t1>enddate: continue
           if t1.year < syear : continue
           if t1.year > eyear : continue
           #print('HERE',nline,  syy, eyy )
   
           if val>199.0: # ARGH! F...ing Ebas
               print('VERROR:', os.path.basename(f.name))
               print('VERROR:', line)
               print('VERROR:', code, t0, stime, val, flag1, flag2 )
               #sys.exit()
               continue
   
           if val > 0.0:
             n= (t1-startdate).days
             sites[code]['vals'][n] = val
             sites[code]['flag'][n] = flag
             sites[code]['period'][n] = sample
             sites[code]['t1'][n] = t1
             sites[code]['t2'][n] = t2
             sites[code]['dc']  += 1
   
             jan1 = dt.datetime(t1.year,1,1)
             doy1  = (t1-jan1).days + 1
             doy2  = (t2-jan1).days    # seems to work better without +1
   
   # end files for this site
             #print('%d %3d %3d %2d %2d %2d  %s  %8.3f   %d' % ( t1.year, doy1, doy2, t1.month, t1.day, t1.hour,  sample,  val, int(1.0e6*flag+0.001)  ) )
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

