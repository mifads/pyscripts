#!/usr/bin/env python3
""" reads an emissplit specials file and generates a default by
 taking the means for each sector. No regard take of diffeernt
 emissions per country, but good-enough for most cases
"""
import numpy as np
import pandas as pd
import sys
import emxmisc.stringfunctions as sf

assert len(sys.argv)>1, 'NEED input file!'
  
ifile=sys.argv[1] # 'test.csv'
f=open('NEW_'+ifile,'w')

with open(ifile) as myFile:
  for num, line in enumerate(myFile, 1):
    f.write(line)
    if 'DATA' in line:
      skip_rows=num
      print('DATA found at line:', num)
      break

ds=np.genfromtxt(ifile,delimiter=',',skip_header=skip_rows)

nrow,ncol = np.shape(ds)

new=np.zeros([19,ncol-2])

for n in range(nrow):
 nsec= int(ds[n,1]) - 1
 new[nsec,:] += ds[n,2:]

for nsec in range(19):
  sumnew = np.sum(new[nsec,:])
  #print('SS', nsec, sumnew)
  if sumnew > 0.0: 
    new[nsec,:] /= sumnew
    new[nsec,:] *= 100
    #print( nsec, new[nsec,:4], np.sum(new[nsec,:]) )
  else:
    new[nsec,-1] = 100.0
  print(' 0,%3d, %s' % ( nsec+1, sf.multiwrite(new[nsec,:],'%9.3f')))
  f.write(' 0,%3d%s\n' % ( nsec+1, sf.multiwrite(new[nsec,:],',%9.3f')))

f.close()


#for n, row in df.iteritems():
#  print( n, row)
#  sys.exit()
#  fields = row.split()
