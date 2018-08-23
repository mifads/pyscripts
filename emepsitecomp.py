#!/usr/bin/env python3
#!-*- coding: utf-8 -*-
"""
emepsitecomp is intended to extract values for one location,
usually from two or more input files. 
produced for variables matching a pattern, e.g. SURF_ppb_NO2 or SURF_ppb -
the latter will produce plots for all variables containing SURF_ppb.

If labels are given (-L option) these are used in the legend, otherwise
mkCdfComp will attempt to 'guess' these by looking for the pattern. We
would get rv4_15a from e.g.:

\n
   -i /global/work/mifads/TRENDS/rv4_15a.2012/Base/Base_month.nc
\n
or -i  rv4_15a.2012/Base/Base
or -i rv4_15a.2012/rv4_15a_month.nc

This pattern matching for labels is based upon Dave's usual filenames,
so is not guaranteed to work for all cases ;-)

A typical pattern (for EECCA grids) to look at NO, NO2  and NO3 over
north-western Europe might be:

mkCdfComp.py -y 2010 -d "40 70 20 50" -i TRENDS/rv4_15a.2010/Base/Base_month.nc TRENDS/rv4_15anosoil.2010/Base/Base_month.nc -p -v SURF_ppb_NO

(Use -p to get plots to screen; png files are produced anyway.)
"""
import argparse
import matplotlib.pyplot as plt
import numpy as np
import netCDF4 as cdf
import os
import sys

#------------------ arguments  ----------------------------------------------

#parser=argparse.ArgumentParser(usage=__doc__) also works, but text at start
parser=argparse.ArgumentParser(epilog=__doc__,
   formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-v','--varkeys',nargs='*',
    help='varname  string in nc file, can be partial eg ug_PM',required=True)
parser.add_argument('-i','--ifiles',help='Input files',nargs='*',required=True)
parser.add_argument('-c','--coords',help='coords wanted, i j',nargs=2,required=False)
parser.add_argument('-o','--ofile',help='output file',required=False)
parser.add_argument('-O','--odir',help='output directory',default='.')
parser.add_argument('-p','--plot',help='plot on screen?\n(Optional)',action='store_true')
parser.add_argument('-L','--labels',help='labels, e.g. -L"rv4.15 rv4.15a rv4.15b"\n(Optional)',required=False)
parser.add_argument('-t','--title',help='title',required=False)
parser.add_argument('-T','--tab',help='title',action='store_true')
parser.add_argument('-V','--verbose',help='extra info',action='store_true')
parser.add_argument('-y','--year',help='year',required=True)
args=parser.parse_args()
dtxt='CdfComp'
dbg=False
if args.verbose: dbg=True
if dbg: print(dtxt+'ARGS', args)

if args.coords:
  #i, j = [ int(n) for n in args.coords.split() ]
  i, j = [ int(n) for n in args.coords ]
else:
  i, j = [ -999, -999 ] # will average over full domain
  args.coords='Default'
if dbg: print(dtxt+' coords', i, j )

case=dict()
cases=[]
ifiles=[]
for n, ifile in enumerate(args.ifiles):
   #print('TRY ', n, ifile)
   if  os.path.isfile(ifile):
      f = ifile
   else:
      print('TRY File not found! ' + ifile)
      f = ifile + '/Base/Base_month.nc'  # Default
   if dbg: print('=>  ', f)
   if  not os.path.isfile(f):
     sys.exit('File not found! ' + f)

   tmpc= f.split('/')
   if dbg: print(f, '=>fTERMS ', n, tmpc)
   if len(tmpc)>2:
      case[f]= tmpc[-3].replace('.%s'%args.year,'')  # rv4.2012 from rv4.2012/Base/Base_month.nc
   else:
     case[f]= tmpc[0]  #  CAMS_IPOA fro CAMS_IPOA/CAMS_IPOA_month.nc
     if dbg: print('CASE', case[f])

   cases.append(case[f])
   ifiles.append(f)  # with full path name to .nc
   if dbg: print(dtxt+'CASE', n, case[f] )

labels = cases.copy() # default

if args.labels:
   labels = args.labels.split()
   for c, b, f in zip( cases, labels, args.ifiles ):
     if dbg: print("LABEL CASE FILE ", b, c, f )

first=True
file0=ifiles[0] #  Need file to get keys at start
#print('F0', file0)
#print('FINAL LABELS', labels)


ecdf=cdf.Dataset(file0,'r',format='NETCDF4')
keys = ecdf.variables.keys()
odir='.'
if args.odir:
  odir=args.odir
  os.makedirs(odir,exist_ok=True)
if args.tab:
  tab=open(odir+'/ResCdfCompTab_%s_%s.txt' %
           ( cases[0], '_'.join(labels[1:])), 'w' )
  header='%-30s' % 'Variable'
  for c in labels: 
    header += ( '%18s' % c )
  tab.write('%s\n' %  header )

months=list(range(1,13))
colours = 'red orange yellow blue green'.split()

for var in args.varkeys:
   for key in keys:
       if dbg: print(' VAR, KEY ', var, key )
       if not var in key:
           continue
       if key.startswith('D3_'):
           print(' SKip 3D VAR, KEY ', var, key )
           continue

       #print('Processing ', var, key )

       nfiles = len(ifiles)
       for nf, ifile in enumerate(ifiles): 

           ecdf=cdf.Dataset(ifile,'r',format='NETCDF4')
           monthly = np.full(12,np.nan)
           tmpvals = np.full(nfiles+1,np.nan) # TMP used for fake fullrun

           tmpx    = np.linspace(0.5,nfiles+0.5,nfiles+1)
           if key in ecdf.variables.keys():
             #Aug tmpv=ecdf.variables[key][:,:,:]
             tmpv=ecdf.variables[key]
             if dbg: print('KEY VALUES? ', ifile, key, np.max(tmpv), tmpv.ndim )
             if i> -1:
               if tmpv.ndim>2:
                  vals=ecdf.variables[key][:,j,i]
               else:
                  vals=[ ecdf.variables[key][j,i], ] # make list
             else:
               vals=np.mean(ecdf.variables[key][:,:,:],axis=(1,2))
             #print('VALS ', nf, vals)
             if np.max(vals) < 1.0e-3:
                print('ZERO VALUES? ', ifile, key )
                continue
             #print('TMPV var ', key, tmpv.shape, i, j, np.max(vals) )
             #print('VALS var ', key, vals.shape, i, j, np.max(vals), vals )
             for n in range(len(vals)):
               print('VAL ', key, n+1, vals[n] )
           else:
             print(' KEY NOT FOUND ', key, case[ifile])
             continue

           if( len(vals) ==1 ): # Just have one value, e.g. annual
             tmpvals[nf] =  monthly[0]
             #plt.bar(tmpx,tmpvals,label=labels[nf],color='C0')
             #SITE plt.bar(tmpx,tmpvals,label=labels[nf],color=colours[nf])
             xmin=0.0   # Start in Jan.
             xmax=nfiles+2  #
           else:
             #SITE plt.plot(months,monthly,label=labels[nf])
             xmin=1.0   # Start in Jan.
             xmax=12.0  #  QUERY??
           nf += 1
           if args.tab:
             if nf ==1: tab.write('%-30s' % key)
             tab.write('%18.3f' % np.mean(monthly) )
           #SITE if dbg: print('M:', monthly)

       if nf == 0:
         #print('NO VALUES FOUND', ifile, key )
         continue
           
       if args.plot:
         if  args.title is None :
           plt.title(key + '   (Domain %s)'%args.domain)
         else: # KEY is special
           title= args.title.replace('KEY',key)
           plt.title(title)
         plt.ylim(ymin=0.0)
       # We add a bit of vertical space for better legend placement
         y=plt.yticks()[0]
         plt.ylim(ymax=y[-1]+2*(y[-1]-y[-2]))
         plt.xlim(xmin=xmin) 
         plt.xlim(xmax=xmax) 
         #SITE if( len(monthly) ==1 ): # Just have one value, e.g. annual
         #SITE   plt.xticks(visible=False)
         plt.legend(loc='upper left',bbox_to_anchor=(0.05,1.0))

       if args.ofile:
         ofile=args.ofile
       else:
         ofile='PlotSiteComp_%s_%s_%s.png' % ( key, cases[0], '_'.join(labels) )
       if args.plot:
         plt.savefig('%s/%s' % ( odir, ofile ))
#       if args.plot: 
#         plt.show()
       #plt.clf()
         plt.close()
       if args.tab:
         tab.write('\n')
  
