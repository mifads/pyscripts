#!/usr/bin/env python3
#!-*- coding: utf-8 -*-
"""
emep_monthlyComp is intended to plot monthly averages over the full grid or
over a specified domain, usually from two or more input files. Plots are
produced for variables matching a pattern, e.g. SURF_ppb_NO2 or SURF_ppb -
the latter will produce plots for all variables containing SURF_ppb.

If labels are given (-L option) these are used in the legend, otherwise
emepmonthlycomp will attempt to 'guess' these by looking for the pattern. We
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

emepmonthlycomp.py -y 2010 -d "40 70 20 50" -i TRENDS/rv4_15a.2010/Base/Base_month.nc TRENDS/rv4_15anosoil.2010/Base/Base_month.nc -p -v SURF_ppb_NO

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
parser.add_argument('-d','--domain',help='domain wanted, i0 i1 j0 j1, e.g. "30 100 40 80"\n(Optional)',required=False)
#parser.add_argument('-f','--ofile',help='output file',required=False)
parser.add_argument('-f','--oflag',help='output file flag label',required=False)
parser.add_argument('-O','--odir',help='output directory',default='.')
parser.add_argument('-p','--plot',help='plot on screen?\n(Optional)',action='store_true')
parser.add_argument('-L','--labels',help='labels, e.g. -L"rv4.15 rv4.15a rv4.15b"\n(Optional)',required=False)
parser.add_argument('-n','--nonegs',help='skip neg values',required=False,action='store_true')
parser.add_argument('-s','--skip',help='skip files with wrong number months',action='store_false')
parser.add_argument('-t','--title',help='title',required=False)
parser.add_argument('-V','--verbose',help='extra info',action='store_true')
parser.add_argument('-y','--year',help='year',required=True)
args=parser.parse_args()
dtxt='CdfComp:'
dbg=False
if args.verbose: dbg=True
if dbg: print(dtxt+'ARGS', args)
skip_wrongmonths = args.skip
if dbg: print(dtxt+'ARGS', args)

if args.domain:
  i0, i1, j0, j1 = [ int(i) for i in args.domain.split() ]
else:
  i0, i1, j0, j1 = [ 0, -2, 0, -2 ] # full domain: -2 used so that j1+1 -> -1
  args.domain='Full'
print(dtxt+' domain', i0, i1, j0, j1 )

case=dict()
cases=[]
ifiles=[]
for n, ifile in enumerate(args.ifiles):
   print('TRY ', n, ifile)
   if  os.path.isfile(ifile):
      f = ifile
   else:
      print('TRY subdirs! ' + ifile)
      f = ifile + '/Base/Base_month.nc'  # Default
      f = ifile + '/Base_month.nc'  # Default
   print('=>  ', f)
   if  not os.path.isfile(f):
     sys.exit('File not found! ' + f)

   tmpc= f.split('/')
   print( '=>  fTERMS ', n, tmpc)
   if len(tmpc)>2:
      case[f]= tmpc[-3].replace('.%s'%args.year,'')  # rv4.2012 from rv4.2012/Base/Base_month.nc
   else:
     case[f]= tmpc[0]  #  CAMS_IPOA fro CAMS_IPOA/CAMS_IPOA_month.nc
   print('CASE', case[f], len(tmpc), tmpc )

   cases.append(case[f])
   ifiles.append(f)  # with full path name to .nc
   print(dtxt+'CASE', n, case[f] )

labels = cases.copy() # default

if args.labels:
   labels = args.labels.split()
   for c, b, f in zip( cases, labels, args.ifiles ):
     print("LABEL CASE FILE ", b, c, f )

first=True
file0=ifiles[0] #  Need file to get keys at start
print('F0', file0)
print('FINAL LABELS', labels)

ecdf=cdf.Dataset(file0,'r',format='NETCDF4')
keys = ecdf.variables.keys()
odir='.'
if args.odir:
  odir=args.odir
  os.makedirs(odir,exist_ok=True)
if args.oflag:
   tablab=args.oflag
else:
   tablab= '%s_%s' % ( cases[0], '_'.join(labels) )
print('TABLAB', tablab )
tab=open(odir+'/ResCdfCompTab_%s.txt' % tablab, 'w') # ( cases[0], '_'.join(labels[1:])), 'w' )
header='%-30s' % 'Variable'
for c in labels: 
  header += ( '%18s' % c.replace('.%s'%args.year,'') )
  print('CCC%s:%s'% (c, c.replace('.%s'%args.year,'')) )
  print("LEN", len(header))
  print('%s' %  header )
print('FINAL %s' %  header )
print('FINAL LEN' ,  len(header) )
#tab.write('%s\n' %  header )
tab.write(header+"\n")
months=list(range(1,13))
colours = 'red orange yellow blue green'.split()

nmonthly_last = -999
for var in args.varkeys:
   #if dbg: print(' VAR ', var )
   for key in keys:
       #if dbg: print(' VAR, KEY ', var, key )
       if not var in key:
           continue
       if key.startswith('D3_'):
           print(' SKip 3D VAR, KEY ', var, key )
           continue

       print('\nProcessing ', var, key )

       nfiles = len(ifiles)
       data_found=False
       for nf, ifile in enumerate(ifiles): 

           ecdf=cdf.Dataset(ifile,'r',format='NETCDF4')
           monthly = np.full(12,np.nan)
           tmpvals = np.full(nfiles+1,np.nan) # TMP used for fake fullrun

           tmpx    = np.linspace(0.5,nfiles+0.5,nfiles+1)
           if key in ecdf.variables.keys():
             tmpv=ecdf.variables[key][:,:,:]
             if dbg: print('KEY FDOM VALUES? ', ifile, key, np.max(tmpv), np.min(tmpv) )
             vals=ecdf.variables[key][:,j0:j1+1,i0:i1+1]
             if np.max(vals) < 1.0e-9:
               print('ZERO VALUES? ', ifile, key, nf )
               continue
             else:
               data_found=True # something to plot
             if args.nonegs:
               vals[vals<0] = np.nan
             #DEBUG CO
             #if np.nanmax(vals) > 1.0e9:
             #  nt, nj, ni = np.shape(vals)
             #  print('TMPV var ', key, tmpv.shape, i0, i1, j0, j1, np.nanmax(vals), np.nanmin(vals), ifile, nj, ni )
             #  zz= np.nanmax(vals,axis=0)
             #  for mm in range(12):
             #    print('TMPV MM  ', mm, np.nanmax(vals), np.nanmax(vals[mm,:,:]), np.nanmin(vals) )
             #  print('SHP', zz.shape )
             #  jj, ii = np.where(zz==np.nanmax(zz))
             #  for j, i in zip(jj,ii): # in case of repeated max
             #   print('MAXLOC', key, j, i, vals[:,j,i] )
          
             monthly = np.nanmean(vals,axis=(1,2))  # domain mean vals: (12, 359, 719)
             if dbg: print('TMPV monthly ',  monthly, len(monthly))
           else:
             print(' KEY NOT FOUND ', key, case[ifile])
             continue

           nmonthly = len(monthly)
           if nmonthly_last < 0:
              nmonthly_last = nmonthly
           else:
            if ( nmonthly != nmonthly_last )  and skip_wrongmonths:
              print('SKIPPING ',labels[nf],
               'Inconsistent lengths! %d %d' % ( nmonthly_last, nmonthly )) 
              continue
            else:
              assert nmonthly==nmonthly_last,'Inconsistent lengths! %d %d' % (
                          nmonthly_last, nmonthly )

           if( nmonthly ==1 ): # Just have one value, e.g. annual
             try:
               tmpvals[nf] =  monthly[0]
             except:
               print('MONTHL ERR?', nf, ifile,nmonthly, monthly )
               sys.exit('MONTHL ERR?' )
             #plt.bar(tmpx,tmpvals,label=labels[nf],color='C0')
             plt.bar(tmpx,tmpvals,label=labels[nf],color=colours[nf])
             left=0.0   # Start in Jan.
             right=nfiles+2  #
           else:
             plt.plot(months,monthly,label=labels[nf])
             left=1.0   # Start in Jan.
             right=12.0  #  QUERY??

#S21           if nf ==1: tab.write('%-30s' % key)
           if nf ==0: tab.write('%-30s' % key)
           #tab.write('%18.3f' % np.mean(monthly) )
           tab.write('%18.5g' % np.mean(monthly) )
           if dbg: print('M:', monthly)

       if not data_found:
         print('NO VALUES FOUND', ifile, key )
         continue
           
       if  args.title is None :
         plt.title(key + '   (Domain %s)'%args.domain)
       else: # KEY is special
         title= args.title.replace('KEY',key)
         plt.title(title)
       plt.ylim(bottom=0.0)
       # We add a bit of vertical space for better legend placement
       y=plt.yticks()[0]
       plt.ylim(top=y[-1]+2*(y[-1]-y[-2]))
       plt.xlim(left=left) 
       plt.xlim(right=right) 
       if( len(monthly) ==1 ): # Just have one value, e.g. annual
         plt.xticks(visible=False)
       plt.legend(loc='upper left',bbox_to_anchor=(0.05,1.0))
       if args.oflag:
          #ofile=args.ofile
          ofile='PlotCdfComp_%s_%s.png' % (key, args.oflag)  # 
       else:
          ofile='PlotCdfComp_%s_%s_%s.png' % ( key, cases[0], '_'.join(labels) )
       if dbg: print('Plotting '+ofile)
       plt.savefig('%s/%s' % ( odir, ofile ))
       if args.plot: 
         plt.show()
       #plt.clf()
       plt.close()
       tab.write('\n')

#
#veg=bcdf.variables['FstO3_IAM_CR'][0,:,:] # Land-mask?
#
##base = veg[j0:j1+1, i0:i1+1]
##test = veg[j0:j1+1, i0:i1+1]
#
##plt.imshow(veg2)
##plt.show()
##print( i0, i1, j0, j1, lats[j0], lats[j1], np.mean(veg[j0:j1+1, i0:i1+1]), np.mean(veg2) )
#
#var='CR'
#n=np.zeros([2,24])
#v=np.zeros([2,24])
#for ivar in range(2):
#  o3=hcdf.variables['CanopyO3_IAM_%s' % var ][:,j0:j1+1,i0:i1+1]
#  print( 'Starting ', var, np.max(o3), np.mean(o3) )
#  o3t=o3[:,0,0]
#  o3j=o3[0,:,0]
#  o3i=o3[0,0,:]
#  h=1
#  for k in range(len(o3t)):
#   #mask == veg2 > 0.0
#    for j in range(len(o3j)):
#      for i in range(len(o3i)):
#        if veg2[j,i] > 0.0:
#          v[ivar,h] += np.mean( o3[k,:,:] )
#          n[ivar,h] += 1
#    h += 1
#    if h == 24: h = 0
#  v[ivar,:] /= n[ivar,:] 
#  meanv = np.mean( v[ivar,:] )
#  v[ivar,:] /= meanv
#  var='DF'  # reset for next ivar
#
#with open('Results_HourlyTable.txt','w') as f:
#  f.write( '%2s  %8s  %8s\n' % ( 'h', 'Crop', 'Tree' ))
#  for h in range(24):
#     f.write( '%2.2d  %8.3f  %8.3f\n' %  ( h, v[0,h], v[1,h] ) )
#
#plt.plot(v[0,:],label='crops')
#plt.plot(v[1,:],label='forest')
#plt.legend()
#plt.savefig('Hourly5deg.png')
#plt.show()
##print('RES n ', i, n )
##print('RES v ', i, v/n )
#
#
