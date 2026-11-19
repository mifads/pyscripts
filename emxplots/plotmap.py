#!/usr/bin/env python3
"""
   Very simple map plotting, using imshow.
   or for simple points on nice background map.
   For more advanced, use plotCdfMap.py

   Methods:
    plotmap
    plotlonlatmap
    plot_map_pts
    plotPSmap
"""
import matplotlib.pyplot as plt
import numpy as np
import netCDF4
import os
import sys

#============================================================================
def plotmap(x,txt,plotfile=None,cmap='jet',vmin=None,vmax=None):
  """ simplest imshow map. Use jet_r to match Hudman """
  if vmax is None:
    plt.imshow(x,origin='lower',cmap=cmap) 
  else:
    plt.imshow(x,origin='lower',cmap=cmap,vmin=vmin,vmax=vmax) 
  plt.colorbar()
  #TMP plt.title(f"PLOTMAP: {txt} {x[50,2]}")
  plt.title(txt)
  if plotfile is None:
    plt.show()
  else:
    plt.savefig(plotfile)
  plt.clf()

#============================================================================
def plotlonlatmap(lons,lats,vals,levels,
        title=None,
        cmap='nmr', 
        img_bounds= [-30.0, 55.0, 30.0, 65.0 ],
        cbar_shrink=0.5,cbar_title=None,idbg=None,jdbg=None,ofile=None
    ):
  """ maps with cartopy world also """
  import cartopy.crs as ccrs
  from matplotlib.colors import ListedColormap, BoundaryNorm # for hetero, from Zhuyun/NMR
  nmrcolors = ['#CCDEEB', '#96CCEB', '#66B7F3', '#62C298', '#76E854','#EAEB30',
     '#E4CC2F', '#EA952A','#F74B37', '#C52C2C']
 
  if cmap == 'nmr':
    cm = ListedColormap(nmrcolors)
  else:
    cm = plt.colormaps[cmap]
  cm.set_under('0.75')
  cm.set_over('0.25')
  norm = BoundaryNorm(levels, ncolors=cm.N, clip=False)
  proj = ccrs.PlateCarree()
  fig = plt.figure(figsize=(10, 4))
  f, ax1 = plt.subplots(1, 1, subplot_kw=dict(projection=proj))
  ax1.set_extent(img_bounds,crs=ccrs.PlateCarree())
  ax1.coastlines(resolution='10m') # 10, 50, 110
  ax1.gridlines()
  #cmap = ListedColormap(nmrcolors)
  print('DBGCM', cmap, cm)
  p=ax1.pcolormesh(lons,lats,vals,cmap=cm,norm=norm,transform=ccrs.PlateCarree())
  #cbar=plt.colorbar(hhh,cax=ax_cb,ticks=v,extend='both')
  #cbar=plt.colorbar(p,ticks=levels,extend='both')
  cbar=plt.colorbar(p,extend='both',shrink=cbar_shrink)
  
  if cbar_title is not None:
      cbar.ax.set_title(cbar_title)
 
  if title is not None: plt.title(title)
  plt.tight_layout()
  if idbg is not None:
    print(f'DBGplotlonlatmap: {lons[idbg]:.3f}E {lats[jdbg]:.3f}N  VALS{vals[jdbg,idbg]} {cm.N}')
  if ofile is None:
    plt.show()
  else:
    plt.savefig(ofile)
  plt.clf()
  plt.close()

#============================================================================
def plot_map_pts(x,y,z,col='r',title='',img_bounds=[-15.0,60.0,30.0,75.0],ofile=None):

  import cartopy.crs as ccrs

  fig = plt.figure(figsize=(10, 4))
  ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

  # make the map global rather than have it zoom in to
  # the extents of any plotted data
  ax.set_global()

  ax.stock_img()
  ax.coastlines()
  ax.set_extent(img_bounds,crs=ccrs.PlateCarree())

  ax.scatter(x,y,z,color=col)
  if len(title)>0:
    plt.title(title,fontsize=14)

  plt.tight_layout()
  if ofile is None:
    plt.show()
  else:
    plt.savefig(ofile)
  plt.clf()
  plt.close()


#============================================================================
""" Plots data which are in PS emep50 grid units, cf grid50.pdf
  use datadict= e.g. dict(JRC=dat1,SKJ=dat2)
"""
def plotPSmap(title,datadicts,vmin=0,vmax=None,
  plotgrid=False, plotborders=False,dpi=300,
  xtit=0.5,ytit=0.8, subtitle_fontsize=10, halignment_tit='center',
  cbar_shrink=0.5,
   oplot=None,cmap='tab20c',plot_offset=[-35, -11],dbg=False):

  import cartopy.crs as ccrs
  import cartopy.feature as cfeature

  font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

  dtxt='plotPSmap:'
  GRID_CELL_SIZE= 50000   # m
  Rearth = 6370000        # m
  sinPi3 = 0.866025403784438
  # R/50 = 127.4 # - 2008 nx=132; ny=111 #  2008-2016 settings
  nx=132; ny=159
  xpol=8; ypol=110
  M =  237.73        #  R/(d[1+sin 60deg])
  R = 127.4    #  127.4 in grid units → 6.37e6 meters
  projection = ccrs.Stereographic(
       central_latitude=90,
       central_longitude=-32,
       true_scale_latitude=60,
       false_easting  = xpol * GRID_CELL_SIZE,
       false_northing = ypol * GRID_CELL_SIZE,
       globe=ccrs.Globe(
         semimajor_axis=R*GRID_CELL_SIZE,  #  127.4 in grid units → 6.37e6 meters
         semiminor_axis=R*GRID_CELL_SIZE,
         ellipse=None)  # radius in meters
   )

  Nplots = len(datadicts)
  fig, ax = plt.subplots(ncols=Nplots,figsize=(4,3),
                      subplot_kw=dict(projection=projection))
  if dbg: print(f"{dtxt} Nplots = {Nplots}: {title}")
  if Nplots==1: ax = [ax, ]

  # Plot data WITHOUT transform — assume it's already in projection coordinates
  # imshow is tricky. The extent must match the data shape. Use x0, ..
  x0=15;x1=nx-10; y0=0; y1=100

  G50=GRID_CELL_SIZE
  res='50m'  # '110m' # '50m' coastlines
  n = 0
  for key, vals in datadicts.items():
    if plot_offset[0] != 0 or plot_offset[1] != 0:
      vals = np.roll(vals,plot_offset[1],axis=0) # typically -11
      vals = np.roll(vals,plot_offset[0],axis=1) # typically -35

    p = ax[n].imshow(vals[y0:y1,x0:x1], extent=[x0*G50,x1*G50,y0*G50,y1*G50],
      vmin=vmin,vmax=vmax, cmap=cmap, alpha=0.7, zorder=1, origin='lower')
    ax[n].set_title(key,fontsize=subtitle_fontsize)

  # Now add coastlines and set extent   10m,
    ax[n].coastlines(resolution=res,linewidth=0.5, color='k', zorder=5)
    if plotborders:
      ax[n].add_feature(cfeature.BORDERS, linewidth=1, linestyle=':',color='r',zorder=5)
    if plotborders:
      ax[n].gridlines(crs=projection)  # fails: ,draw_labels=True)
    n += 1

  #fig.colorbar(p,ax= ax, shrink=cbar_shrink,anchor=(1.0,0.5))
  fig.colorbar(p,ax= ax, shrink=cbar_shrink)
  plt.suptitle(title,x=xtit,y=ytit,ha=halignment_tit)

  #FAILS plt.tight_layout()

  if oplot is None:
    plt.show()
  elif oplot.endswith(".eps"):
    plt.savefig(oplot)
  else:
    plt.savefig(oplot,dpi=dpi)
  plt.clf()
  plt.close()



if __name__ == '__main__':
  x=np.ones([180,360])  # typical emep domain
  for i in range(360):
      x[:,i] = i

  plotmap(x,'TestX',vmin=0,vmax=600)

  x = np.linspace(-10,40,10)
  y = np.linspace(30,60,10)
  z = np.linspace(0,100,10)
  plot_map_pts(x,y,z,'r')

