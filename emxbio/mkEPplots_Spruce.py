#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import emxmisc.stringfunctions as sf

# MEGAN3 EFv240120.csv
# Units nmole/m2PLA/s at 30C, 1000 uE
#                       Eiso   Emt   Esqt/Emt
meg3=dict()
meg3['Picea abies'] =  ( 1.00,  2.17,  0.95)
meg3['Picea sitchensis'] =  ( 8.00,  2.17,  0.95)

I_to_uggh = 1.0e-3*68*3600/150
M_to_uggh = 1.0e-3*136*3600/150
for m, vals in meg3.items():
   print('MEG3', m, vals[0]*I_to_uggh, vals[1]*M_to_uggh )


# Table 5, ug/m2/h. I think ug/m2PLA/h
#             A       M       J   J   A   S
tab5SFmt = [ np.nan, np.nan, 14, 32, 10, 13 ]
tab5NFmt = [ 72,    15,    97,   81, 61, np.nan ]
tab5mt = tab5SFmt + tab5NFmt
mt=np.nanmean(tab5mt)
mts=np.nanmean(tab5SFmt)
mtn=np.nanmean(tab5NFmt)

tab5SFsqt = [ np.nan, np.nan, 17, 81, 66, 384 ]
tab5NFsqt = [ 13,     56,    342, 189, 408, np.nan ]
tab5sqt = tab5SFsqt + tab5NFsqt
sqt=np.nanmean(tab5sqt)
sqts=np.nanmean(tab5SFsqt)
sqtn=np.nanmean(tab5NFsqt)

uggh =  1/150.0
print(f'MT:  {mt:8.2f} {5*mt:8.2f} {uggh*mt:8.2f}')
print(f'MTS:  {mts:8.2f} {5*mts:8.2f} {uggh*mts:8.2f}')
print(f'MTN:  {mtn:8.2f} {5*mtn:8.2f} {uggh*mtn:8.2f}')
print(f'SQT: {sqt:8.2f} {5*sqt:8.2f} {uggh*sqt:8.2f}')
print(f'SQTS:  {sqts:8.2f} {5*sqts:8.2f} {uggh*sqts:8.2f}')
print(f'SQTN:  {sqtn:8.2f} {5*sqtn:8.2f} {uggh*sqtn:8.2f}')

print('as ug/g/h')
print(f'MT:  {mt/150:8.2f}')
print(f'SQTS/MT(%):  {100*sqts/mts:8.2f}')
print(f'SQTN/MT(%):  {100*sqtn/mts:8.2f}')

# Table 2 summer values (ng/gdw/h, 30C). Note that beta for MT is 0.1, for SQT 0.17, so 
# SQT may be too high?
htab="/home/davids/Work/D_Emis/Docs_BVOC/Spruce/Table_Hakola2023_spruceComps.txt"
ds=pd.read_table(htab,delim_whitespace=True,comment='#')

x=[]; y=dict( isop=[], mt=[], sqtRatio=[] )
emep=dict( isop=1.0, mt=1.5 )
clist='r b g m c black orange'.split()
ncol=0
cols=[]
sites=[]  # Unique site list
csites=[] # cols for sites
sites.append(ds.code[0])
csites.append(clist[0])

for n in range(len(ds)):
  if ds.mm[n] < 6:
     #print('SKIP ', ds.code) 
     continue
  if ds.mm[n] > 9:
    if ds.mm[n] == 678:
      pass
    else:
      #print('SKIP ', ds.code[n] )
      continue  # 901 = SON
#  if ds.mm[n] > 9: continue  # 901 = SON
  #print('USES ',n, ds.mm[n], ds.code[n])
  if n> 1:
   if ds.deg[n] != ds.deg[n-1]: 
    ncol += 1
    sites.append(ds.code[n])
    csites.append(clist[ncol])
  cols.append(clist[ncol])
  x.append( ds.deg[n] )
  y['isop'].append( 0.001* ds.isop[n] )
  y['mt'].append( 0.001* (ds.mt[n] + ds.omt[n]) )
  if ds.sqt[n] > 0.0:
    y['sqtRatio'].append( ds.sqt[n]/(ds.mt[n]+ds.omt[n]))
  else:
    y['sqtRatio'].append( np.nan )
  print(f'H-Out {n:2d} {ds.code[n]:<12s} {ds.mm[n]:3d}  {ds.deg[n]:9.2f} {y['isop'][-1]:8.3f} {y['mt'][-1]:8.3f} {y['sqtRatio'][-1]:8.3f}' )

#Purser, 2021, UK sites
x.append( 56.089 ) # early shoot
y['isop'].append( 0.2 )
y['mt'].append( 3.44 )
y['sqtRatio'].append( 0.13 )
sites.append('Pu-early')
csites.append('darkgrey')
cols.append('darkgrey')

x.append( 56.089 )
y['isop'].append( 0.16)
y['mt'].append( 4.25 )
y['sqtRatio'].append( 0.003 )
sites.append('Pu-late')
csites.append('lightgrey')
cols.append('lightgrey')

for poll in 'isop mt sqtRatio'.split():
  print(f'MEAN/MED {poll:<8s} {np.nanmean(y[poll]):6.3f} {np.nanmedian(y[poll]):6.3f} {sf.multiwrite(y[poll],"%5.2f")}')
  plt.scatter(x,y[poll],color=cols,label=None) # 'Is')
  # Lines
  if 'sqt' not in poll:
    plt.plot([min(x), max(x)], [emep[poll], emep[poll]],ls='--',color='darkgrey',label=None) # 'Is')

  if poll=='isop':      plt.figtext(0.5,0.82,'Isoprene',fontsize=16)
  if poll=='mt':        plt.figtext(0.6,0.82,'Monoterpenes',fontsize=16)
  if poll=='sqtRatio':  plt.figtext(0.4,0.82,'sqtRatio',fontsize=16)

  xleg=0.15; yleg=0.82
  #for n in range(ncol+1):
  for n in range(ncol+3): # now +2 for Purser
    plt.figtext(xleg,yleg,sites[n],color=csites[n])
    yleg -= 0.05
  plt.xlabel(r'Latitude ($^\circ$N)',fontsize=14)
  if 'sqt' not in poll:
    plt.ylabel(f'EP-{poll} (ug/g/h)',fontsize=14)
  else:
    plt.ylabel('SQT/MT ratio',fontsize=14)
  plt.savefig(f'plotSpruceEPs_{poll}.png')
  plt.clf()
  #plt.show()
