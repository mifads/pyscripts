#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import print_function
import numpy as np
from netCDF4 import Dataset
import mkCdf

#     EU15(15) = (/ "AT", "BE", "DK", "FI", "FR", "DE", "GR", "IE", "IT", &
#               "NL", "PT", "ES", "SE",  "GB", "LU" /),&
#     EU27(27) = (/ EU15,"HU", "PL", "CY", "CZ", "EE", "LT", "LV", "MT", &
#                        "SK", "SI", "BG", "RO" /),&
#     EU28(28) = (/ EU27, "HR" /),&
#     EUplus NO, CH


eu28 = ( 2, 3, 4, 6, 7,8, 9, 10, 60, 11, 12, 14, 15, 16, 17, 19, 20, 21, 22, 23, 27, 
         43, 44, 45, 46, 47, 48, 49,  55, 57 ) # DE is 9, 10, 60 for safety
eea  = ( 18, 24 )
eu28plus =  eu28  + eea

# 1 19.75 39.75 7.7804956 0.8401421 0.0 36.7195696 0.0 0.0000000 117.2765097 0.0 0.0866394 0.3376644 0.0
# ie cc lon lat emis..

def tst(x):
  return x+99.0

def EUmask(MapWanted=False,dbg=False):
  f=np.loadtxt('/global/work/mifads/cdf_emis/CdfGlobal/global05deg_cc_Feb2013/2005_v2/NOx_2005_ECLIPSEwithSHIP_05lonlat_cc_CH_v2.txt')
  
  cc=f[:,0]
  lon=f[:,1]
  lat=f[:,2]

  # Create output arrays in netcdf space
  mask=np.zeros([360,720],dtype=int)
  xlon=np.linspace(-179.75,179.75,720)
  xlat=np.linspace(-89.75,89.75,360)

  print('EUmask in lon lat ', len(lon), len(lat),  max(lon), max(lat))
  print('EUmask out lon lat ', len(xlon), len(xlat),  max(xlon), max(xlat))
  
  for i in range(len(cc)):
     icc = int( cc[i] + 0.1 )
     if eu28plus.count(icc) > 0:
       s= sum( f[i,3:-1] )
       if s > 0.0:
          #print icc, s
          jlat = int(  ( 90.0 + lat[i])/0.5 )
          ilon = int(  (180.0 + lon[i])/0.5 )
          #print i, jlat, ilon, lat[i], lon[i]
          #if( jlat > 360) :print i, jlat, ilon  # , lat[i], lon[i]
          if( dbg and icc==27 ) :print(icc, i, jlat, ilon, lat[i], lon[i])
          # Dingle bay is ca. 10.2W, Canary Islands ca. 15W
          if lon[i] > -12.0 : mask[jlat,ilon] = 1

  if MapWanted : mkCdf.createCDF('mask','TestEUmask.nc','i4',xlon,xlat,mask,dbg=True)

  return mask
  
if __name__ == '__main__':

  mask=EUmask(MapWanted=True,dbg=True)
