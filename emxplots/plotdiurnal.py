#!/usr/bin/env python3
from collections import OrderedDict as odict
import numpy as np
import matplotlib.pyplot as plt
#import EmepStats
dtxt='plotdiurnal:'

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

  hrs = [ h+1 for h in range(24) ]

  plt.clf()

  lstyles = 'k- r-- b._ g:'.split()
  cols    = 'k r b g'.split()
  if len(lineLabels) ==0: lineLabels = list(concs.keys())
  for nk, key in enumerate( concs.keys()):
    yvals = concs[key][:]
    if useMarkers: # Add markers, usually when gappy data
      plt.plot(hrs,yvals,lstyles[nk],lw=1.5,label=lineLabels[nk],marker='o')
    else:
      plt.plot(hrs,yvals,lw=1.5,color=cols[nk],label=lineLabels[nk])

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
  if yaxisMax: plt.ylim(ymax=yaxisMax)
  if yaxisMin: plt.ylim(ymin=yaxisMin)

  #if notetxt: # Hard-coded position so far, top-left
  #  plt.text(xnote*maxv,ynote*maxv,notetxt, fontsize=notefont)

  if title:
    plt.title(title)
  if notetxt: # Hard-coded position so far, top-left
    plt.figtext(xnote,ynote,notetxt)

  if dbg: print(dtxt, len(jdays), len(obs), len(mod) )
  if ofile:
    plt.savefig(ofile)
    if dbg: print(dtxt, ' SAVES ', ofile )
  else:
    plt.show()
    if dbg: print(dtxt, ' NO PLOT ' )

if __name__ == '__main__':

  h = np.linspace(1,24,24)
  y=odict()
  y['AAA'] = 40.0 +50* np.sin(h/24.0)
  y['BBB'] = 30.0 +50* np.sin(h/24.0)

  #? stats=EmepStats.ObsModStats(x,y)
  testnote=' Germany\n 20 edgE 60N 200m\n Run rv\n xxx'
  plotdiurnal(y) # ,notetxt=testnote)
