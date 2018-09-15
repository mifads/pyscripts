#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect  # just to get name of this code 
import numpy as np
import os
import re
import sys
from emxmisc import stringfunctions   # pyscripts

niluFile='NiluFeb2016.txt'
niluFile='EMEP_ozone_sites_Feb2016.txt'
niluFile="../DATA_O3/stations_ozone_Feb2016.html"  # encoding problems for DE0042R Öhringen
niluFile="../DATA_O3/stations_ozone_Feb2016.txt"
niluFile="../DATA_O3/stations_ozone_Sep2018.txt" # Added FI08

class NiluStations(object):
  """ Class to hold info on NIKU/EMEP stations
  """
  def __init__(self,name=None,code=None,scode=None,degN=0.0,degE=0.0,alt=0.0):
    self.name=name
    self.code=code                # eg NO0001R
    self.scode=scode              # eg NO01
    self.degN = degN
    self.degE = degE
    self.alt  = alt

def fmtObs(n):
   """ function to print main contents of EMEP ozone site data class """
   p=ObsList[n]
   return '%-6s %-10s %-30s %10.4f %10.4f %9.2f' % (p.scode, p.code, p.name, p.degN, p.degE, p.alt)

def headerObs():
   """ function to print main contents of EMEP ozone site data class """
   return '%-6s %-10s %-30s %10s %10s %9s' % ('scode', 'code', 'name', 'degN', 'degE', 'alt')


def printObs(n):
   """ function to print main contents of EMEP ozone site data class """
   p=ObsList[n]
   print('%-6s %-10s %-30s  %8.4f %8.4f %7.2f' % (p.scode, p.code, p.name, p.degN, p.degE, p.alt) )

def ReadOzoneSites():
  """ Function to read ozone site details from NILU ascii (utfXX?) file and
   store data as an array of NiluStations class objects
   The arrays ObsCodes provides a list of site-codes (e.g. AT00033R) which can
   be used to access the objects (stored in ObsList).
  """
   
  ObsCodes=[]
  ObsList=[]
  for line in open(niluFile,'r'):
    #AM0001R Amberd           40 deg 23'04"N 044 deg 15'38"E 2080.0m
        
      #           code  name                     57   deg     35'     56"N    11  deg    00'    36"  E   1465m
      #r=re.match('(\w*) (\w+\-*.*\s*\w*\w*).*\s+(\d+) deg (\d\d)\'.(\d+)\"N (\d+) deg (\d+)\'(\d+)\"(.)\s+(\d+).*',line)
      r=re.match('(\w*) (\w+\-*.*\s*\w*\w*).*\s+(\d+)°(\d\d)\'.(\d+)\"N (\d+)°(\d+)\'(\d+)\"(.)\s+(\d+).*',line)

      if r:
        #print r.groups()
        code=r.groups()[0]
        scode=code[:2]+code[4:6]
        xname=line[8:45] # easier for multi-part names
        name= stringfunctions.stringClean(xname.strip())
    
        degN= np.float(r.groups()[2])
        minN= np.float(r.groups()[3])
        secN= np.float(r.groups()[4])
        degE= np.float(r.groups()[5])
        minE= np.float(r.groups()[6])
        secE= np.float(r.groups()[7])
        EastWest= r.groups()[8]
        alt = np.float(r.groups()[9])
        
        degE=degE+minE/60.0+secE/3600.0
        if EastWest == 'W' :
           degE = -degE
        obs=NiluStations(name,code,scode,
          degN=degN+minN/60.0+secN/3600.0,
          degE=degE+minE/60.0+secE/3600.0,
          alt=alt)
        ObsList.append(obs)
        ObsCodes.append(code)
    
      #fi=re.match('(DE0042\w+).*',line)
      fi=re.match('(NO00\w+).*',line)
      if fi:
         #print("DEBUG ", line)
         #print("DEBUG code ", fi.groups())
         xcode=fi.groups()[0]
         #print("DEBUG xcode ", xcode, type(xcode))
         #ncode=xcode.decode('cp1252')
         #print("DEBUG xcode ", xcode)
         dbg=re.match('(\w+) ',line)
         #print("DEBUG AA ", name, dbg.groups())
         dbg=re.match('(\w+) (\w+\-*.*\s*\w*\w*).*\s+(\d+)°(\d\d)\'.(\d+)\"N (\d+)°(\d+)\'(\d+)\"(.)\s+(\d+).*',line)
         #print "DEBUG BB ", dbg.groups()

         #xline=line.decode('cp1252')
        # nline=xline.encode('utf-8')
        # print "DEBUG NN ", nline
        # dbg=re.match('(\w+) (\w+\-*.*\s*\w*\w*).*\s+(\d+)°(\d\d)\'.(\d+)\"N (\d+)°(\d+)\'(\d+)\"(.)\s+(\d+).*',nline)
        # print "DEBUG CC ", dbg.groups()
       # Tested another approach
        #fields = line.split()
        #ndeg = fields.index('deg')
        #name = ' '.join( fields[1:ndeg-1])  # NB needs 1:2 to get fortran 1:1
        #print " F", ndeg-2, fields[0], fields[1], fields[ndeg-2], '=>', name, stringfunctions.stringClean(name)

  return ObsCodes, ObsList

if __name__ == '__main__':
   ObsCodes, ObsList = ReadOzoneSites()
   #print  "NOBS ", nobs[1].name
   #niluFile="../DATA_O3/stations_ozone_Sep2018.txt" # Added FI08

   # Example for a few sites
   stats = 'IE0031R IT0004R SI0033R TESTER'.split()
   print('Example for:', stats)
   for s in stats:
      if s in ObsCodes:
        n= ObsCodes.index(s)
        printObs(n)

   #outfile= 'Tabulated_' + os.path.basename(niluFile)
   outfile= 'Tabulated_nilu_ozone_stations.txt'
   with open(outfile,'w') as f:
     f.write('# Tabulated from '+niluFile+ ' using ' + sys.argv[0] + '\n')
     f.write(headerObs()+'\n')
     for s in  ObsCodes:
        n= ObsCodes.index(s)
        f.write(fmtObs(n)+'\n')

   print('ARGS', sys.argv[0])
   #def f():
   #  caller = inspect.currentframe().f_back
   #  print('# called from ',caller.f.globals['__name__'])
   #f()

