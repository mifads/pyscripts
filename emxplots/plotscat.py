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
  sys.exit()

def getBias(x,y):
    sumBias=0.0
    for obs, mod in zip(x,y):
        sumBias += (mod-obs)
    return sumBias/len(x)

def getNME(x,y):
    sumObs=0.0
    sumErr=0.0
    for obs, mod in zip(x,y):
        sumErr += np.abs(obs-mod)
        sumObs += obs
    return 100*sumErr/sumObs # normalised mean error, as %

#============================================================================

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
  
#============================================================================

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
    addNME=False,
    addBias=False,
    biasUnits=None,
    skipOutliers=False,dbg=False,ofile=None):

  """
   Scatter plot, emepscatplot(x,y,xlabel,ylabel,txt=None,pcodes=None,addxy=0.0,
      addStats=False,ofile=None)
  """
  dtxt = 'emepscatplot'
  col_def     = 'k'
  col_valid   = 'b'
  col_outlier = 'r'
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

  # fig, ax allows ax.transAxes for better label poistion
  # see stackoverflow.com/questions/62856272/position-font-relative-to-axis-using-ax-text-matplotlib
  fig, ax = plt.subplots()
  #  x = np.log(x)
  #  y = np.log(y)

  ax.scatter(x,y,color=col_valid)   # Start with same colour for all
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
    ax.set_title(title, fontsize=labelsize)
  if label: # Hard-coded position so far, top-left
    ax.text(labelx,labely,label, fontsize=labelsize,transform=ax.transAxes)
  print('XYLAB', maxv, minv, labelx*maxv, labely*maxv, v, xlabel,label)
  ax.set_aspect('equal')
    

###########################################################################
  # Regression stats:
  [m,c]=np.polyfit(x,y,1)
  r=np.corrcoef(x,y)
###########################################################################
  skipi = np.zeros(len(x),dtype='int')
  skipL = np.full(len(x),True,dtype=bool)
  skip = [] 
  if skipOutliers:
     #try:
       regression= ols("data ~x",data=dict(data=y,x=x)).fit()
       test = regression.outlier_test()  # Find outliers 
       #DS outliers = ((x[i],y[i]) for i,t in enumerate(test.icol(2)) if t < 0.5)
       #for i,t in enumerate(test.icol(2)):
       for i,t in enumerate(test.iloc[:,2]):
         skipL[i] = t < 0.5
         if t < 0.5:
           skipi[i] = 1
           skip.append(i)
           print(dtxt+'SKipping ', i, x[i], y[i] )
       #print(dtxt+'SKIPi,n=', len(skip), skipL )
       ax.scatter(x[skipL],y[skipL],color=col_outlier)
       #sys.exit()

#     except: # where stats not implemented Test own outliers
#       g = []
#       for i in range(0,len(x)):
#         g.append( geom.distancePoint2line( x[i],y[i], m, -1.0, c ) )
#         print('GEOM', i, x[i], y[i], pcodes[i], geom.distancePoint2line( x[i],y[i], m, -1.0, c ))
#       print('MAXGEOM', max( g ))
#       for i in range(0,len(x)):
#         if g[i] > 0.5* max(g):
#             skipi[i] = 1
#             skip.append(i)

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
      col = col_valid # 'k'
      if skipi[n] : col=col_outlier # 'r'
      print(dtxt, n, skipi[n], pcodes[n], x[n], y[n])
      ax.text(x[n],y[n],label,color=col,fontsize=10)

#### 1:1 line  ############################################################

  print('MAXv ', maxv, minv)

  lin=(minv,maxv) # 1:1 line
  ax.plot(lin,lin,'g--')

#### regression line - all data ###########################################
  #[m,c]=np.polyfit(x,y,1) #r=np.corrcoef(x,y)

  fit=( c+m*lin[0], c+m*lin[1] )
  if skipOutliers:
    ax.plot(lin,fit,'r--')
  elif regline_wanted:
    ax.plot(lin,fit,'k--')

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
    fitn=( cn+mn*lin[0], cn+mn*lin[1] )
    ax.plot(lin,fitn,'b--') # non outliers in blue
    print('SKIPFIT ', mn, cn, lin[0], lin[1], fitn )


  vspan = maxv+abs(minv)  # complete axis length
  if statsxy is not None:
    vpos=minv + statsxy[1]*vspan  # vertical position for text
  else:
    vpos=minv + 0.17*maxv   # vertical position  for text below
    statsxy = [ 0.01, 0.95 ]   # Oct 28 2022 testing
  dvpos=0.05*vspan   # increment between text lines

  if addStats:

     regline = 'y= %4.2f x + %6.1f'%( m, c)
     #SKIP? if np.abs(c) < 1.0e-4*np.max(y):  #????
     signtxt = ' + '
     if c < 0.0: signtxt = ' '   # minus part of number
     regtxt  = r'$y= %4.2f x %s %6.1f$'%( m, signtxt, c)
     corrtxt  = r'Corr.= %6.2f'%r[0,1]
     if addStats4: 
         regline = r'$y= %6.4f x %s %6.3f$'%( m,signtxt,  c)
         corrtxt  = r'Corr.= %8.4f'%r[0,1]
     if addNME:
       nme = getNME(x,y)
       print("NME = " , nme) 
       corrtxt += ',  NME= %.1f%%'%nme
     if addBias:
       bias = getBias(x,y)
       print("Bias = " , bias) 
       #corrtxt += ',  Bias= %.1f r"%s"'%( bias, biasUnits)
       #corrtxt += ',  Bias= %.1f %s'%( bias, r"$\mu$g/m$^3$")
       corrtxt += ',  Bias= %.1f %s'%( bias, biasUnits )
     xpos = minv + 0.6*vspan
     if statsxy is not None:
       xpos = minv + statsxy[0]*vspan
     print('TTTTT', m, c, maxv, minv, vpos, vspan, xpos)
     print('XYSTAT', maxv, minv, labelx*maxv, labely*maxv, v, xlabel,label)
     # Switch to using ax.transAxes
     #tips from https://stackoverflow.com/questions/62856272/position-font-relative-to-axis-using-ax-text-matplotlib
     dvpos = 0.05 # ax coords 0-1
     print('XPOS VPOS VVV AA', xpos, vpos, dvpos, minv, maxv, vspan )
     print('STATSXY', statsxy)
     plt.figtext(statsxy[0],statsxy[1],regline,color=col_outlier,fontsize=12,transform=ax.transAxes)
     plt.figtext(statsxy[0],statsxy[1]-0.05,corrtxt,color=col_outlier,fontsize=12,transform=ax.transAxes)

  if skipOutliers: # Now text for non-outliers in black
     vpos -= dvpos
     plt.figtext(0.01,0.85,'y= %4.2f x + %6.1f'%( mn, cn),color=col_valid,fontsize=12,transform=ax.transAxes)
     vpos -= dvpos
     corrtxt  = r'Corr.= %6.2f'%rn[0,1]
     if addNME:
       nme = getNME(xn,yn)
       print("NME = " , nme) 
       corrtxt += ',  NME= %.1f%%'%nme
     if addBias:
       bias = getBias(xn,yn)
       print("Bias = " , bias) 
       corrtxt += ',  Bias= %.1f %s'%( bias, biasUnits )
     plt.figtext(0.01,0.80,corrtxt,color=col_valid,fontsize=12,transform=ax.transAxes)
  if minxy is not None:
    minv=minxy
  ax.axis([minv,maxv,minv,maxv])

  if txt:  # place in upper left
    vpos=minv+0.90*vspan   #  vertical position  for text below, was 0.22
    xpos = minv + 0.01*vspan
    ax.text(xpos,vpos,txt,color='k',fontsize=12)

  plt.tight_layout()
  if ofile:
    print(dtxt+'SAVES ', ofile)
    plt.savefig(ofile,bbox_inches='tight')
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

# =========================================================================== !
if __name__ == '__main__':
  import argparse
  import os
  import xarray as xr

  #------------------ arguments  ----------------------------------------------
  
  #parser=argparse.ArgumentParser(usage=__doc__) also works, but text at start
  parser=argparse.ArgumentParser(epilog=__doc__,
     formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v','--varkey',help='varname',required=False) # True)
  parser.add_argument('-d','--demo',help='Shows example plots',action='store_true')
  #parser.add_argument('-i','--ifiles',help='Input files',nargs='*',required=False) # True)
  parser.add_argument('-i','--ifiles',help='Input files',nargs=2,required=False) # True)
  parser.add_argument('-m','--maskvar',help='mask variable',nargs=1,required=False) # True)
  parser.add_argument('-o','--ofile',help='output file',required=False)
  parser.add_argument('-p','--plot',help='plot on screen?\n(Optional)',action='store_true')
  parser.add_argument('-L','--labels',help='labels, e.g. -L"rv4.15 rv4.15a"\n(Optional)',nargs=2,required=False)
  parser.add_argument('-t','--title',help='title',required=False)
  args=parser.parse_args()
  print('ARGS ', args)
  if args.labels:
    xlab, ylab = args.labels
  else:
    xlab, ylab = 'x-vals', 'y-vals'

#------------------ arguments  ----------------------------------------------

  if args.demo:

    x = [ 0.009996590476190477,0.011191434070061063,0.012558233597911746,0.0072396302425059515,0.026974358974358976 ]
    y = [ 0.010964822955429554,0.009696880355477333,0.010967271402478218,0.007331404369324446,0.003907112404704094 ]
    c= [ s[:3]+s[4:6] for s in 'CZ0003R,DE0002R,DE0007R,DE0009R,FR0015R'.split(',')  ]
      
  
   # Illustrate some styles
  
    #for style in 'bmh ggplot seaborn-colorblind seaborn-deep'.split():
    for style in 'ggplot'.split():

      print('TESTING STYLE', style)

      p=emepscatplot(x,y,'Obs.','Mod.',pcodes=c,label='nC7H16',labely=0.1,
           plotstyle=style,addStats=False,dbg=True,skipOutliers=False,ofile='Demo_allpoints.png')
      p=emepscatplot(x,y,'Obs.','Mod.',pcodes=c,label='nC7H16',labely=0.1,
           plotstyle=style,addStats=True,dbg=True,skipOutliers=True,ofile='Demo_excpoints.png')

      #p=emepscatplot(x,y,'Testx','TestLog',label=style,plotstyle=style,addStats=True,loglog=True,dbg=True,minv=3.0)
      #p= emeploglogplot(x,y,'Testx','Testy',txt=None,pcodes=None)
      #p= emeploglogplot(x,y,'Testx','Testy',txt=None,pcodes=c)
      #p.show()
  
  
  elif args.ifiles:
    v = args.varkey
    assert args.varkey,'NEED varkey (-v) also!'
    assert v,'NEED v (-v) also!'
    print('Files', args.ifiles)
    n=0
    vals=dict()
    for ifile in args.ifiles:
      assert os.path.isfile(ifile),"FILE %s doesn't exist" % ifile
      ds=xr.open_dataset(ifile)
      assert v in ds.keys(),'No %s in %s'% ( v, ifile )
#      if n==0 and args.maskvar:
#        mask=ds[args.maskvar].values[:,:].flatten()
     
      print('KEY found ', v )
      vals[n]=ds[v].values[0,:,:].flatten()
      print(n, len(vals[n]), np.shape(vals[n]) )
      n += 1
    for style in 'ggplot'.split():
      ofile= args.ofile
      p=emepscatplot(vals[0],vals[1],xlab,ylab,title=v,plotstyle=style,addStats=True,ofile=ofile) #,dbg=True)

      

