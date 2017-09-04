#!/usr/bin/env python3
""" mkCdfSums.py simply adds all values in a cdf file. This is great for
    emissions given in eg moles/day or kg/hr, since we don't need to 
    allow for grid area.
"""
import argparse
import numpy as np
import netCDF4 as cdf
import os
import sys

#------------------ arguments  ----------------------------------------------

parser=argparse.ArgumentParser()
parser.add_argument('-v','--var',help='varname string in nc file')
parser.add_argument('-i','--ifile',help='Input file',required=True)
parser.add_argument('-d','--domain',help='domain wanted, i0 i1 j0 j1, e.g. "30 100 40 80"',required=False)
parser.add_argument('-o','--odir',help='output directory',default='.')
parser.add_argument('-V','--verbose',help='extra info',action='store_true')
args=parser.parse_args()
dtxt='CdfComp'
dbg=False
if args.verbose: dbg=True
if dbg: print(dtxt+'ARGS', args)


case=dict()
cases=[]
ifile=args.ifile
if  os.path.isfile(ifile):
   if dbg: print('TRY ', ifile)
else:
   sys.exit('MISSING IFILE'+ifile)
   
ecdf=cdf.Dataset(ifile,'r',format='NETCDF4')
var = args.var
val0=ecdf.variables[var]
ndims=len( val0.shape )

i0=0;j0=0;t0=0
if ndims  == 2:
  j1, i1 = val0.shape 
else:
  t1, j1, i1 = val0.shape 
if dbg: print(' VAR ', var, 'Shape ', val0.shape, 'Dims = ', len(val0.shape), 'Dom ', j1, i1 )

if args.domain:
  i0, i1, j0, j1 = [ int(i) for i in args.domain.split() ]

if ndims == 3:
  vals=ecdf.variables[var][:,j0:j1+1,i0:i1+1]
elif ndims == 2:
  vals=ecdf.variables[var][j0:j1+1,i0:i1+1]

if dbg: print(dtxt+' domain', i0, i1, j0, j1 )
vsum = np.sum(vals) # ,axis=(1,2))
print('Sum all values = ', vsum )
