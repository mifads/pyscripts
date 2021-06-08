#!/usr/bin/env python3
# TD is Chad, VE Vene, SD is ca 30E, NE is Niger 
import emxgeo.rdGoogleCentroids as mc
dbgCodes = 'VE BR US FR FI TD NE Sahel'.split()

future="""
jdbg=237;idbg=140  # see mkBugFixComp. Old had -1.08013, new had 3.62423
                   # in western USA
idbg=(180+15)*2; jdbg=(90+14)*2 # Sahel is 0-30E, 10-18N, dbg 15, 14
jdbg=220;idbg=518  # Pulsing
idbg=365; jdbg=274 # France, GLOBAL05
jdbg=160;idbg=234  # Amazon, SH, with 25% rainforest
idbg=350; jdbg=260 # Spain, GLOBAL05
if domain == 'GLOBAL':
   idbg //= 2; jdbg //= 2 # France
"""

def getCountryCodes(cc,lat0=-90.,lon0=-180.,dlat=0.5,dlon=0.5,dbg=False):
  """ CRUDE - just fixed lat0, lon0 now for CAMS"""

  geocc = dict()
  if cc=='Sahel':
    geocc['i'] = 390
    geocc['j'] = 208
    geocc['land'] =  'Sahel'

  else:

    geo=mc.getGoogleCentroids(cc)
    if dbg: print('mkCountryDebg:cc=:',cc,' geo:', geo)

    geocc['j'] = int(( geo['lat']-lat0 )/dlat)
    geocc['i'] = int(( geo['lon']-lon0 )/dlon)
    geocc['lat'] = geo['lat']
    geocc['lon'] = geo['lon']
    geocc['land'] = geo['country']
  return geocc

def getCountryIJ(cc):
    geo=getCountryCodes(cc)
    return geo['i'], geo['j']

if __name__ == '__main__':

  for cc in dbgCodes:
    geo=getCountryCodes(cc)
    print(cc, geo)
    print( getCountryIJ(cc) )
    #i,j = getCountryIJ(cc)
