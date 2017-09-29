#!/usr/bin/env python3
#!-*- coding: utf-8 -*-
"""
mkCdfComp is intended to plot monthly averages over a specified domain, usually from two
or more input files. Plots are produced for variables matching a pattern, e.g. SURF_ppb_NO2
or SURF_ppb - the latter will produce plots for all variables containing SURF_ppb. 

If labels are given (-L option) these are used in the legend, otherwise mkCdfComp will
attempt to 'guess' these by looking for the pattern. We would get rv4_15a from e.g.:

\n
   -i /global/work/mifads/TRENDS/rv4_15a.2012/Base/Base_month.nc
\n
or -i  rv4_15a.2012/Base/Base
or -i rv4_15a.2012/rv4_15a_month.nc

This pattern matching for labels is based upon Dave's usual filenames, so is not
guaranteed to work for all cases ;-)

A typical pattern (for EECCA grids) to look at NO, NO2  and NO3 over north-western Europe might be:

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
parser.add_argument('-v','--varkeys',nargs='*',help='varname  string in nc file, can be partial eg ug_PM',required=True)
parser.add_argument('-i','--ifiles',help='Input files',nargs='*',required=True)
parser.add_argument('-d','--domain',help='domain wanted, i0 i1 j0 j1, e.g. "30 100 40 80"',required=True)
parser.add_argument('-o','--odir',help='output directory',default='.')
parser.add_argument('-p','--plot',help='plot on screen?',action='store_true')
parser.add_argument('-L','--labels',help='labels, e.g. -L"rv4.15 rv4.15a rv4.15b"',required=False)
parser.add_argument('-V','--verbose',help='extra info',action='store_true')
parser.add_argument('-y','--year',help='year',required=True)
args=parser.parse_args()
dtxt='CdfComp'
dbg=False
if args.verbose: dbg=True
if dbg: print(dtxt+'ARGS', args)

i0, i1, j0, j1 = [ int(i) for i in args.domain.split() ]
print(dtxt+' domain', i0, i1, j0, j1 )

case=dict()
cases=[]
ifiles=[]
for ifile in args.ifiles:
   print('TRY ', ifile)
   #print('TRY ', ifile.split('/') )
   if  os.path.isfile(ifile):
      f = ifile
#   elsif args.suffix:
#      f = ifile + '/' + suffix  # Adds, NOT TESTED YET
   else:
      f = ifile + '/Base/Base_month.nc'  # Default
   print('=>  ', f)
   

   tmpc= f.split('/')
   print('CASES ', len(tmpc), tmpc)
   if len(tmpc)>2:
      case[f]= tmpc[-3].replace('.%s'%args.year,'')  # rv4.2012 from rv4.2012/Base/Base_month.nc
   else:
     case[f]= tmpc[0]  #  CAMS_IPOA fro CAMS_IPOA/CAMS_IPOA_month.nc
     print('CASE', case[f])
#     sys.exit()

   cases.append(case[f])
   ifiles.append(f)  # with full path name to .nc
   print(dtxt+'CASE', case[f] )

labels = cases.copy() # default

if args.labels:
   labels = args.labels.split()
   for c, b, f in zip( cases, labels, args.ifiles ):
     print("LABEL CASE FILE ", b, c, f )
print('FINAL LABELS', labels)

first=True
file0=ifiles[0] #  Need file to get keys at start
print('F0', file0)
print('LABELS', labels)

ecdf=cdf.Dataset(file0,'r',format='NETCDF4')
keys = ecdf.variables.keys()
odir='.'
if args.odir:
  odir=args.odir
  os.makedirs(odir,exist_ok=True)
#tab=open(odir+'/ResCdfCompTab_%s.txt' % '_'.join(cases), 'w' )
tab=open(odir+'/ResCdfCompTab_%s_%s.txt' % ( cases[0], '_'.join(labels)), 'w' )
header='%-30s' % 'Variable'
for c in labels: 
  header += ( '%18s' % c )
tab.write('%s\n' %  header )
months=list(range(1,13))
for var in args.varkeys:
   if dbg: print(' VAR ', var )
   for key in keys:
       if dbg: print(' VAR, KEY ', var, key )
       if not var in key:
           continue
       if key.startswith('D3_'):
           print(' SKip 3D VAR, KEY ', var, key )
           continue

       tab.write('%-30s' % key)
       print('Processing ', var, key )

       nf=0
       for ifile in ifiles: 

           ecdf=cdf.Dataset(ifile,'r',format='NETCDF4')
           if key in ecdf.variables.keys():
             tmpv=ecdf.variables[key][:,:,:]
             print('TMPV var ', key, tmpv.shape, i0, i1, j0, j1 )
             vals=ecdf.variables[key][:,j0:j1+1,i0:i1+1]
             monthly = np.mean(vals,axis=(1,2))
           else:
             print(' KEY NOT FOUND ', key, case[ifile])
             monthly = np.full(12,np.nan)
           plt.plot(months,monthly,label=labels[nf])
           nf += 1
           tab.write('%18.3f' % np.mean(monthly) )
           if dbg: print('M:', monthly)

       plt.title(key)
       plt.ylim(ymin=0.0)
       plt.xlim(xmin=1.0) # Start in Jan.
       plt.legend()
       plt.savefig('%s/PlotCdfComp_%s_%s_%s.png' % ( odir, key, cases[0], '_'.join(labels) ))
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
