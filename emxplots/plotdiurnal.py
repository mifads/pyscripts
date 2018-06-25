#!/usr/bin/env python3
from collections import OrderedDict as odict
import numpy as np
import matplotlib.pyplot as plt
#import EmepStats
dtxt='plotdiurnal:'

def makediurnal(obs,mod,dstart=0,dend=367):
  """ Makes 24h arrays from eg 365 days. 
      (or between sd and ed if given)
      Assumes 'obs' maybe has Nan. Use as mask """

  dtxt='makediurnal:'
  assert len(obs) == len(mod), dtxt+'unequal lengths %d %d!!' % (len(mod), len(obs))
  o24=np.zeros(24)
  m24=np.zeros(24)
  n24=np.zeros(24)
  ndays =len(obs/24)
  h = 0
  doy=0
  for n, o in enumerate(obs):
     if np.isfinite(o) and o>=0.0:
       if ( dstart <= doy < dend ):
         o24[h] += o
         m24[h] += mod[n]
         n24[h] += 1
       h += 1
       if h==24:
          h=0
          doy += 1
  for h in range(24):
    if n24[h] >0:
       o24[h] /= n24[h]
       m24[h] /= n24[h]
    else:
       o24[h] = np.nan
       m24[h] = np.nan
  return o24, m24

def plotdiurnal(concs=odict(),
    xlabel='Hour of Day',ylabel='Conc',
    lineLabels=[],
    yaxisMin=None, yaxisMax=None, # y-axis limits
    useMarkers=None,
    title=None,                   # 
    notetxt=None,                 # Text, can be multi-line
    xnote=0.15,ynote=0.75,notefont=16,  #  default location
    dbg=False,ofile=None):
  """ Arguments as from  emxplots.scatplots """

  print('IN PLOTDIURNAL', yaxisMin)
  hrs = [ h+1 for h in range(24) ]

##  x np.array(list(concs.values()))  # We look for shape
# if len(x[0]) > 24:
#    ndays = len(x[0])
#  print('PLOTDIUNRAL ', len(concs) )

  plt.clf()

  lstyles = 'k- r-- b._ g:'.split()
  cols    = 'k r b g'.split()
  if len(lineLabels) ==0: lineLabels = list(concs.keys())
  for nk, key in enumerate( concs.keys()):
    yvals = concs[key][:]
    print('PLOTDIURNAL',nk, key)
    if useMarkers: # Add markers, usually when gappy data
      plt.plot(hrs,yvals,lstyles[nk],lw=1.5,label=lineLabels[nk],marker='o')
    else:
      plt.plot(hrs,yvals,lstyles[nk],lw=1.5,label=lineLabels[nk])
      #plt.plot(hrs,yvals,lstyles[nk],lw=1.5,color=cols[nk],label=lineLabels[nk])

  #if len(modmin)>1:
  #if not modmin == None:
  #   plt.fill_between(jdays,modmin,modmax,color='b',alpha=0.1)

  plt.legend()
  plt.title('TITLE')
  plt.xlabel(xlabel, fontsize=16)
  plt.ylabel(ylabel, fontsize=16)
  v=plt.axis()
  maxv=max(v)
  plt.xlim([1,24])
  # BTW, cannot test just 'if yaxisMin:' since zero ymin value -> false
  if yaxisMax is None: 
     plt.ylim(ymax=maxv+5) # Just to get some space
  else:
     plt.ylim(ymax=yaxisMax)
  if yaxisMin is not None: plt.ylim(ymin=yaxisMin)

  #if notetxt: # Hard-coded position so far, top-left
  #  plt.text(xnote*maxv,ynote*maxv,notetxt, fontsize=notefont)

  if title:
    plt.title(title)
  if notetxt: # Hard-coded position so far, top-left
    plt.figtext(xnote,ynote,notetxt,fontsize=notefont)

  if dbg: print(dtxt, len(jdays), len(obs), len(mod) )
  print('DIUR OFILE ', ofile)
  if ofile is None:
    plt.show()
    if dbg: print(dtxt, ' NO PLOT ' )
  else:
    plt.savefig(ofile)
    if dbg: print(dtxt, ' SAVES ', ofile )

if __name__ == '__main__':

  h = np.linspace(1,24,24)
  y=odict()
  y['AAA'] = 40.0 +50* np.sin(h/24.0)
  y['BBB'] = 30.0 +50* np.sin(h/24.0)

  #? stats=EmepStats.ObsModStats(x,y)
  testnote=' Germany\n 20 edgE 60N 200m\n Run rv\n xxx'
  plotdiurnal(y) # ,notetxt=testnote)
