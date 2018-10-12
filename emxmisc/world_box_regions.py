#!/usr/bin/env python3
# Regions from MEGAN-MACC
# Plus some smaller regions from DS
# Oct 2018, from ~/Work/RESULTS/REGIONS/stallo_scripts/JPCtabs_nov2017/MaccBvocRegions.py
# but with 2 sea regions added from Stadtler et al N2O5 work.
# See Notes.MaccBvocRegions for comments on older modules
from collections import OrderedDict

def getMaccRegions():
   MaccRegions = OrderedDict()
   #                     lat0,  lat1,  lon0, lon1
   MaccRegions['NA']  = [  13.0,  75.0, -170, -40 ]
   #BUG MaccRegions['SA']  = [ -60.0,  13.0,  -90,  35 ]
   MaccRegions['SA']  = [ -60.0,  13.0,  -90,  -30 ]
   MaccRegions['EUR'] = [  37.0,  75.0,  -15,  50 ]
   MaccRegions['WEUR'] = [  40.0,  60.0,  -10,  20 ] # ds
   MaccRegions['NAF'] = [   0.0,  37.0,  -20,  65 ]
   MaccRegions['SAF'] = [ -35.0,   0.0,  -20,  55 ]
   MaccRegions['RUS'] = [  35.0,  75.0,   50, 179 ]
   MaccRegions['SEA'] = [ -10.0,  37.0,   65, 170 ]
   MaccRegions['AUS'] = [ -50.0, -10.0,  110, 179 ]
   MaccRegions['GLOB'] = [ -90.0, 90.0,  -180, 180 ] #ds
# Sea regions
   MaccRegions['ATL']  = [ 23.4,  60.0,  -60, -15 ]
   MaccRegions['NPAC'] = [  0.0,  60.0, -135, -180 ]

   return MaccRegions

