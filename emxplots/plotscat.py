#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import emxmisc.geometry as geom
import sys

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

def emeploglogplot(x,y,xlabel,ylabel,txt=None,pcodes=None): #,label=None,
  plt.style.use('seaborn')
  #y[-1] = 10.0
  logx = np.log10( np.array(x))
  logy = np.log10( np.array(y))
  plt.scatter(x,y)
  for i in range(len(x)):
     p= pcodes[i] if pcodes else '#%d'%i
     print( 'INTO emepscatplot p,x,y: ', p, x[i], y[i], logx[i], logy[i] )
     if pcodes is not None:
       label = '%4s'%p
       plt.text(x[i],y[i],p,color='k',fontsize=10)
  t= plt.xticks()
  print('TTT', t)
  plt.xscale('log')
  plt.yscale('log')
  plt.axis('equal')
  plt.show()
  

def emepscatplot(x,y,xlabel,ylabel,txt=None,pcodes=None,label=None,
    title=None,
    plotstyle='seaborn',
    labelx=0.1,labely=0.9,labelsize=16,
    addxy=0.0,  # Increases maxv to e.g. cope with label  overwrites
    minxy=None,  # lower  value limit for plots
    statsxy=None, # loc reg stats text, e.g. (0.5,0.8)
    loglog=False,
    regline_wanted=True,
    addStats=False,addStats4=False,  # 4 gives 4 figs
    skipOutliers=False,dbg=False,ofile=None):

  """
   Scatter plot, emepscatplot(x,y,xlabel,ylabel,txt=None,pcodes=None,addxy=0.0,
      addStats=False,ofile=None)
  """
  dtxt = 'emepscatplot'
  plt.style.use(plotstyle)
  x = np.array(x)
  y = np.array(y)
  if addStats4: addStats = True  # 4 just gives extra prec
  if dbg:
   print( dtxt+' lengths x,y: ', len(x), len(y) )
   print( dtxt+' shape x, y: ', x.shape, y.shape )
   print( dtxt+' plotstyle : ', plotstyle)
   for i in range(len(x)):
     p= pcodes[i] if pcodes else '#%d'%i
     print( 'INTO emepscatplot p,x,y: ', p, x[i], y[i] )
#vlimit=300.0
#f=alt<vlimit
  plt.clf()
  #OCT21 plt.subplot(111)
  # fig, ax allows ax.transAxes for better label poistion
  # see stackoverflow.com/questions/62856272/position-font-relative-to-axis-using-ax-text-matplotlib
  fig, ax = plt.subplots()
  #  x = np.log(x)
  #  y = np.log(y)
  #OCT21 fig=plt.scatter(x,y,color='b')
  ax.scatter(x,y,color='b')
  if loglog is True:
    t= ax.xticks()
    print('TTT', t)
    ax.xticks([1.0e-2,5.0e-2,0.1,0.3,0.5,0.7,1.0,3.0,1.0e2])
    ax.yticks([1.0e-2,5.0e-2,0.1,0.3,0.5,0.7,1.0,3.0,1.0e2])
    ax.xscale('log')
    ax.yscale('log')
  ax.set_xlabel(xlabel, fontsize=12)
  ax.set_ylabel(ylabel, fontsize=12)
  v=ax.axis()
  maxv=max(v)
  minv=min(v)

  if addxy>0.0:
      maxv += addxy
  if title: # Hard-coded position so far, top-left
    ax.title(title, fontsize=labelsize)
  if label: # Hard-coded position so far, top-left
    ax.text(labelx,labely,label, fontsize=labelsize,transform=ax.transAxes)
  print('XYLAB', maxv, minv, labelx*maxv, labely*maxv, v, xlabel,label)
  #plt.gca().set_aspect('equal')
  ax.set_aspect('equal')
    

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
       print(dtxt+'SKIPi,n=', len(skip) )
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
      ax.text(x[n],y[n],label,color=col,fontsize=10)

#J8  v=plt.axis() #J8  maxv=max(v)

#### 1:1 line  ############################################################

  print('MAXv ', maxv, minv)

  #lin=(0,maxv) # 1:1 line
  lin=(minv,maxv) # 1:1 line
  ax.plot(lin,lin,'g--')

#### regression line - all data ###########################################
  #[m,c]=np.polyfit(x,y,1) #r=np.corrcoef(x,y)

  #BUG fit=( c, c+m*lin[1] )
  fit=( c+m*lin[0], c+m*lin[1] )
  if skipOutliers:
    ax.plot(lin,fit,'r--')
  elif regline_wanted:
    ax.plot(lin,fit,'k--')
  #plt.plot(lin,fit,'c--')

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
    ax.plot(lin,fitn,'k--') # non outliers in black

  vspan = maxv+abs(minv)  # complete axis length
  if statsxy is not None:
    vpos=minv + statsxy[1]*vspan  # vertical position for text
  else:
    vpos=minv + 0.17*maxv   # vertical position  for text below
  dvpos=0.05*vspan   # increment between text lines

  if addStats:

     regline = 'y= %4.2f x + %6.1f'%( m, c)
     col='b'
     if skipOutliers: col='r'  # keep black for non-outliers
     #SKIP? if np.abs(c) < 1.0e-4*np.max(y):  #????
     signtxt = ' + '
     if c < 0.0: signtxt = ' '   # minus part of number
     regtxt  = r'$y= %4.2f x %s %6.1f$'%( m, signtxt, c)
     corrtxt  = r'Corr.= %6.2f'%r[0,1]
     if addStats4: 
         regline = r'$y= %6.4f x %s %6.3f$'%( m,signtxt,  c)
         corrtxt  = r'Corr.= %8.4f'%r[0,1]
     xpos = minv + 0.6*vspan
     if statsxy is not None:
       xpos = minv + statsxy[0]*vspan
     print('TTTTT', m, c, maxv, minv, vpos, vspan, xpos)
     #plt.text(xpos,vpos,regline,color=col,fontsize=12)
     #plt.figtext(labelx,labely-0.05,regline,color=col,fontsize=12)
     print('XYSTAT', maxv, minv, labelx*maxv, labely*maxv, v, xlabel,label)
     # Switch to using ax.transAxes
     #tips from https://stackoverflow.com/questions/62856272/position-font-relative-to-axis-using-ax-text-matplotlib
     dvpos = 0.05 # ax coords 0-1
     ax.text(labelx,labely-dvpos,regline,color=col,fontsize=12,transform=ax.transAxes)
     #vpos -= dvpos
     #plt.text(xpos,vpos,corrtxt,color=col,fontsize=12)
     ax.text(labelx,labely-2*dvpos,corrtxt,color=col,fontsize=12,transform=ax.transAxes)

  if skipOutliers: # Now text for non-outliers in black
     vpos -= dvpos
     ax.text(xpos,vpos,'y= %4.2f x + %6.1f'%( mn, cn),color='k',fontsize=12)
     vpos -= dvpos
     ax.text(xpos,vpos,'Corr.= %6.2f'%rn[0,1],color='k',fontsize=12)
  if minxy is not None:
    minv=minxy
  ax.axis([minv,maxv,minv,maxv])

  if txt:  # place in upper left
    vpos=minv+0.90*vspan   #  vertical position  for text below, was 0.22
    xpos = minv + 0.01*vspan
    ax.text(xpos,vpos,txt,color='k',fontsize=12)
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

  #p=emepscatplot(x,y,'Testx','Testy',addStats=True,dbg=True)
  #p=emepscatplot(x,y,'Testx','Testy',label='LABEL',addStats=True,dbg=True)

 # Illustrate some styles

  #for style in 'bmh ggplot seaborn-colorblind seaborn-deep'.split():
  for style in 'ggplot'.split():
    print('TESTING STYLE', style)
    #p=emepscatplot(x,y,'Testx','Testy',label=style,plotstyle=style,addStats=True,dbg=True)
    #p=emepscatplot(x,y,'Testx','Testy',label=style,plotstyle=style,addStats=True,dbg=True,minv=3.0)
#    p=emepscatplot(x,y,'Testx','TestLog',label=style,plotstyle=style,addStats=True,loglog=True,dbg=True,minv=3.0)
    p= emeploglogplot(x,y,'Testx','Testy',txt=None,pcodes=None)
    p= emeploglogplot(x,y,'Testx','Testy',txt=None,pcodes=c)
#    p.show()

  #p=emepscatplot(x,y,'Testx','Testy',addStats=True,pcodes=c,ofile='TestPlots.png')

