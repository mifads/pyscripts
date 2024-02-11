#!/usr/bin/env python3
import numpy as np
import pandas as pd
import sys
import emxmisc.stringfunctions as sf

skip_rows=8  # get 1st line after Data

ifile='test.csv'
with open(ifile) as myFile:
  for num, line in enumerate(myFile, 1):
    if 'DATA' in line:
      skip_rows=num
      print('DATA found at line:', num)

# nb this will give NaN for confusing #Headers col
#df=pd.read_csv('test.csv',delimiter=',',skiprows=6,comment='#',skipinitialspace=True)
#npolls=len(list(df.keys())) - 2

#sd=np.loadtxt('test.csv',skiprows=SKIP_ROWS)
ds=np.genfromtxt('test.csv',delimiter=',',skip_header=skip_rows)

nrow,ncol = np.shape(ds)

new=np.zeros([19,ncol-2])

for n in range(nrow):
 nsec= int(ds[n,1]) - 1
 new[nsec,:] += ds[n,2:]
 #if nsec==3: # S4=fugituve
 #  print('S4', nsec, ds[n,2], new[nsec,0] )

for nsec in range(19):
  sumnew = np.sum(new[nsec,:])
  #print('SS', nsec, sumnew)
  if sumnew > 0.0: 
    new[nsec,:] /= sumnew
    new[nsec,:] *= 100
    #print( nsec, new[nsec,:4], np.sum(new[nsec,:]) )
  else:
    new[nsec,-1] = 100.0
  print(' 0,%3d, %s' % ( nsec, sf.multiwrite(new[nsec,:],'%11.3f')))


#for n, row in df.iteritems():
#  print( n, row)
#  sys.exit()
#  fields = row.split()
