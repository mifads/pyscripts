#!/usr/bin/env python
# ONLY WORKS WITH PYTHON2 - something failed with python3 json with urlopen 

from urllib2 import urlopen    # for getplace
#DSfrom urllib3 import urlopen    # for getplace
import json                    # for getplace
import urllib, codecs          # for geonames

def getplace(lon, lat):
    """
     Convert lon, lat to country
     DS - adapted from http://stackoverflow.com/questions/20169467/how-to-convert-from-longitude-and-latitude-to-country-or-city
    """
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false" % (lat, lon)
    v = urlopen(url).read()
    j = json.loads(v)
    try:
      components = j['results'][0]['address_components']
    except: 
      return '-'

      #components = { 'types': {'country':'-', 'town':'-'}} 
    country = town = None
    for c in components:
        #print('CTYPES ', c)
        #print('CTYPES ', c['types'])
        if "country" in c['types']:
            country = c['long_name']
        if "postal_town" in c['types']:
            town = c['long_name']
    return country   #, town, continent


#------------------------------------------------------------
"""
Retrieve a list of information about countries, pulled from GeoNames.
DS adapted from: from https://www.djangosnippets.org/snippets/1049/

Example entry:

 {u'Area(in sq km)': u'33843',
  u'Capital': u'Chi\u015fin\u0103u',
  u'Continent': u'EU',
  u'Country': u'Moldova',
  u'CurrencyCode': u'MDL',
  u'CurrencyName': u'Leu',
  u'EquivalentFipsCode': u'',
  u'ISO': u'MD',
  u'ISO-Numeric': u'498',
  u'ISO3': u'MDA',
  u'Languages': u'mo,ro,ru,gag,tr',
  u'Phone': u'373',
  u'Population': u'4324000',
  u'Postal Code Format': u'MD-####',
  u'Postal Code Regex': u'^(?:MD)*(\\d{4})$',
  u'fips': u'MD',
  u'geonameid': u'617790',
  u'neighbours': u'RO,UA',
  u'tld': u'.md'}
"""


COUNTRY_INFO_URL = "http://download.geonames.org/export/dump/countryInfo.txt"

def get_geonames_country_data():
    "Returns a list of dictionaries, each representing a country"
    udata = urllib.urlopen(COUNTRY_INFO_URL).read().decode('utf8')
    # Strip the BOM
    if udata[0] == codecs.BOM_UTF8.decode('utf8'):
        udata = udata[1:]
    # Ignore blank lines
    lines = [l for l in udata.split('\n') if l]
    # Find the line with the headers (starts #ISO)
    header_line = [l for l in lines if l.startswith('#ISO')][0]
    headers = header_line[1:].split('\t')
    # Now get all the countries
    country_lines = [l for l in lines if not l.startswith('#')]
    countries = []
    for line in country_lines:
        countries.append(dict(zip(headers, line.split('\t'))))
        lastDS = countries[-1]
        wanted = 'Country ISO ISO3 Continent tld'.split()
        #if 'Germany' in line:
        #    print('DS',lastDS['Country'],lastDS['ISO'], lastDS['ISO3'])
        #if 'United' in line:
        #    print('DS',lastDS['Country'],lastDS['ISO'], lastDS['ISO3'])
            #for k in wanted:
            #  print('DSK', k, lastDS[k] )
            #for kk in lastDS.keys():
            ##  print('DSKK', kk, lastDS[kk] )
    #DS
    #nDS = 0
    #for h in headers:
    #  print('h', h)
    #  if h == 'Germany': print ('DE', nDS)
    #  nDS += 1
    return countries

def getCountryInfo(country):

  countries=get_geonames_country_data()
  iso2, iso3, continent = '-' * 3
  for c in countries:
    #print 'Checking ',  c['Country'], country
    if c['Country'] == country:
      iso2 = c['ISO']
      iso3 = c['ISO3']
      continent = c['Continent']
  return iso2, iso3, continent

def lonlat2ccodes(lon,lat):
    country = getplace(lon, lat)
    iso2, iso3, continent = getCountryInfo(country)
    return iso2, iso3, country, continent

if __name__ == '__main__':

  import sys

  if len(sys.argv) > 1:
     if  sys.argv[1] == '--xy':
         try:
           x, y = map(float, sys.argv[2].split())
           country = getplace(x, y)
           iso2, iso3, continent = getCountryInfo(country)
           print('step-by-step', x, y,  ' => ', iso2, iso3, country, continent )
           iso2, iso3, country, continent = lonlat2ccodes(x,y)
           print('lonlat2codes', x, y,  ' => ', iso2, iso3, country, continent )
         except:
           #print(help(CountryStuff))
           sys.exit('Usage: CountryStuff --xy "lon lat"')

  else: 
      
    # test google suggestion
    #print(getplace(0.1,51.1))
    #print(getplace(0.1,51.2))
    #print(getplace(0.1,51.3))
    print('Mace Heed:  ', getplace( -9.00,53.3175))
    print('Tudor Hill: ', getplace(-64.87,32.27))
    x = -(11.0+53/60.0)
    y=78.0+54/60.0
    print('Zeppelin: ', getplace(x, y))
  
    # test geoname suggestion
    #g=get_geonames_country_data()
    testers = 'Germany Turkey Canada Greenland China India'.split()
    testers.append('New Zealand')
    for ccs in testers:
      iso2, iso3, continent = getCountryInfo(ccs)
      print ccs, 'ISO2:', iso2, 'ISO3:', iso3, 'Cont:', continent
  
