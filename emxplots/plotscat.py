#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import emxmisc.geometry as geom

# Styles, added Dec 2017,  see e.g.
# print(plt.style.available)
# https://tonysyu.github.io/raw_content/matplotlib-style-gallery/gallery.html

# Outliers, info:
# More advanced, from http://stackoverflow.com/questions/10231206/can-scipy-stats-identify-and-mask-obvious-outliers
# See also: http://statsmodels.sourceforge.net/devel/examples/notebooks/generated/robust_models_0.html
# For statsmodels on python3: install python3-pip; pip3 install statsmodels

try:
  from statsmodels.formula.api import ols   # Used pip3 (python3-pip) to install
  print('Stats: statsmodels available')
  ImportStats=True
except:
  print('Stats: NOT FOUND statsmodels')
  ImportStats=False


def emepscatplot(x,y,xlabel,ylabel,txt=None,pcodes=None,label=None,
    title=None,
    plotstyle='classic',
    labelx=0.1,labely=0.9,labelsize=16,
    addxy=0.0,  # Increases maxv to e.g. cope with label  overwrites
    addStats=False,skipOutliers=False,dbg=False,ofile=None):

  """
   Scatter plot, emepscatplot(x,y,xlabel,ylabel,txt=None,pcodes=None,addxy=0.0,addStats=False,ofile=None)
  """
  dtxt = 'emepscatplot'
  plt.style.use(plotstyle)
  x = np.array(x)
  y = np.array(y)
  if dbg:
   print( dtxt+' lengths x,y: ', len(x), len(y) )
   print( dtxt+' shape x, y: ', x.shape, y.shape )
   print( dtxt+' plotstyle : ', plotstyle)
   for i in range(len(x)):
     p= pcodes[i] if pcodes else '#%d'%i
     print( 'INTO emepscatplot p,x,y: ', p, x[i], y[i] )
#vlimit=300.0
#f=alt<vlimit
  plt.subplot(111)
  plt.clf()
  fig=plt.scatter(x,y)
  plt.xlabel(xlabel, fontsize=16)
  plt.ylabel(ylabel, fontsize=16)
  v=plt.axis()
  maxv=max(v)
  if addxy>0.0:
      maxv += addxy
  if title: # Hard-coded position so far, top-left
    plt.title(title, fontsize=labelsize)
  if label: # Hard-coded position so far, top-left
    plt.text(labelx*maxv,labely*maxv,label, fontsize=labelsize)
  plt.gca().set_aspect('equal')

###########################################################################
  [m,c]=np.polyfit(x,y,1)
  r=np.corrcoef(x,y)
###########################################################################
  skipi = np.zeros(len(x),dtype='int')
  skip = [] 
  if skipOutliers:
     try:
       regression= ols("data ~x",data=dict(data=y,x=x)).fit()
       test = regression.outlier_test()  # Find outliers 
       #DS outliers = ((x[i],y[i]) for i,t in enumerate(test.icol(2)) if t < 0.5)
       #for i,t in enumerate(test.icol(2)):
       for i,t in enumerate(test.iloc[:,2]):
         if t < 0.5:
           skipi[i] = 1
           skip.append(i)
     except: # where stats not implemented Test own outliers
       g = []
       for i in range(0,len(x)):
         g.append( geom.distancePoint2line( x[i],y[i], m, -1.0, c ) )
         print('GEOM', i, x[i], y[i], pcodes[i], geom.distancePoint2line( x[i],y[i], m, -1.0, c ))
       print('MAXGEOM', max( g ))
       for i in range(0,len(x)):
         if g[i] > 0.5* max(g):
             skipi[i] = 1
             skip.append(i)

     print('Outliers: ', skip)
     # Figure #
     #DS figure = smgraphics.regressionplots.plot_fit(regression, 1)
     # Add line #
     #DS smgraphics.regressionplots.abline_plot(model_results=regression, ax=figure.axes[0])

#### station codes if wanted ##############################################

  if pcodes is None : # uses site codes, e.g AT00031R
    print('No PCODES')
  else:

    print('PCODES0 ', len(y), len(pcodes))
    for n in range(0, len(y) ):

      label = '%4s'%pcodes[n]
      col='k'
      if skipi[n] : col='r'
      print(dtxt, n, skipi[n], pcodes[n], x[n], y[n])
      plt.text(x[n],y[n],label,color=col,fontsize=10)

#J8  v=plt.axis() #J8  maxv=max(v)

#### 1:1 line  ############################################################

  lin=(0,maxv) # 1:1 line
  plt.plot(lin,lin,'g--')

#### regression line - all data ###########################################
  #[m,c]=np.polyfit(x,y,1) #r=np.corrcoef(x,y)

  fit=( c, c+m*lin[1] )
  plt.plot(lin,fit,'r--')

###########################################################################
  # Data without outliers
  if len(skip) > 0:
     xn = np.delete( x, skip ) 
     yn = np.delete( y, skip ) 
  else:
     xn = x.copy()
     yn = y.copy()

###########################################################################
# After removing outliers

  if skipOutliers:
    [mn,cn]=np.polyfit(xn,yn,1)
    rn=np.corrcoef(xn,yn)
    fitn=( cn, cn+mn*lin[1] )
    plt.plot(lin,fitn,'k--')

  vpos=0.17*maxv   #  vertical position  for text below, was 0.22
  dvpos=0.05*maxv  # for text below
  if addStats:
     #plt.text(0.6*maxv,0.25*maxv,'Year %4s'% year,fontsize=12)
     #plt.text(0.6*maxv,0.2*maxv,'Max altitude %4.0f m'% vlimit,fontsize=12)
     regline = 'y= %4.2f x + %6.1f'%( m, c)
     col='k'
     if skipOutliers: col='r'  # keep black for non-outliers
     if c < 0: regline = 'y= %4.2f x %6.1f'%( m, c)
     plt.text(0.6*maxv,vpos,regline,color=col,fontsize=12)
     vpos -= dvpos
     plt.text(0.6*maxv,vpos,'Corr.= %6.2f'%r[0,1],color=col,fontsize=12)

  if skipOutliers:
     vpos -= dvpos
     plt.text(0.6*maxv,vpos,'y= %4.2f x + %6.1f'%( mn, cn),color='k',fontsize=12)
     vpos -= dvpos
     plt.text(0.6*maxv,vpos,'Corr.= %6.2f'%rn[0,1],color='k',fontsize=12)
  plt.axis([0,maxv,0,maxv])

  if txt:  # place in upper left
    vpos=0.95*maxv   #  vertical position  for text below, was 0.22
    plt.text(0.06*maxv,vpos,txt,color='k',fontsize=12)
  #plt.xbound(0,2*maxv)
  #plt.axis('scaled')
  #plt.axis('equal')

  if ofile:
    print(dtxt+'SAVES ', ofile)
    plt.savefig(ofile)
  else:
    print(dtxt+'SHOWS ', plotstyle)
    plt.show()
  
  if skipOutliers:
     return  mn, cn, rn[0,1]   # Stats
  else:
     return  m, c, r[0,1]   # Stats

#maxv=24000
#P.axis([0,maxv,0,maxv])
#P.xlim(0,maxv)
#P.ylim(0,maxv)
#P.axis('scaled')
#P.axis('equal')
#P.title(r'Modelled versus Observed AOT40$_f$\n(Year %s, Stations < %s m a.s.l., Model %s)'%( year, vlimit, rv ))

#P.show()
#P.savefig('CompU%d_%s_%s_%s.png' % (maxalt, year, rv, grid) )
#P.savefig('CompU%d_%s_%s_%s.eps' % (maxalt, year, rv, grid) )

if __name__ == '__main__':
  x = [ 1.0, 2.0, 3.3, 3.9, 5.2, 5.3 ]
  y = [ 1.2, 2.2, 2.7, 3.5, 5.2, 2.2 ]
  c = [ 'AT92', 'AA', 'CCC', 'DDD', 'EEE', 'OUT' ]
  #p=emepscatplot(x,y,'Testx','Testy')
  #maxalt=300   # Max altitude of stations
  #aot   = r'AOT40$_\mathrm{f}$'

  p=emepscatplot(x,y,'Testx','Testy',addStats=True,dbg=True)
  p=emepscatplot(x,y,'Testx','Testy',label='LABEL',addStats=True,dbg=True)

 # Illustrate some styles

  for style in 'bmh ggplot seaborn-colorblind seaborn-deep'.split():
    print('TESTING STYLE', style)
    p=emepscatplot(x,y,'Testx','Testy',label=style,plotstyle=style,addStats=True,dbg=True)
#    p.show()

  #p=emepscatplot(x,y,'Testx','Testy',addStats=True,pcodes=c,ofile='TestPlots.png')

