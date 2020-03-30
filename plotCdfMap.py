#!/usr/bin/env python3
#plotEmep + http://worksofscience.net/matplotlib/colorbar
# From plotCordex3.py with different projection which was from plotrca....
import matplotlib.pyplot as plt
from  matplotlib.gridspec import GridSpec #see http://worksofscience.net/matplotlib/colorbar
#import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys
    # Put a background image on for nice sea rendering.
    #ax.stock_img()

    # Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
    #states_provinces = cfeature.NaturalEarthFeature(
    #    category='cultural',
    #    name='admin_0_states_provinces_lines',
    #    scale='50m',
    #    facecolor='none')

    #ax.add_feature(cfeature.LAND)
    #ax.add_feature(cfeature.COASTLINE)
    #ax.add_feature(states_provinces, edgecolor='gray')

#from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib as mpl
import netCDF4 as cdf
import numpy as np
import optparse

# --------- parse inputs -----------------
#From plotrca3.py
parser=optparse.OptionParser()

parser.add_option( '-i' ,help="Input file name, map-data")
parser.add_option( '-o' ,help="Output file name", default="Screen")
parser.add_option( '-t' ,help="Title",dest='title')
parser.add_option( '-v' ,help="Variable name",dest='var')

parser.add_option( '-b' ,help="add country boders",dest='borders',default=False,action='store_true')
parser.add_option( '--cmap' , help="cmap, eg --cmap hot,jet_r",
                      default='jet', dest='cmap', action='store',nargs=1)
                      #default='Set3', dest='cmap', action='store',nargs=1)
                     #default='YlOrRd', dest='cmap', action='store',nargs=1)
parser.add_option( '--coast' ,help="Colour of coast",default='r')
parser.add_option( '--skipcbar' ,help="No colourbar",dest='skipcbar')
parser.add_option( '--extent', help="extent (LonL,LonR,LatS,LatN), eg --extent -15.0,40.0,35.0,65.0",
                      default="-15.0,40.0,35.0,65.0",
                      dest='extent', action='store',nargs=1)
parser.add_option( '--levels', help="levels, eg --levels 10,20,40,60",
#                         default="30,70,99,101,149,160.5,170,180",
                      dest='levels', action='store',nargs=1)
parser.add_option( '--over' , help="over, eg --over 0.75 or yellow",
                      default='0.45', # darkish gret
                      dest='over', action='store',nargs=1)
parser.add_option( '--under' , help="under, eg --under 0.25 or cyan",
                      default='0.75', # light grey
                      dest='under', action='store',nargs=1)


(opts, args) = parser.parse_args()

#if __name__ == "__main__":
#   opts.i = "../D7_5stallo/DS_DIFFS25/diffSOMO35_2050_Base_PL_N.nc"
#   opts.var = "SOMO35"
#   opts.title = "TITLE"
#   print "CALLING AS MAIN "
#   opts.i = 'AnavRatio.nc'
#   opts.var = 'Ratio'

   #opts.levels = '10,30,50,70'

if opts.i is None:
   print("\n ERROR No input file specified!!\n")
   parser.print_help()
   exit(-1)

print("OPTS ALL  ", opts)


#-----------------------------------------------------
emepfile= opts.i

ecdf = cdf.Dataset(emepfile,'r',format='NETCDF4')

#S lats=ecdf.variables['lat'][:,:]
#S lons=ecdf.variables['lon'][:,:]
#vals=ecdf.variables[var][0,:,:]  # Jan

if( 'longitude' in ecdf.dimensions ):
  dimx, dimy =( 'longitude', 'latitude')
  print(('DIMS1 are ', dimx, dimy))
elif ( 'lon' in ecdf.dimensions ) :
  dimx, dimy =( 'lon', 'lat')
  print(('DIMS2 are ', dimx, dimy))
else:
  dimx, dimy = ('-', '-')
  print("ERROR")

print(('DIMENSIONS are ', ecdf.dimensions))
print(('DIMS are ', dimx, dimy))
try:
  tst=ecdf.variables[dimx]
except:
  print('DIMS testing variables')
  try:
    tst=ecdf.variables['lon']
    dimx, dimy =( 'lon', 'lat')
  except:
    tst=ecdf.variables['longitude']
    dimx, dimy =( 'longitude', 'latitude')
ndim=len(tst.shape)
print(('DIMS3 are ', dimx, dimy, ndim))

var=opts.var    # 'SURF_MAXO3'
print('VAR ', var)
if( ndim == 1):
  lats=ecdf.variables[dimy][:]
  lons=ecdf.variables[dimx][:]
  eee=ecdf.variables[var]
  print("SHAPING ", eee.shape, ecdf.variables[var].shape, len(eee.shape))
  if len(eee.shape) == 2:
    vals=ecdf.variables[var][:,:]  
  else:
    ntim = -1
    if ( 'time' in ecdf.dimensions ) :
      ntim= len(ecdf.variables['time'])
    print("EEE ", ntim, eee.shape[0] )
    if ntim == 1:
      vals=ecdf.variables[var][0,:,:]  
    else:
      sys.exit('Not coded yet for time variable > 0')


#Svals=ecdf.variables[var][0,:,:]  

print("LONG LAT", dimx, dimy , ndim, lons[0], lats[0] ) # vals.max())
print("LONG LAT min max", dimx, dimy , ndim, vals.shape, vals.min(), vals.max())


#CCC#projps=ccrs.Stereographic(central_latitude=60.0,central_longitude=-32.0)
#CCC#projrot=ccrs.RotatedPole(pole_longitude=180+18,pole_latitude=39.25,globe=None)
#CCC#peter:
#CCC#projection_params='90.0 -32.0 0.933013'
#CCC#projrot=ccrs.RotatedPole(pole_longitude=90,pole_latitude=-32.0,globe=None)
#CCC#projrot=ccrs.RotatedPole(pole_latitude=39.25,central_rotated_longitude=-162.0,globe=None)
#CCC#projrot=ccrs.RotatedPole(pole_latitude=90.0,central_rotated_longitude=-162.0,globe=None)
#CCC proj=ccrs.Stereographic(central_latitude=60.0,central_longitude=0.0)
#CCC#proj=ccrs.RotatedPole(pole_latitude=39.25,pole_longitude=198.0,central_rotated_longitude=-162.0,globe=None)
proj=ccrs.PlateCarree()

#CCC#EnsClim
# & CORDEX RotPOle(198.0,39.25)  top-left corner Lon=331.79, Lat 21.67
#CRDX proj=ccrs.RotatedPole(pole_longitude=198,pole_latitude=39.25,globe=None)

#CCC#img_extent= (-30.0, 55.0, 30.0, 65.0 )
#CCC#ax = plt.axes(projection=proj,extent=img_extent)
print("EXTENT ", opts.extent)
img_extent=opts.extent.split(',')
img_bounds=list(map(float,img_extent))

# Following use of GridSpec taken from http://worksofscience.net/matplotlib/colorbar
# Also has examples for horizontal
#D7_5: fig1=plt.figure(figsize=[8,6])
fig1=plt.figure(figsize=[10,8])
#gs = GridSpec(100,100,bottom=0.18,left=0.18,right=0.88)
gs = GridSpec(100,100,bottom=0.05,left=0.05,right=0.88)

# ax for graph
ax1 = fig1.add_subplot(gs[:,0:85],projection=proj,extent=img_bounds)

# ax for colour bar 
#axC = fig1.add_subplot(gs[20:80,95:99])
#D7_5: axC = fig1.add_subplot(gs[20:90,95:99])
#STARTS FROM TOP!!!
cbar_dy= 20   # Pcnt 
axC = fig1.add_subplot(gs[50-cbar_dy:50+cbar_dy,92:95])
###################### GridSp

ax1.coastlines(resolution='10m') # 10, 50, 110
ax1.gridlines()
if opts.borders:
  ax1.add_feature(cfeature.BORDERS)  # odd looking: ,edgecolor='darkgray')

#----------- colors --------------------
if opts.levels is None:
  Nv=8
  cmap=plt.cm.get_cmap(opts.cmap,Nv)
  #NN colours=[ cmap(i/(1.0*Nv)) for i in range(Nv) ]
  #
  #M=plt.contourf(xi,yi,zT,cmap=cmap,extend='both')
  #CRDX hhh=plt.contourf(rlon,rlat,vals,cmap=cmap,extend='both') # Ens,transform=proj)
  hhh=ax1.contourf(lons,lats,vals,cmap=cmap,extend='both') # Ens,transform=proj)
else:
  bounds=opts.levels.split(',')
  print("levels:", opts.levels)
  print("BOUNDS:", bounds)
  v=list(map(float,bounds))
  Nv=len(v)+1
  print("MIN MAX ", Nv, v, vals.max(), vals.min(), "VVVVV ", v, Nv)

  #cmap=mpl.colors.ListedColormap(['r','g','w','b','c','k','m','k','r'])
  #cmap=mpl.colors.ListedColormap(['r','g','w','b','c','k','m','k'])
  # Using ideas from colorbar_only demo
  #bounds = [1, 2, 2.02, 4, 7, 8, 10]

  vv = [-999]+v+[999] # Needed extending for colorbar?
  Nv = len( v ) 
  Nv = len( v )  + 2 #CRDX
  print(" VV ", vv, Nv)

  cmap = plt.cm.get_cmap(opts.cmap, len(v) )
  #cmap = plt.cm.get_cmap("cool", len(v) )
  cmap.set_over('0.25')
  cmap.set_under('0.75')
  norm = mpl.colors.BoundaryNorm(v, cmap.N)
  print("LENGTH ", Nv, len(v), cmap.N)

  #TEST cmap=mpl.cm.get_cmap(opts.cmap,Nv+1)
  #TEST norm=mpl.colors.BoundaryNorm(v, cmap.N)
  #colours=[ cmap(i/(1.0*Nv)) for i in range(Nv) ]
  #CRDX hhh=plt.contourf(rlon,rlat,vals,v,cmap=cmap,norm=norm,boundaries=vv,extend='both')
  hhh=ax1.contourf(lons,lats,vals,v,cmap=cmap,norm=norm,boundaries=vv,extend='both')


if opts.skipcbar is None:
  print("Uses colorbar")
  #cbar=plt.colorbar(ticks=bounds,orientation='horizontal')
  if opts.levels is None:
     fig1.colorbar(hhh,ax=ax1,cax=axC)
  else:
     cbar=fig1.colorbar(hhh,ax=ax1,cax=axC,ticks=v)

#  else:
#      print "Skips colorbar"

if opts.title:
  print("TITLE", opts.title)
  print("EXTENT", opts.extent)
  #ax1.title(opts.title)
  #cf ax1 = fig1.add_subplot(gs[:,0:85],projection=proj,extent=img_bounds)
  #cf#img_extent= (-30.0, 55.0, 30.0, 65.0 )
  # in lat/long:
  #D7_5: ax1.text(12.5,70.0,opts.title,horizontalalignment='center')
  #TTT ax1.text(-14,74.0,opts.title,horizontalalignment='left',fontsize=18)
  #Oct2019 ax1.text(-14,85.0,opts.title,horizontalalignment='left',fontsize=18)
  xtitle= np.mean(img_bounds[0:2]) - 10
  ytitle= img_bounds[3]+5
  #ytitle= img_bounds[3]+12
  ax1.text(xtitle,ytitle,opts.title,horizontalalignment='left',fontsize=18)

#ERR? fig1.tight_layout(pad=0)

if ( opts.o == "Screen"):
  plt.show()
else:
  #plt.savefig('%s' % opts.o )
  plt.savefig('%s' % opts.o, bbox_inches='tight' )
  if ( opts.o[-3:] == "eps" ):  # produce png also, for geeqie
     mypng=opts.o.replace("eps","png")
     plt.savefig('%s' % mypng)
     #plt.savefig('%s' % mypng , bbox_inches='tight')

#CCC#box_top = 20.79  
#CCC#x, y = [-21.61, -21.61, 15.35, 15.35, -21.61], [-20.57, box_top, box_top, -20.57, -20.57] # RCA
#CCC#ax.plot(x,y,marker='o',transform=proj)



#CCC#ax = plt.axes(projection=ccrs.PlateCarree(),extent=img_extent)
#P3 plt.contourf(rlon,rlat,v) # Ens,transform=proj)
#CCC#plt.contourf(lons,lats,v)
#CRDXTMP plt.show()


