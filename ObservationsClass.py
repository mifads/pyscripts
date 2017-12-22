#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  ObservationsClass - to  gets site codes and coordinates from NILU list
   ObsStations - class to hold info on NILU/EMEP/GAW type stations
   printObs - prints summary table
"""
import StringFunctions as str   # pyscripts

# We will often print tables, but will need to adapt field widths for differnt
# cases. We try a flexible system:
hdrfmt= '%8s  %-30s %20s %3s %3s %6s %8s %8s %8s %5s %5s %6s'
numfmt= '%s  %-30s %20s %3s %3s %6.2f %8.3f %8.3f %8.2f %5.1f, %5.1f %6.1f'

tabterms = tuple( 'code name country cont cat   dc  di24 degN degE alt hRel obsHt tz'.split() )
tabwidth =      [     8, -30,     20,   4,  8,  4,     6,    8,   8,  8,   6,    5,  6 ]
tabhfmt  =           's    s       s    s   s   s      s     s    s   s    s     s   s'.split()
tabnfmt  =           's    s       s    s   s .0f    .2f   .3f  .3f  .0f .0f   .1f .1f'.split()
tabwdth= dict( zip( tabterms, tabwidth ) ) # List needed to keep python2-type dicts
tabhdrs= dict( zip( tabterms, tabhfmt ) )
tabnums= dict( zip( tabterms, tabnfmt ) )


def tabstring(terms,vals=None,Hdr=False):
   typefmt=tabnums.copy()
   if Hdr: typefmt=tabhdrs.copy()
   #for k in terms:
   #  print('TABterms',k, tabwdth[k], typefmt[k] )
   #  print('%%%d%s' % ( tabwdth[k] , typefmt[k] ) )
   stxt = ''.join([ ' %%%d%s' % ( tabwdth[k] , typefmt[k] ) for k in terms ])
   #print('STXT', stxt)
   if Hdr:
     stxt = stxt % tuple( terms )
   elif vals:
     stxt = stxt % tuple( vals )
   return stxt

class ObsStations(object):
  """
    Class to hold info on NILU/EMEP/GAW type stations
  """
  def __init__(self,name=None,code=None,scode=None,continent=None,degN=0.0,degE=0.0,alt=0.0,\
       hRel=0.0, samplerHt=3.0,country=None,category=None,dc=0.0,DayNightIndex=0.0,tz=0.0):
    #self.name=  str.blankRemove(name)
    self.name=  name
    self.code=code             #  e.g. AT0002R
    self.scode=scode           #  e.g. AT02
    self.cont=continent   # from GeoNames, e.g. EU, NA
    self.degN = degN
    self.degE = degE
    self.alt  = alt            # altitude, m
    self.hRel  = hRel          # relative altitude, m, within 5 km
    self.obsHt = samplerHt     # height of sample, m
    self.country  = country 
    self.cat  = category 
    self.dc  = dc              # Data capture, % 
    self.di24  = DayNightIndex
    self.tz  = tz              # time relative to GMT

    if self.name:
       self.name=  str.blankRemove(name)

    #hdrfmt= '%8s  %-30s %20s %3s %3s %6s %8s %8s %8s %5s %5s %6s'
    #numfmt= '%s  %-30s %20s %3s %3s %6.2f %8.3f %8.3f %8.2f %5.1f, %5.1f %6.1f'
    #    ( code, name, country, cont, cat, di24, degN, degE, alt, hRel, obsHt, tz)

  def keyslist(self):
    """ Returns the items in the order that a Table might want """
    return 'code name country cont cat di24 degN  degE alt hRel obsHt tz'.split()

  def keyfmts(self):
    """ Returns the default format in the order that a Table might want """
    hdrfmt= '%8s  %-30s %20s %3s %3s %6s %8s %8s %8s %5s %5s %6s'
    numfmt= '%s  %-30s %20s %3s %3s %6.2f %8.3f %8.3f %8.1f %5.1f, %5.1f %6.1f'
    return hdrfmt, numfmt

  def printObs(self,txt='',dbg=False):
     """ function to print main contents of EMEP ozone site data class """
     outHdr = txt+'%8s  %-30s %20s %3s %3s %6s %8s %8s %8s %5s %5s %6s' % \
        tuple( 'code name country cont cat di24 degN  degE alt hRel obsHt tz'.split())
     if dbg:
       print(outHdr)
     #print("DEBUG ", self.code, self.name, self.country, self.cont, self.cat,\
     #     self.di24, self.degN, self.degE, self.alt, self.hRel, self.obsHt, self.tz )
     print(txt+'%s  %-30s %20s %3s %3s %6.2f %8.3f %8.3f %8.2f %5.1f, %5.1f %6.1f' % 
        ( self.code, self.name, self.country, self.cont, self.cat,\
          self.di24, self.degN, self.degE, self.alt, self.hRel, self.obsHt, self.tz) )

  def printStr(self,txt='',dbg=False,ccodes=None):
     """ function to print main contents of EMEP ozone site data class to a string """

     fmt='%8s  %-24s %20s %3s %3s %7s %8s %8s %8s %7s %5s %6s'
     outHdr = fmt % tuple( 'code name country cont cat di24 degN  degE alt hRel obsHt tz'.split())
     if ccodes:
        fmt='%8s  %-24s %4s %3s %3s %7s %8s %8s %8s %7s %5s %6s' # 'AT' instead of Austria
     outHdr = txt+ fmt % \
        tuple( 'code name country cont cat di24 degN  degE alt hRel obsHt tz'.split())

     if dbg:
       print(outHdr)
     fmt= '%s  %-24s %20s %3s %3s %7.3f %8.3f %8.3f %8.2f %7.1f, %5.1f %6.1f'
     if ccodes: fmt= '%s  %-24s %4s %3s %3s %7.3f %8.3f %8.3f %8.2f %7.1f, %5.1f %6.1f'
     outStr= (txt+fmt % \
        ( self.code, self.name, self.country, self.cont, self.cat,\
          self.di24, self.degN, self.degE, self.alt, self.hRel, self.obsHt, self.tz) )
     return outStr, outHdr

def sortObsDB(db):
  #def sortObs(self,field=None):
     """ function to sort data base of observations by some 
        field.
        From: http://stackoverflow.com/questions/16412563/python-
           sorting-dictionary-of-dictionaries
     """
     #self.field = field   # e.g. 'degN', 'Country'

     #slist=sorted(self.items(), key=lambda x: x[1][field],reverse=True)
     field='degN'
     #slist=sorted(db.items(), key=lambda x: x[1][field],reverse=True)
     # CHECK RdPickle ... works there!

     #for s in range(0,len(slist)):
     #  code= slist[s][0]
     #  lat = self[code]['degN']
     #  print('TEST SORT ', code, lat )


if __name__ == '__main__':
   """ Just testing the system """

   stations  = 'Mace_Head xxx yyy'.split()
   stations[0] = 'Mace Head' 
   stations[2] = 'Ähtäri'
   codes = 'IE0031R IT0004R SI0033R TESTER'.split()
   continents = 'EUR EUR EUR AN'.split()
   cat   = 'Global Global Regional Contributing'.split()
   degn  = [ 55.0,   45.0,   35.0 ]
   dege  = [ 15.0,  -45.0,  175.0 ]
   n=0
   sites=[]
   db = {}

   for s in stations:
       obs = ObsStations( s, codes[n], degN=degn[n], degE=dege[n], 
               category=cat[n] )
       sites.append(obs)
       ObsStations.printObs(obs)
       if  'Mace' in s: obs.cont = 'NEW'
       ObsStations.printObs(obs)
       db[obs.code] = obs
       tt, hh= obs.printStr()
       print("TT ", tt, "HH ", hh)
       tt, hh= obs.printStr(ccodes=True)
       print("CC ", tt)
       n += 1

   print('Testing  string formats')
   print( tabstring( ['hRel',] ) )
   obsvals = vars(obs)
   vals = [ obsvals[k] for k in tabterms ] 
   print( tabstring( tabterms ) )
   print( "TERMS ", tabterms )
   print( "VALS  ", vals  )
   print( tabstring( tabterms , vals ) )
   tabwdth['country'] = 7
   print( tabstring( tabterms , Hdr=True ) )
   print( tabstring( tabterms , vals ) )
     
   #print('DB ', db)
   s=sortObsDB(db)
   #s=ObsStations.sortObs(db,'degN')
   #ObsCodes, ObsList = ReadOzoneSites()
   #print  "NOBS ", nobs[1].name
   #for s in stats:
   #  try:
   #    n= ObsCodes.index(s)
   #    print("TEST for %s " % s, n, printObs(n))
   #  except:
   #    print("TEST for %s ", s, " not in list")
