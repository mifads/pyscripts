#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import emxmisc.emepstats as emepstats
dtxt='plotdaily:'

def plotdaily(jdays,obs,mod=[],modmin=[],modmax=[],
    mod2=[],modmin2=[],modmax2=[],
    xlabel='Days',ylabel='Conc',
    ymin=0,ymax=None,             #  lower and upper y curves
    yaxisMin=None, yaxisMax=None, # y-axis limits
    useMarkers=None,
    title=None,                   # 
    notetxt=None,                 # Text, can be multi-line
    xnote=0.15,ynote=0.75,notefont=16,  #  default location
    dbg=False,ofile=None):
  """ Arguments as from plotscatt """

  obs = np.array(obs)
  for n, xx in enumerate(obs):
    if xx < 0.0:
      obs[n] = np.nan

  if len(mod)>1:
    mod = np.array(mod)

  # now in emepstats
  #f=np.isfinite(obs)
  #dc = int( 0.5 +  sum(f)/(0.01*len(obs)) ) # Data capture in %
  #print('DC ', dc, len(jdays) )
#
#  if addStats:
#    meanx = np.mean(obs[f])
#    meany = np.mean(mod[f])
#    bias = int(  0.5+  100*(meanmod - meanobs)/meanobs )
#    r=np.corrcoef(obs[f],mod[f])[0,1]
#    print('R',meanx, meany, r, sum(f) )

#  fig=plt.scatter(x,y)

  plt.clf()

  if useMarkers: # Add markers, usually when gappy data
    plt.plot(jdays,obs,lw=1.5,label='Obs',marker='o')
  else:
    plt.plot(jdays,obs,lw=1.5,color='g',label='Obs')

  if len(mod)>1:
     plt.plot(jdays,mod,'--',lw=1.5,color='b',label='Mod')

  if len(mod2)>1:
     plt.plot(jdays,mod2,'--',lw=1.5,color='r',label='Mod2')

  if len(modmin)>1:
  #if not modmin == None:
     plt.fill_between(jdays,modmin,modmax,color='b',alpha=0.1)

  plt.legend()
  plt.title('TITLE')
  plt.xlabel(xlabel, fontsize=16)
  plt.ylabel(ylabel, fontsize=16)
  v=plt.axis()
  maxv=max(v)
  plt.xlim([jdays[0],jdays[-1]])
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

  jdays = list(range(1,366))

  x = 30.0 +50* np.sin(jdays)
  y = 40.0 +50* np.sin(jdays)

  y[40:60] = np.nan
  ymin = y - 10
  ymax = y + 2
  stats=emepstats.obsmodstats(x,y)
  testnote=' Germany\n 20 edgE 60N 200m\n Run rv\n xxx'
  plotdaily(jdays,x,y,ymin,ymax,yaxisMax=200,notetxt=testnote)
