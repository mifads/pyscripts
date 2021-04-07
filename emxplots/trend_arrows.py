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
from matplotlib.gridspec import GridSpec
# arrows:
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
#p <= 0.05:   # dark blue/brown #0.05<p<0.1       # blue/orange for 
# 0.1<p<0.34  # yellow/lightblue #p>034            # green 

  """ colours found using gpick and Chang article """
  if abs(p)>0.34 : col = '#AEC283' # 'gray' # darkseagreen' #'sage'
  elif p > 0.1   : col = '#7CB8FC' # 'skyblue'
  elif p > 0.05  : col = '#1A69EC' # 'blue'
  elif p > 0.0   : col = '#04008D' # 'midnightblue'
  elif p > -0.05 : col = '#9D0427' # 'brown'
  elif p > -0.1  : col = '#F2650E' # 'orange'
  elif p > -0.34 : col = '#F7BA67' # 'yellow'
  else: col = 'r'
  return col


def sample_1d():
  x = np.linspace(-30.0,60.0, 30)
  y = np.linspace(45.0, 74.8, 30)
  u = 10 * (2 * np.cos(2 * np.deg2rad(x) + 3 * np.deg2rad(y + 30)) ** 2)
  v = 20 * np.cos(6 * np.deg2rad(x))
  p = v # fake p.value
  return x, y, u, v, p #, crs



def annotate_axes(fig):
  for i, ax in enumerate(fig.axes):
      ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
      ax.tick_params(labelbottom=False, labelleft=False)


#fig = plt.figure()
#fig.suptitle("Controlling subplot sizes with width_ratios and height_ratios")
#
#annotate_axes(fig)
#

def trend_arrows(x0,x1,y0,y1,x,y,u,v,p,scale_arrows=None,plotfile=None,
   title=None,inset=False,insText='ppb/yr',cbars=True,insUp=1,dbg=False):

  crs=ccrs.PlateCarree()
  fig = plt.figure(figsize=[10.5,5.8])  # 10.5"
  proj=ccrs.PlateCarree()
  # from demo_gridspec03.py, 
  
  gs2 = GridSpec(2, 2, left=0.02, right=0.98, width_ratios=[5,1],wspace=0.001)
  ax  = fig.add_subplot(gs2[:, :-1],projection=proj)
  axu = fig.add_subplot(gs2[:-1, -1],projection=proj)  # ur 
  axl = fig.add_subplot(gs2[-1, -1])                   # ll for colours

  resol='50m'
#  ax.add_feature(cfeature.OCEAN, zorder=0)
#  ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
#  ax.add_feature(cfeature.BORDERS, zorder=0, edgecolor='lightgrey')
# following https://stackoverflow.com/questions/62308857/borders-and-coastlines-interfering-in-python-cartopy
  bodr = cfeature.NaturalEarthFeature(category='cultural', 
    name='admin_0_boundary_lines_land', scale=resol, facecolor='none', alpha=0.7)
  land = cfeature.NaturalEarthFeature('physical', 'land', \
    scale=resol, edgecolor='k', facecolor=cfeature.COLORS['land'])
  ocean = cfeature.NaturalEarthFeature('physical', 'ocean', \
    scale=resol, edgecolor='none', facecolor=cfeature.COLORS['water'])
#  lakes = cfeature.NaturalEarthFeature('physical', 'lakes', \
#    scale=resol, edgecolor='b', facecolor=cfeature.COLORS['water'])
#  rivers = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', \
#    scale=resol, edgecolor='b', facecolor='none')

  ax.add_feature(land, facecolor='beige',zorder=0)
  ax.add_feature(ocean, linewidth=0.2,zorder=0 )
  ax.add_feature(bodr, edgecolor='lightgrey', zorder=0)
  #ax.add_feature(bodr, linestyle='--', edgecolor='lightgrey', alpha=1,zorder=0)
#  ax.add_feature(lakes)
#  ax.add_feature(rivers, linewidth=0.5)
  ax.set_global()

  # Arrows on map:
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
    if dbg: print(n, x[n],y[n],u[n], dx,  r, 'P:', p)
    if p is not None:
      col=rgbcolor(p[n])
    kwargs=dict(color=col,width=0.2,overhang=0.5)

    ax.arrow(x[n],y[n],fac*dx,fac*dy,**kwargs) #,transform=crs)

  ax.set_xlim([x0,x1])
  ax.set_ylim([y0,y1])
  if title is not None:
    fig.suptitle(title)

  # Arrows in upper legend
  kwargs=dict(color='k',width=0.02,overhang=0.5)
    # centre at x=dR, y=2dR
  degs=np.linspace(90.,-90.,num=5,endpoint=True)
  dR=1.0
  x0=0.5;y0=3.5
  axu.text(x0,6.0,'ppb/yr')
  for d in degs:
    dx=dR * np.cos(np.deg2rad(d))
    dy=dR * np.sin(np.deg2rad(d))
    axu.arrow(x0,y0,dx,dy, **kwargs) # up
    va='bottom'; ha='left'
    # Tweaks:
    if dy<0: va='top'
    if abs(d) > 50:
      dx = 0.0
      ha='center'
      dy *= (1.3*dR)
    axu.text(x0+dx,y0+dy,'%+.1f' % (insUp*d/90.0),va=va,ha=ha)
    
  axu.set_xlim([0.0,5.0])
  axu.set_ylim([2.0,7.0])
  axu.axis('off')

  if cbars:
    dR=1.0
    axl.set_facecolor('lightgrey')
    y=2*dR
    axl.plot([dR,2*dR],[y,y],lw=4,c=rgbcolor(0.001))
    axl.plot([2.2*dR,3.2*dR],[y,y],lw=4,c=rgbcolor(-0.001))
    axl.text(3.3*dR,y,r'p$<$0.05',va='center',ha='left')
    y=1.4*dR
    axl.plot([dR,2*dR],[y,y],lw=4,c=rgbcolor(0.06))
    axl.plot([2.2*dR,3.2*dR],[y,y],lw=4,c=rgbcolor(-0.06))
    axl.text(3.3*dR,y,r'0.05$<$p$<$0.10',va='center',ha='left')
    y=0.8*dR
    axl.plot([dR,2*dR],[y,y],lw=4,c=rgbcolor(0.11))
    axl.plot([2.2*dR,3.2*dR],[y,y],lw=4,c=rgbcolor(-0.11))
    axl.text(3.3*dR,y,r'0.10$<$p$<$0.34',va='center',ha='left')
    y=0.2*dR
    axl.plot([1.5*dR,2.5*dR],[y,y],lw=4,c=rgbcolor(1.0))
    axl.text(3.3*dR,y,r'p$>=$0.34',va='center',ha='left')
    axl.set_xlim([0.9,7.0])
    axl.set_ylim([0.0,3.0])
    axl.axis('off')

  
  #annotate_axes(fig)
  #plt.tight_layout(pad=0.01)
  if plotfile is not None:
    print('SAVE PLOT', plotfile)
    plt.savefig(plotfile)
  else:
    plt.show()
  #plt.clear()
  plt.clf()# plt.gca())
  return

  
  #plt.show()
  
  
if __name__ == '__main__':

  x, y, u, v, p = sample_1d()
  t=trend_arrows(-40,40,0.,80.,x,y,u,v,p,title='Demo',inset=True)

  
