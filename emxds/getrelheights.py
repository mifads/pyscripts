#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import netCDF4 as cdf
import os
import sys
from great_circle import great_circle_distance


def LonLat2hRel(lon_s,lat_s,alt_s,label_s,mapdims,dbg=None):

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  # # # # # # # # # # # # # # # # # # #
# -Input: latlon-coordinates and altitude for stations
#
# -Get topography
# -Calculate the relative height for the stations
# -Output: Relative height and average
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

  if mapdims == 'ETOPO':
     xdim='x'; ydim='y'; zdim='z'
     # x from -180 to +180 ?? should be grid centres
     # y from -90 to +90 ??
     # 21601 (x) by 10801 (y) cells
  else:
     sys.exit('Need to specify ', mapdims )

  ## Importing the topographic data with each grid space 1x1 km (30sec)
  ## DIMS: lat = 2999 ; lon = 1940 ; alt (m) 

  home=os.getenv('HOME')
  topo_file='%s/Data/TOPO/ETOPO1/ETOPO1_Ice_g_gmt4.grd' % home

  he      =  np.zeros(len(alt_s))  # effective height
  avg_alt =  np.zeros(len(alt_s))  # Terrain height
  min_alt =  np.zeros(len(alt_s))  # Terrain height
  #ETOPO for region in 'central west eastern'.split():
  for region in 'ETOPO'.split():
     #d=cdf.Dataset('Europe_%s_topo_30sec.nc' % region,'r')
     d=cdf.Dataset(topo_file)
     alt= np.array( d.variables[zdim][:,:] )  #  [ jlat, ilon ]
     lon= np.array( d.variables[xdim] ) # CAREFUL. changed for ETOPO
     lat= np.array( d.variables[ydim] )
     idim=len(alt[0,:])
     jdim=len(alt[:,0])

     ##
     print( "Lat Lon Range ", region, min(lat), max(lat), min(lon), max(lon),
               idim, jdim, alt[jdim-1,idim-1], alt.dtype )

     dx = lon[10]-lon[9]
     dy = lat[10]-lat[9]
     for i in range(0,len(lat_s)):
       print('SITE ', lat_s[i], lon_s[i], alt_s[i], min(lat), max(lat), min(lon), max(lon) )
       if( min(lat) < lat_s[i] < max(lat) ):
         if( min(lon) < lon_s[i] < max(lon) ):

            ndx= int( 0.5 + (lon_s[i] - lon[0])/dx )
            ndy= int( 0.5 + (lat_s[i] - lat[0])/dy )
            # size of grid in m:
            dxm=great_circle_distance( [lat[ndy],lon[ndx]], [lat[ndy],lon[ndx+1]] )
            dym=great_circle_distance( [lat[ndy],lon[ndx]], [lat[ndy+1],lon[ndx]] )
            # No grids needed for 5km:
            nx5km = int( 0.5 + 5000.0/dxm )
            ny5km = int( 0.5 + 5000.0/dym )
            #
            print("Found ", label_s[i],  region, lat_s[i], lon_s[i],
               ndx, ndy, dxm, dym, nx5km, ny5km)
            dxm2=dxm*dxm; dym2=dym*dym; r5km2 = 5000.0*5000
            h_min  = 9999.0
            h_avg =  0.0
            nGood    =0
            nWarnings=0
            for ii in range( -nx5km, nx5km+1 ):
              for jj in range( -ny5km, ny5km+1 ):
                r2= ii*ii*dxm2 + jj*jj*dym2 
                if( r2 < r5km2 ):
                   #if dbg: print("HERE ", i,ii,jj, label_s[i], ndy+jj, ndx+ii, len(alt[:,0]), len(alt[0,:]))
                   iii = ndx+ii; jjj = ndy + jj
                   if( iii < idim and jjj < jdim ):
                     xalt=alt[jjj,iii]
                     if xalt > -0.0001:  # Exclude sea areas
                       nGood += 1
                       h_avg +=  xalt
                       h_min  = min( h_min , alt[jjj,iii] )
                     if dbg: print(":%4i%4i%7.2f%7.2f%5.1f%8.1f%5i%5i"%
                          ( ii, jj, lat[jjj], lon[iii], 0.001*np.sqrt(r2),
                           xalt, nGood, nWarnings ))
                   else:
                     #xalt=-888.0
                     nWarnings += 1
                     print("WARNING on edge?", iii, jjj, nGood, nWarnings)
     
            if( nWarnings < 0.1 * nGood ):
               he[i] = alt_s[i] - max( h_min , 0.0 ) # Sea would have given -500
               avg_alt[i] =  h_avg/nGood
            else:
               he[i]      = alt_s[i]   # Keep original height, since we have no better info.
               avg_alt[i] = np.nan     # but here we can marl what has happened
 
            print("End %s %5i %5i" % ( label_s[i], nGood, nWarnings ))
  
  return he, avg_alt

     

#AAA  # Rewrite all the coordinates to only degree and rewrite westerly coordinates with a minus sign
#AAA  #lat_s=[]
#AAA  #lon_s=[]
#AAA  #lon_data=np.zeros((np.size(latlon_data[:,1]),3),dtype=float) # Here the westerly lonitudedata will be saved
#AAA  #for s in range(0,np.size(latlon_data[:,1])):
#AAA    #if latlon_data[s,7]=='W':
#AAA      #lon_data[s,0]=-float(latlon_data[s,4])
#AAA      #lon_data[s,1]=-float(latlon_data[s,5])
#AAA      #lon_data[s,2]=-float(latlon_data[s,6])
#AAA    #elif latlon_data[s,7]=='E':
#AAA      #lon_data[s,0]=float(latlon_data[s,4])
#AAA      #lon_data[s,1]=float(latlon_data[s,5])
#AAA      #lon_data[s,2]=float(latlon_data[s,6])
#AAA    #la=float(latlon_data[s,0]) + float(latlon_data[s,1])/60 + float(latlon_data[s,2])/(60*60)
#AAA    #lat_s.append(la)
#AAA    #lo=lon_data[s,0]+ lon_data[s,1]/60 + lon_data[s,2]/(60*60)
#AAA    #lon_s.append(lo)
#AAA
#AAA  # Check if station lies within the boundary of the maps
#AAA  lat_sn=[]
#AAA  lon_sn=[]
#AAA  index_n=[]
#AAA  alt_sn=[]
#AAA  i_n=[]
#AAA  j_n=[]
#AAA  for ii in range(0,np.size(lat_s)):
#AAA    if min(lat)<lat_s[ii]<max(lat) and min(lon)<lon_s[ii]<max(lon):
#AAA      lat_sn.append(lat_s[ii])
#AAA      lon_sn.append(lon_s[ii])
#AAA      index_n.append(index[ii])
#AAA      alt_sn.append(alt_s[ii])
#AAA      #DS i_n.append(ij_coord[ii,0])
#AAA      #DS j_n.append(ij_coord[ii,1])
#AAA      i_n.append(i_coord[ii])
#AAA      j_n.append(j_coord[ii])
#AAA      print "DS here"
#AAA
#AAA  # Extracting indices for the stations (to be used when extracting their relative height from the map)
#AAA  lo_s=[]
#AAA  la_s=[]
#AAA  for m in range(0,np.size(lat_sn)):
#AAA    ab=abs(lat-lat_sn[m])
#AAA    la_s.append((ab==min(ab)).nonzero()[0][0])
#AAA  for n in range(0,np.size(lon_sn)):
#AAA    ab1=abs(lon-lon_sn[n])
#AAA    lo_s.append((ab1==min(ab1)).nonzero()[0][0])
#AAA
#AAA  # Getting the EMEP orography and the corresponding height for all the stations
#AAA  data_emep=sio.netcdf_file('meteo20090102_cf.nc','r')
#AAA  emep_height=data_emep.variables['orography']
#AAA  h_emep=emep_height[:] # An array with emep (j,i) coordinates (! reversed order og i,j) h_emep(time,j,i) time=1:8 seems to be the same value for all the times... take 1
#AAA
#AAA  # Extracting the EMEP height for the stations within the map, with the (i,j) coordinates
#AAA  he_s=[]
#AAA  for jj in range(0,np.size(i_n)):
#AAA    he_s.append(float(h_emep[1,j_n[jj],i_n[jj]]))
#AAA    print "DS herejj ", jj
#AAA    
#AAA  # LOOKS DANGEROUS.... should take these constants from .nc variables:
#AAA  he_s=2936.350661953+np.asarray(he_s)*0.0921258194197467 # Corrections from the netcdf-file
#AAA
#AAA  # Check if the stations are 'mountain stations' and extract only them to use for relative height
#AAA  he_sm=[]
#AAA  alt_snm=[]
#AAA  index_nm=[]
#AAA  i_nm=[]
#AAA  j_nm=[]
#AAA  la_sm=[]
#AAA  lo_sm=[]
#AAA  for kk in range(0,np.size(he_s)):
#AAA    print "DSkk ", kk, alt_sn[kk], he_s[kk]
#AAA    if alt_sn[kk]>he_s[kk]:
#AAA      he_sm.append(he_s[kk])
#AAA      alt_snm.append(alt_sn[kk])
#AAA      index_nm.append(index_n[kk])
#AAA      i_nm.append(i_n[kk])
#AAA      j_nm.append(j_n[kk])
#AAA      la_sm.append(la_s[kk])
#AAA      lo_sm.append(lo_s[kk])
#AAA  he_sm=np.asarray(he_sm)       # The EMEP heigh for the mountain stations in the map
#AAA  alt_snm=np.asarray(alt_snm)   # The absolute height for the mountain stations in the map
#AAA  index_nm=np.asarray(index_nm) # The index for the mountain stations in the map
#AAA  i_nm=np.asarray(i_nm)         # The i coordinate for the mountain stations in the map
#AAA  j_nm=np.asarray(j_nm)         # The j coordinate for the mountain stations in the map
#AAA  ij_nm=np.hstack((i_nm,j_nm))  # The (i,j) coordinates for the mountain stations in the map
#AAA  la_sm=np.asarray(la_sm)       # The latitude coordinates for the mountain stations in the map
#AAA  lo_sm=np.asarray(lo_sm)       # The longitude coordinates for the mountain stations in the map
#AAA
#AAA  # Relative height calculations (here with 5 km radius)
#AAA  hr=[]
#AAA  h5=[]
#AAA  for jj in range(0,np.size(alt_snm)): # Same range as la_sm and lo_sm
#AAA    h5=alt[(la_sm[jj]-2):(la_sm[jj]+3),(lo_sm[jj]-2):(lo_sm[jj]+3)] # Remember until! Therefore 3...
#AAA    hr.append(alt_snm[jj]-h5.min())
#AAA  hr=np.asarray(hr)
#AAA
#AAA  print "DS RES", hr, he_sm,alt_snm, index_nm
#AAA  return hr, he_sm,alt_snm, index_nm
#AAA
#AAA# Marcus:
#AAA#            Neunkirch Novaggio Laegeren  Davis
#AAAsite_lat = [ 47.690, 46.024, 47.478, 46.815 ]
#AAAsite_lon = [ 8.5264, 8.8353, 8.3644, 9.8561 ]
#AAAindex    = [   1, 2, 3, 4]
#AAAalt_s = [ 511.0, 1105.0, 736.0, 1687.0 ]
#AAA#ij_coord = [ [ 68, 71, 68, 40 ], [71, 40] ]
#AAAi_coord = [ 68,71,68, 71 ]
#AAAj_coord = [ 40, 37,40, 40 ]
#AAA
#AAAheights(site_lat,site_lon,i_coord,j_coord,index,alt_s)


if ( __name__ == "__main__" ):
  """ Testing LonLat2hRel(lon_s,lat_s,alt_s,label_s,mapdims,dbg=None)
  """
  import sys

  site_lat = [ 89.5, 47.690, 46.024, 47.478, 46.815, -89.5 ]
  site_lon = [ -179.5, 8.5264, 8.8353, 8.3644, 9.8561, -179.5 ]
  site_alt = [ 50.0, 511.0, 1105.0, 736.0, 1687.0, 100.0 ]
  sites    = 'FakeNW Neunkirch Novaggio Laegeren  Davis FakeSW'.split()
  #alt_h5, alt_avg =  heights(site_lat,site_lon,site_alt,sites,mapdims='ETOPO')
  #for i in range(0,len(sites)):
  #  print( i, site_lat[i], site_lon[i], site_alt[i], alt_h5[i], alt_avg[i] )

  #xlat=30.67;xlon=76.73;xalt=310.0;xname='Mohali'
  #alt_h5, alt_avg =  heights( [xlat], [xlon],[xalt],[xname],mapdims='ETOPO')
  #print(alt_h5)

  #print(sys.args)
#  if sys.argv[1]==None:
  xlat=30.08;xlon=31.28;xalt=35.0;xname='Cairo'
  if sys.argv[1] == '--xyz':
    xlon, xlat, xalt = map( float,  sys.argv[2].split())
    xname='User'
  alt_h5, alt_avg =  LonLat2hRel( [xlon], [xlat],[xalt],[xname],mapdims='ETOPO',dbg=True)
  print( 'hRel(5km) = ', alt_h5[0], ' Avg terrain: ', alt_avg[0])



