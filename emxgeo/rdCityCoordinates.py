#!/usr/bin/env python3
import numpy as np
import sys

"""
#https://www.infoplease.com/world/geography/major-cities-latitude-longitude-and-corresponding-time-zones
Aberdeen, Scotland	57	9 N	2	9 W	5:00 p.m.
Adelaide, Australia	34	55 S	138	36 E	2:30 a.m.1
Algiers, Algeria	36	50 N	3	0 E	6:00 p.m.
"""

def getCityCoords(city=None,country=None):

  city=dict()
  with open('cities.txt','r') as f:
   for line in f:
    if line.startswith('#'): continue
    fields = line.split('\t')
    city, land = fields[0].split(',')
    minN, sign  = fields[2].split()
    degN = int(fields[1]) + int(minN)/60.0
    if sign == 'S': degN = -degN

    minE, sign  = fields[4].split()
    degE = int(fields[3]) + int(minE)/60.0
    if sign == 'W': degE = -degE
    print(city, land, degN, degE)
  #sys.exit()
