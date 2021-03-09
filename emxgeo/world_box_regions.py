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
   MaccRegions['Sahel'] = [  0.0,  30.0,   10,  18 ] # Hudman defs
   MaccRegions['SAF'] = [ -35.0,   0.0,  -20,  55 ]
   MaccRegions['RUS'] = [  35.0,  75.0,   50, 179 ]
   MaccRegions['SEA'] = [ -10.0,  37.0,   65, 170 ]
   MaccRegions['AUS'] = [ -50.0, -10.0,  110, 179 ]
   MaccRegions['GLOB'] = [ -90.0, 90.0,  -180, 180 ] #ds
# Sea regions
   MaccRegions['ATL']  = [ 23.4,  60.0,  -60, -15 ]
   MaccRegions['NPAC'] = [  0.0,  60.0, -135, -180 ]

   return MaccRegions


def getNamedMaccRegions(): # Added names
   MaccRegions = OrderedDict()
   #                     lat0,  lat1,  lon0, lon1  name
   MaccRegions['NA']  = [  13.0,  75.0, -170, -40, 'North America' ]
   #BUG MaccRegions['SA']  = [ -60.0,  13.0,  -90,  35 ]
   MaccRegions['SA']  = [ -60.0,  13.0,  -90,  -30, 'South America' ]
   MaccRegions['EUR'] = [  37.0,  75.0,  -15,  50 , 'Europe' ]
   MaccRegions['WEUR'] = [  40.0,  60.0,  -10,  20, 'W.Europe'  ] # ds
   MaccRegions['NAF'] = [   0.0,  37.0,  -20,  65, 'North Africa' ]
   MaccRegions['Sahel'] = [  0.0,  30.0,   10,  18, 'Sahel' ] # Hudman defs
   MaccRegions['SAF'] = [ -35.0,   0.0,  -20,  55, 'southern Africa' ]
   MaccRegions['RUS'] = [  35.0,  75.0,   50, 179, 'Russia' ]
   MaccRegions['SEA'] = [ -10.0,  37.0,   65, 170, 'South East Asia' ]
   MaccRegions['AUS'] = [ -50.0, -10.0,  110, 179, 'Australia' ]
   MaccRegions['GLOB'] = [ -90.0, 90.0,  -180, 180, 'Global' ] #ds
# Sea regions
#   MaccRegions['ATL']  = [ 23.4,  60.0,  -60, -15 ]
#   MaccRegions['NPAC'] = [  0.0,  60.0, -135, -180 ]

   return MaccRegions

def ns(y):
    """ converts -ve lat to degS. Use degN notation for easier latex 
    editing later
    """
    if y > 0: deg = '%ddegN' % int(y)
    else:     deg = '%ddegS' % int(-y)
    return deg
def ew(x):
    if x > 0: deg = '%ddegE' % int(x)
    else:     deg = '%ddegW' % int(-x)
    return deg

def print_regions():
  r=getNamedMaccRegions()
  for reg in r.keys():
    c=r[reg]
    print('%s:%s,%s - %s,%s - %s' % ( reg, c[-1], ns(c[0]),ns(c[1]), ew(c[2]), ew(c[3]) ))
    
if __name__ == '__main__':
  print_regions()
