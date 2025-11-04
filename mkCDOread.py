#!/usr/bin/env python3
""" USE MODCDO on nebula """
import argparse
import subprocess as sub
import sys

tipsfrom="""
 https://code.mpimet.mpg.de/boards/1/topics/4461
 https://stackoverflow.com/questions/59846765/regridding-operations-on-smaller-subsets:q
 https://www.youtube.com/watch?v=YdFo8YAbLTw
"""


def getcdovals(ifile,lon,lat,var='SURF_MAXO3',ofile='output.txt',star5=False):
  cmd='ls -lt %s' % ifile
  tmpfile='tmptmpout.nc'
  cmd='cdo -selvar,%s %s %s' % ( var, ifile, tmpfile )
  print(f'TRY: {cmd}')
  try:
    sub.run(cmd,shell=True,check=True)
  except:
    print('FAILED:', cmd)
    print('DID you do module load cdo')
  
  #FAILS sub.run(cmd.split(),shell=True,check=True)
  if star5:
    nstar=0
    for dlat in [ -0.5, 0, 0.5 ]:
      xlat = lat + dlat
      for dlon in [ -0.5, 0, 0.5 ]:
        xlon = lon + dlon
        cmd='cdo -outputtab,value -remapbil,lon=%f/lat=%f %s > %s%02d' % ( lon, lat, tmpfile, ofile, nstar)
        print("CMDstar ", nstar, cmd)
        sub.run(cmd,shell=True,check=True)
        nstar += 1 
  else:
    cmd='cdo -outputtab,value -remapbil,lon=%f/lat=%f %s > %s' % ( lon, lat, tmpfile, ofile)
    print("CMD2: ", cmd)
    sub.run(cmd,shell=True,check=True)


  
if __name__ == '__main__':

  print('SYS', sys.argv)
  if sys.argv[1] == 'demo':
     print('SYS', sys.argv)
     lat=58.389; lon=8.252
     ifile='/ec/res4/hpcperm/fawc/Output_EMEP/RI-Urbans/Floris_2014/Base_month.nc'
     getcdovals(ifile,lon,lat,var='SURF_ppb_NO2',ofile='outdemo.txt')

  else:
#------------------ arguments  ----------------------------------------------

    #parser=argparse.ArgumentParser(usage=__doc__) also works, but text at start
    parser=argparse.ArgumentParser(epilog=__doc__,
     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i','--ifile',help='ifile',required=True)
    parser.add_argument('-o','--ofile',help='ofile',required=True)
    parser.add_argument('-v','--var',help='var',required=True)
    parser.add_argument('--lonlat',nargs=2,required=True)
    parser.add_argument('-s','--star5',help='star5',action='store_true')

    args=parser.parse_args()
    print(args)
  
    lon=float(args.lonlat[0])
    lat=float(args.lonlat[1])
    getcdovals(args.ifile, lon, lat, args.var, args.ofile,star5=args.star5)

#
##cdo -selvar,SURF_ppb_O3 -outputtab,value -remapbil,lon=23.816/lat=37.995 $ifile  > testing.O3
##cdo  -outputtab,value -remapbil,lon=23.816/lat=37.995 $ifile  > testing.O3
#
#res=0302c
#grid=EMEP$res
#res=01
#grid=CAMS01
#run=rv5_1pmfDS_EEv5pmf  
#idir=/ec/res4/hpcperm/fads/2024TESTS/$grid/
#period=hourInst
#
#for year in 2019 #  2019
#do
#  odir1=/ec/res4/scratch/fads/PMF_Feb16/$grid/$run.$year/
#  odir2=/home/fads/PMF_Feb16/$grid/$run.$year/
#  ifile="$idir$run.$year/Base_$period.nc"
#  mkdir -p $odir1
#  mkdir -p $odir2
#  echo $ifile
#  
#  cd $odir1
##  ls -lt $ifile
##  exit
#  
#for v in ug_SEASALT_F # ug_remPPM_f ug_FFIRE_REMPPM25 ppb_O3 ppb_NO2 ug_SO4 ug_NO3_F ug_NH4_F ug_SEASALT_F ug_DUST_WB_F  ug_PM25 ug_PM10 ug_BBPOA_f ug_AGPOA_f ug_POA_f_rem ug_PM_OM25 ug_PM_ASOA ug_PM_BSOA ug_FFIRE_OM ug_POA_f_Cb ug_POA_f_Cf ug_RTPOA ug_ECFINE ug_FFIRE_BC
#  do
#    var="SURF_$v"
#    echo $grid $year $grid $v
#
##0302done cdo -selvar,$var $ifile selvar$var.nc
#  
#  # from rdSites.py
#    echo  starts....
#   cdo   -outputtab,value -remapbil,lon=23.816/lat=37.995 selvar$var.nc > $odir2/emep$res_${var}_id01.txt
#   exit
#
#   cdo   -outputtab,value -remapbil,lon=23.700/lat=37.980 selvar$var.nc > $odir2/emep$res_${var}_id02.txt
#   cdo   -outputtab,value -remapbil,lon=2.118/lat=41.388 selvar$var.nc > $odir2/emep$res_${var}_id03.txt
#   cdo   -outputtab,value -remapbil,lon=8.250/lat=58.383 selvar$var.nc > $odir2/emep$res_${var}_id04.txt
#   cdo   -outputtab,value -remapbil,lon=26.029/lat=44.348 selvar$var.nc > $odir2/emep$res_${var}_id05.txt
#   cdo   -outputtab,value -remapbil,lon=-6.340/lat=52.190 selvar$var.nc > $odir2/emep$res_${var}_id06.txt
#   cdo   -outputtab,value -remapbil,lon=-6.224/lat=53.308 selvar$var.nc > $odir2/emep$res_${var}_id07.txt
#   cdo   -outputtab,value -remapbil,lon=24.952/lat=60.196 selvar$var.nc > $odir2/emep$res_${var}_id08.txt
#   cdo   -outputtab,value -remapbil,lon=11.010/lat=47.801 selvar$var.nc > $odir2/emep$res_${var}_id09.txt
#   cdo   -outputtab,value -remapbil,lon=24.283/lat=61.850 selvar$var.nc > $odir2/emep$res_${var}_id10.txt
#   cdo   -outputtab,value -remapbil,lon=15.120/lat=49.600 selvar$var.nc > $odir2/emep$res_${var}_id11.txt
#   cdo   -outputtab,value -remapbil,lon=19.917/lat=50.067 selvar$var.nc > $odir2/emep$res_${var}_id12.txt
#   cdo   -outputtab,value -remapbil,lon=3.140/lat=50.611 selvar$var.nc > $odir2/emep$res_${var}_id13.txt
#   cdo   -outputtab,value -remapbil,lon=-0.150/lat=51.520 selvar$var.nc > $odir2/emep$res_${var}_id14.txt
#   cdo   -outputtab,value -remapbil,lon=-0.200/lat=51.500 selvar$var.nc > $odir2/emep$res_${var}_id15.txt
#   cdo   -outputtab,value -remapbil,lon=5.395/lat=43.305 selvar$var.nc > $odir2/emep$res_${var}_id16.txt
#   cdo   -outputtab,value -remapbil,lon=13.550/lat=51.900 selvar$var.nc > $odir2/emep$res_${var}_id17.txt
#   cdo   -outputtab,value -remapbil,lon=33.381/lat=35.141 selvar$var.nc > $odir2/emep$res_${var}_id18.txt
#   cdo   -outputtab,value -remapbil,lon=2.150/lat=48.710 selvar$var.nc > $odir2/emep$res_${var}_id19.txt
#   cdo   -outputtab,value -remapbil,lon=26.735/lat=58.371 selvar$var.nc > $odir2/emep$res_${var}_id20.txt
#   cdo   -outputtab,value -remapbil,lon=8.530/lat=47.378 selvar$var.nc > $odir2/emep$res_${var}_id21.txt
#  
#  # rm input.nc
#  done # year
#done
#  
#  
#  # nn = nearest neighbour
#  # bil = bilin
#  # cdo showdate
#  
#  # statement about 1x1 means point!
#  
