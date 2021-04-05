#!/usr/bin/env python3
"""
Arrows
------

Plotting  trends as arrows on maps. Inspired by Owen Cooper's O3 plots.
Following TOAR approaches, we also colour according to p values,
with dark blue/brown fr p<=0.05, blue/orange for 0.05<p<0.1,
yellow/lihtblue for 0.1<p<0.34, and green for p>=0.34
(cf Kai-Lan CHang et al., 2017, https://doi.org/10.1525/elementa.243)

p <= 0.05:       # dark blue/brown 
0.05<p<0.1       # blue/orange for 
 0.1<p<0.34      # yellow/lihtblue
p>034            # green 

"""
import matplotlib.pyplot as plt
import numpy as np
import sys

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import cm
import matplotlib.colors as colors

cmap=cm.coolwarm
#norm=colors.CenteredNorm()

def pcolor(p):
#p <= 0.05:       # dark blue/brown 
#0.05<p<0.1       # blue/orange for 
# 0.1<p<0.34      # yellow/lightblue
#p>034            # green 

  if   p>0.34    : col = 'gray' # darkseagreen' #'sage'
  elif p > 0.1   : col = 'skyblue'
  elif p > 0.05  : col = 'blue'
  elif p > 0.0   : col = 'midnightblue'
  elif -p > 0.05 : col = 'brown'
  elif -p > 0.1  : col = 'orange'
  elif -p > 0.34 : col = 'yellow'
  else: col = 'r'
  return col

def rgbcolor(p):
#p <= 0.05:       # dark blue/brown 
#0.05<p<0.1       # blue/orange for 
# 0.1<p<0.34      # yellow/lightblue
#p>034            # green 

  """ colours found using gpick and Chang article """
  if   p>0.34    : col = '#AEC283' # 'gray' # darkseagreen' #'sage'
  elif p > 0.1   : col = '#7CB8FC' # 'skyblue'
  elif p > 0.05  : col = '#1A69EC' # 'blue'
  elif p > 0.0   : col = '#04008D' # 'midnightblue'
  elif -p > 0.05 : col = '#9D0427' # 'brown'
  elif -p > 0.1  : col = '#F2650E' # 'orange'
  elif -p > 0.34 : col = '#F7BA67' # 'yellow'
  else: col = 'r'
  return col

def sample_1d():
    x = np.linspace(-30.0,60.0, 30)
    y = np.linspace(45.0, 74.8, 30)
    u = 10 * (2 * np.cos(2 * np.deg2rad(x) + 3 * np.deg2rad(y + 30)) ** 2)
    v = 20 * np.cos(6 * np.deg2rad(x))
    p = v # fake p.value
    return x, y, u, v, p #, crs


def trend_arrows(x0,x1,y0,y1,x,y,u,v,p,scale_arrows=None,plotfile=None,
   title=None,inset=False,insText='ppb/yr',insUp=1):

  crs=ccrs.PlateCarree()
  fig = plt.figure()
  ax = fig.add_subplot(1,1,1,projection=ccrs.PlateCarree())

  ax.add_feature(cfeature.OCEAN, zorder=0)
  ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
  ax.set_global()

  fac=2
  if scale_arrows is not None:
    fac *= scale_arrows
  col='b'
  for n in range(len(x)):
    dx=u[n]
    dy=v[n] 
    r=np.sqrt(dx**2 + dy**2)
    dx /= r # make all arrows same length
    dy /= r
    print(n, x[n],y[n],u[n], dx,  r, 'P:', p)
    if p is not None:
      col=rgbcolor(p[n])
    kwargs=dict(color=col,width=0.2,overhang=0.5)
     

    ax.arrow(x[n],y[n],fac*dx,fac*dy,**kwargs) #,transform=crs)

  ax.set_xlim([x0,x1])
  ax.set_ylim([y0,y1])
  if title is not None:
    plt.title(title)

  if inset:
    #axins = ax.inset_axes([0.8,0.1,0.2,0.2])
    # keep x/y ratio consistent with xlim,ylim below
    axins = ax.inset_axes([1.0,0.3,0.3,0.25])
    #axins.plot([1.0,2.0,3.0,1.0])
    kwargs=dict(color='k',width=0.0002,overhang=0.5)
    # centre at x=dR, y=2dR
    dR=1.0
    axins.arrow(dR,2*dR,0.0,dR, **kwargs) # up
    axins.arrow(dR,2*dR,dR ,0.0,**kwargs) # horiz
    axins.arrow(dR,2*dR,0.0,-dR, **kwargs)# down
    axins.set_xlim([0.0,6.0])
    axins.set_ylim([0.0,5.0])
    axins.text(0.5*dR,4.0*dR,'ppb/yr')
    axins.text(0.7*dR,3.1*dR,'+%d' % insUp)
    axins.text(3.1*dR,2*dR,'0',va='center')
    axins.text(0.6*dR,0.5*dR,'-%d' % insUp)
    #axins.set_xticklabels('')
    #axins.set_yticklabels('')
    #axins.tick_params(axis='both',which='both',...
    axins.axis('off')


  if plotfile is not None: 
    print('SAVE PLOT', plotfile)
    plt.savefig(plotfile)
  plt.show()
  #plt.clear()
  plt.clf()# plt.gca())
  return

def trend_quivers(x0,x1,y0,y1,x,y,u,v,c,plotfile=None):

  fig = plt.figure()
  ax = fig.add_subplot(1,1,1,projection=ccrs.PlateCarree())

  ax.add_feature(cfeature.OCEAN, zorder=0)
  ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')

  ax.set_global()
  #ax.gridlines()

  #ax.quiver(x, y, u, v, scale=100)# color=w) #, transform=vector_crs)
  #ax.quiver(x, y, u, v, color=v,norm=colors.CenteredNorm()) #, transform=vector_crs)
  #ax.quiver(x, y, u, v, color=v,norm=colors.DivergingNorm(vmin=np.min(v),vcenter=0.0,vmax=np.max(v))) #, transform=vector_crs)
  #ax.quiver(x, y, u, v, color=v,norm=colors.TwoSlopeNorm(vmin=np.min(v),vcenter=0.0,vmax=np.max(v))) #, transform=vector_crs)

  #x2=x+5.0
  print('COOPER typ', type(v) )
  f=c>1.0
  ax.quiver(x[f], y[f], u[f], v[f], color='r') #, transform=vector_crs)
  f=np.logical_and(c>0.0,c<=1.0)
  ax.quiver(x[f], y[f], u[f], v[f], color='salmon') #, transform=vector_crs)
  f=np.logical_and(c<0.0,c>= -1.0)
  ax.quiver(x[f], y[f], u[f], v[f], color='lightblue') #, transform=vector_crs)
  f= c < -1
  ax.quiver(x[f], y[f], u[f], v[f], color='b') #, transform=vector_crs)

  kwargs=dict(headwidth=1,headlength=0.5,headaxislength=1)
  #ax.quiver(x, y, u, v,**kwargs) #, color='r') #, transform=vector_crs)
  #ax.quiver(x, y, u, v,headwidth=1,headlength=0.5,headaxislength=1) #, color='r') #, transform=vector_crs)
  #ax.quiver(x, y, u, v, color='r') #, transform=vector_crs)
  #ax.quiver([10.75], [59.99], [30.], [30.], color='g') #, transform=vector_crs)

  ax.set_xlim([x0,x1])
  ax.set_ylim([y0,y1])

  if plotfile is None:
    plt.show()
  else:
    plt.show()
    plt.savefig(plotfile)
 
  plt.clf()

if __name__ == '__main__':
  
  x, y, u, v, p = sample_1d()
  t=trend_arrows(-40,40,0.,80.,x,y,u,v,p,inset=True)

