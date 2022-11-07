#!/usr/bin/env python3
#formatted with yapf3 --style=google
import argparse
import glob
import numpy as np
import pandas as pd
import xarray as xr
import os
import sys
import emxcdf.makecdf as cdf
#import emxgeo.km2_area_of_wgs84pixel as km2cell  # (center_lat, pixel_size):
Usage="""
  Usage:
     ceip2emep.py -i CEIP_DIR  -o  odir
  e.g.
     ceip2emep.py -i /home/davids/MDISKS/Nebula/Agnes/work/emis01degEMEP/trends_2022  -o TMPDIR 
    DEAL with years later

"""

#----------- user changable ----------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('-i','--idir',help='location of .txt files')
parser.add_argument('-y','--year',help='year')
parser.add_argument('-o','--odir',help='location of .txt files')
#parser.add_argument('-s','--style',help='Style of TNO input file, e.g. cams3p1, NMR-RWC')
args=parser.parse_args()

debugCheck = False # was just used to compare with Agnes's f90 version for 1 sector
ceipdir = '/home/davids/MDISKS/Nebula/Agnes/work/emis01degEMEP'  # Dave's sshfs mount
ceipdir = '/nobackup/forsk/sm_agnny/emis01degEMEP'  # nebula

# changed path after RO, 2006 bug fixes
# BUG here was ALLDATA.
exclude_C = 'none'  # Keep lower case to avoid match with e.g. AT
exclude_C = 'YEP' 
if exclude_C == 'none':
  polls = "CO NH3 NMVOC NOx PM2_5 PMcoarse SOx".split()  # skips PM10, BC
  odir    = '/nobackup/forsk/sm_davsi/Data/inputs_emis/NMR-RWC/Emis4Emep/Apr2022/CEIP2021'  # nebula
else:
  polls = "PM2_5".split()  # skips PM10, BC
  exclude_C= 'ES FR RU TR GB BE SE PT NO GR FI AL IT DE PL BY BG IE UA RO AT EE HU DK LV LT BA RS SI HR CH CZ LU SK MK MD CY NL KOS ME MT'.split()
  odir    = '/nobackup/forsk/sm_davsi/Data/inputs_emis/NMR-RWC/Emis4Emep/Apr2022/CEIP2021_noPMfC'  # nebula

if args.idir is not None:  # CEIP for Agri so far:
    polls = "CO NH3 NMVOC NOx PM2_5 PMcoarse SOx".split()  # skips PM10, BC
    #SEP22 tests polls = "NMVOC".split()  # skips PM10, BC
    ceipdir = args.idir
if args.odir is not None:
    odir = args.odir
print('CEIPDIR', ceipdir)
print('ODIR', odir)

#--- best on nebula for multi-polls
if len(polls) > 1:
    assert 'sm_dav' in os.environ['USER'], 'TOO MANY POLLS FOR PC'

if debugCheck:
  polls='NOx'.split()
  odir = 'HERE'
  dbgfiles = glob.glob('%s/NOx_F_*2021_GRID_2019.txt' % ceipdir)

pollmap = dict(CO='co',
               NH3='nh3',
               NMVOC='voc',
               NOx='nox',
               SOx='sox',
               PM2_5='pm25',
               PMcoarse='pmco')
dx = 0.1
dy = 0.1  # set by hand. Safest.
if args.year is not None:
  years = [ int( args.year ), ]
else:
  years = range(2019, 2004,-1)
  years = range(2019, 2020)
#years = range(2005, 2010)
#years = range(2019, 2020)
one_big_output = False  # If true, one big file created with all polls for each year. Otherwise one per poll
sigfigs = 6  # number significant figures in output. Set negative to skip
# April 2022. Need to exclude GNFR C PMf from:
#----------- end of user changable ---------------------------
assert os.path.isdir(ceipdir), 'Missing CEIP dir %s' % ceipdir
os.makedirs(odir,exist_ok=True)

globattrs = {
    'Conventions': "CF-1.0",
    'projection': "lon lat",
    'Created_by':
        'ceip2emep',  # codetxt.codetxt(__file__),  # will add script and date
    'Data_from': "CEIP",
    'MSC-W_Contact': "Agnes Nyiri (emissions), David Simpson (script)",
    'Sector_names': "GNFR_CAMS",
    'sec01': "A_publicpower",
    'sec02': "B_industry",
    'sec03': "C_otherstationarycomb",
    'sec04': "D_fugitive",
    'sec05': "E_solvents",
    'sec06': "F_roadtransport",
    'sec07': "G_shipping",
    'sec08': "H_aviation",
    'sec09': "I_offroad",
    'sec10': "J_waste",
    'sec11': "K_agrilivestock",
    'sec12': "L_agriother",
    'sec13': "M_other",
    'sec14': "A1_PublicPower_Point",
    'sec15': "A2_PublicPower_Area",
    'sec16': "F1_RoadTransportExhaustGasoline",
    'sec17': "F2_RoadTransportExhaustDiesel",
    'sec18': "F3_RoadTransportExhaustLPGgas",
    'sec19': "F4_RoadTransportNonExhaust",
    'periodicity': "yearly",
}


def nf(x):
    """ Used with lon/lat ranges and dimensions converts eg 0.09999999999787 to 0.1 """
    return float('%12.6f' % x)


def tmpcreate_xrcdf(xrarrays,
                 globattrs,
                 outfile,
                 timeVar='',
                 skip_fillValues=False):
    """ Creates netcdf4 file.  """

    xrdatasets = []

    print('XRCDF:', len(xrarrays), type(xrarrays))
    for a in xrarrays:
        varname = a['varname']
        print('XR sub ', varname, a['attrs'], type(a['attrs']))
        print('XR keys', varname, a.keys())
        print('XR coords', varname, a.keys())
        field = xr.DataArray(a['data'],
                             dims=a['dims'],
                             coords=a['coords'],
                             attrs=a['attrs'])
        xrdatasets.append(xr.Dataset({varname: field}))

    outxr = xr.merge(xrdatasets)
    outxr.lon.attrs = {
        'long_name': 'longitude',
        'units': 'degrees_east',
#        '_FillValue': False,
        'standard_name': 'longitude'
    }
    outxr.lat.attrs = {
        'long_name': 'latitude',
        'units': 'degrees_north',
#        '_FillValue': False,
        'standard_name': 'latitude'
    }
    #for key, val in globattrs.items():
    #    outxr.attrs[key] = val

    encoding = dict()
    #for var in outxr.coords:  # Coordinates should never need FillValue!
    # was following https://stackoverflow.com/questions/45693688/xarray-automatically-applying-fillvalue-to-coordinates-on-netcdf-output#45696423
    # but didn't work. Added FillValue above
    #    print('OUTXR coords ', var)
    #    encoding[var] = {'zlib':False,'_FillValue': False}

    # compression settings:
    data_comp = dict(zlib=True, complevel=5, shuffle=True,  # _FillValue=np.nan,
                     dtype='float32')  
    if sigfigs > 0:
        data_comp['least_significant_digit'] = np.int32(sigfigs)
        globattrs['least_significant_digit'] = np.int32(sigfigs)

    for var in outxr.data_vars:
        encoding[var] = data_comp
        print('OUTXR vars ', var, data_comp)
        #if skip_fillValues is True:
        #    encoding[var]['_FillValue'] = False
        #else:
        #    encoding[var]['_FillValue'] = 0.0

    #globattrs = globattrs | data_comp
    for key, val in globattrs.items():
        outxr.attrs[key] = val
    outxr.to_netcdf(outfile, format='netCDF4', encoding=encoding)
    outxr.close()


def character_range(char1, char2):
    """ range from 'a' to 'z, make use of e.g. ord('A') = 65... """
    for char in range(ord(char1), ord(char2) + 1):
        yield (char)

sectorcodes = dict()
for k, letter in enumerate(character_range('A', 'M')):
    sectorcodes[chr(letter)] = k + 1
    print(chr(letter), k+1,   end=', ')

for year in years:

    print('STARTING YEAR ', year )
    # Start by scanning for lat/lon limits
    idir = '%s/%d' % (ceipdir, year)
    files = glob.glob('%s/*.txt' % idir) # NB NEED TO REPEATE BELOW ######
    files = glob.glob('%s/*%d.txt' % (idir, year)) # Agri-VOC FIX
    if debugCheck:
      files = dbgfiles
      print('FILES', ceipdir, year )
      print('FILES', files)
    xmin = 999.
    xmax = -999.
    ymin = 999.
    ymax = -999.
    # from frac file:
    #May xmin = -29.95
    #May xmax = 89.95
    #May ymin = 30.05
    #May ymax = 81.95

    if xmax < 0:  # find domain from files:
        for nfile, ifile in enumerate(files):
            print('READING ', nfile, ifile )
            if '_new.txt' in ifile or  'Bacau' in ifile:
                continue
            df = pd.read_csv(ifile, sep=";", header=4)
            lats = np.sort(np.unique(df.LATITUDE.values))
            lons = np.sort(np.unique(df.LONGITUDE.values))

            #km2 = np.zeros([len(lats)]) # , len(lons)])
            #for j, lat in enumerate(lats):
            #  km2[j] =  mk2cell(lat,dy) 

            if len(lons) > 0:  # some files have only headers
                if lons[0] < xmin:
                    xmin = lons[0]
                if lats[0] < ymin:
                    ymin = lats[0]
                if lons[-1] > xmax:
                    xmax = lons[-1] + 1
                if lats[-1] > ymax:
                    ymax = lats[-1] + 1
            print(nfile, os.path.basename(ifile), len(lons), xmin, xmax, ymin,
                  ymax)

    nlons = int((xmax - xmin) / dx)
    nlats = int((ymax - ymin) / dy)
    print(year, xmin, xmax, nlons)
    # Make uniform coords:
    lons = np.linspace(xmin, xmin + nlons*dx, nlons + 1)
    lats = np.linspace(ymin, ymin + nlats*dy, nlats + 1)
    print('Lon', xmin, dx, xmax, len(lons), 'tmpdx:', lons[1] - lons[0],
          lons[0], lons[-1])
    print('Lat', ymin, dy, ymax, len(lats), 'tmpdy:', lats[1] - lats[0])

    # edges
    xleft   = nf(xmin - 0.5 * dx)
    xright  = nf(xmax + 0.5 * dx)
    ybottom = nf(ymin - 0.5 * dy)
    ytop    = nf(ymax + 0.5 * dy)

    countries_used = set(['tot']) # will store totals (could also use {'tot'} for set
    srcfiles = dict() # will store file name

    # Now, start data processing...
    if one_big_output:
        xrarrays = []  # stores arrays for netcdf

    for poll in polls:

        if not one_big_output:
            xrarrays = []  # stores arrays for netcdf
        olog = open('Logging_sums_%d_%s.txt' % ( year, poll), 'w' )
        olog.write('iso')
        for i in range(1,21):
          olog.write('%11d' % i )
        olog.write('\n')

        idir = '%s/%d' % (ceipdir, year)
        files = glob.glob('%s/%s*.txt' % (idir, poll))
        files = glob.glob('%s/%s*%d.txt' % (idir,poll, year)) # Agri-VOC FIX
        if debugCheck:
          files = dbgfiles

        sectemis = dict()
        sumemis = dict()
        sumemis['tot'] = np.zeros(20)

        for nfile, ifile in enumerate(files):

            #if nfile > 3: continue

            # BUG FIX RO:
            if '_new.txt' in ifile or  'Bacau' in ifile:
                print('SKIP new FILE', ifile)
                continue
            if year == 2006 and '_2000.txt' in ifile:
                print('SKIP extra 2006 FILE', ifile)
                continue


            df = pd.read_csv(ifile, sep=";", header=4)
            tmpiso = df.columns[0]  # Includes "  # Format: ISO2"
            countries = set(df[tmpiso].unique())
            countries_used = countries_used | countries  # Union of sets -> all
            countries_list = list( sorted(countries_used ))
            #print('Countries:', len(countries), len(countries_used))
            #print('Countries:', countries_list)
            #sys.exit()
            tmpname = os.path.basename(ifile).replace(
                'PM2_5', 'PM25')  # simplify to allow next split for all polls
            fields = tmpname.split(
                '_')  # e.g. PM25_A_PublicPower_2021_GRID_2015.txt
            #xpoll=fields[0]
            sect = fields[1]
            #print('SECT', sect )
            if sect == 'NT':
                continue  # totals

            isect = np.int32(sectorcodes[sect])  # from A to 1
            secname = fields[2]
            #print(ifile, sect, poll, secname, isect)

            #SEP22 BUG FIX vtot = '%s_%s_sec%2.2d' % ('tot', sect, isect)
            #SEP22 BUX FIX?
            vtot = '%s_%s_sec%2.2d' % ('tot', pollmap[poll], isect)  
            if vtot not in sectemis.keys():
                sectemis[vtot] = np.zeros([len(lats), len(lons)])
                print('New vtot: ', vtot, sect )


            for index, row in df.iterrows():
                iso2 = row[tmpiso]  # .ISO2
                print('TMP', iso2, sect, isect, secname, iso2 in exclude_C)
#            for isect in range(1, 20):
                if iso2 in exclude_C and sect == 'C':
                    print('ExcludeC: ', iso2, sect )
                    continue
                if iso2 not in sumemis:
                    print('ADDISO2', iso2, poll )
                    sumemis[iso2] =  np.zeros(20)

                lon = row.LONGITUDE
                lat = row.LATITUDE

                # Mangled .txt files will throw errors here:
                try:
                  if lon < xleft or lon > xright or lat < ybottom or lat > ytop:
                   print('XXLL', iso2, lon, lat, sect, poll)
                except:
                  print('XXLLPROBLEM', iso2, lon,  xleft, dx, lat, sect, poll )
                  print('XXLLPROBLEM L',  index,   tmpname) 
                  sys.exit(row)
                try:
                  ix = int((lon - xleft) / dx)
                except:
                  print('XXPROBLEM', iso2, lon,  xleft, dx, lat, sect, poll )
                  sys.exit(row)

                iy = int((lat - ybottom) / dy)
                if ix > nlons - 1 or iy > nlats - 1:
                    continue  # just skip
                    print('OOPS', lon, lat, iso2, ix, iy, ifile)
                    sys.exit()

                x = row.EMISSION
                # BUG FIX 
                if iso2=='RO' and poll=='NOx' and np.abs(lon-26.95)<0.01 and np.abs(lat-46.65)<0.01:
                    print('BUG FIX RO ', ifile, year)
                    x = 0.008086  # Agnes used same value for 2005, 2015 and 2019.

                if x > 0.0:

                    v = '%s_%s_sec%2.2d' % (iso2, pollmap[poll], isect)  # e.g. AT_PM25_sec03
                    vtot = '%s_%s_sec%2.2d' % ('tot', pollmap[poll], isect)  

                    if v not in sectemis.keys():
                        sectemis[v] = np.zeros([len(lats), len(lons)])
                        srcfiles[v] = tmpname

                    sectemis[v][iy, ix] += x
                    sectemis[vtot][iy, ix] += x
                    sumemis[iso2][isect] +=  x    # NOT AREA BASED?? * km2[iy] )
                    sumemis['tot'][isect] +=  x    # NOT AREA BASED?? * km2[iy] )

        # Now, add to xrarrays (alph and number order)
        #SEP2022 for iso2 in countries_list:  #  + [ 'tot' ]:
        #print('SUMSEP22 ',  np.sum(sectemis['tot_A_sec01']), np.sum(sectemis['tot_K_sec11'])  )
        for iso2 in countries_list + [ 'tot' ]:
            if iso2 not in sumemis: 
                print('KEY NOT FOUND: ', poll,  iso2, isect )
                continue
            olog.write('%3s ' % iso2 )
            for isect in range(1, 20):
                v = '%s_%s_sec%2.2d' % (iso2, pollmap[poll], isect)
                print('SEP22v', v, vtot, vtot in sectemis )
                try:
                  if sumemis[iso2][isect] > 10.0:  # SEP 6 WHY: or  sumemis[iso2][isect] < 1.0e-6 :
                    olog.write('%11.1f' %  sumemis[iso2][isect] )
                  else:
                    olog.write('%11.3e' %  sumemis[iso2][isect] )
                except:
                  print('KEY ERRROR', iso2, isect )
                  sys.exit()
                if iso2=='tot': print('SEP22: ', iso2, v, vtot,  v in sectemis )
                if v in sectemis.keys():

                    print('ENDING %4s %d %12s   %20s %12.5f' %
                          (iso2, isect, poll, v, 1.0e-6 * np.sum(sectemis[v])))

                    if iso2=='tot': print('SEP22: ', iso2, v, sectemis[v] )
                    if np.sum(sectemis[v]) > 0.0:
                        if iso2 == 'tot':
                          attrs = {
                                'units': 'tonnes',
                                'sector': isect
                          }  # Skip species, stops emissions being used
                        else:
                          attrs = {
                            'units': 'tonnes',
                            'country_ISO': iso2,
                            'srcfile': srcfiles[v],
                            'species': pollmap[poll],
#                            '_FillValue': False,
                            'sector': np.int32(isect)
                          }
                        xrarrays.append(
                            dict(varname=v,
                                 dims=['lat', 'lon'],
                                 attrs=attrs,
                                 coords={
                                     'lon': lons,
                                     'lat': lats
                                 },
                                 data=sectemis[v].copy()))
            olog.write('%12.1f\n' %  np.sum(sumemis[iso2][:]) )
             

        #sys.exit('TMPR')
        #---end poll
        if not one_big_output:
            ofile = odir+'/outcdf_' + poll + '_%d.nc' % year
            xrout = cdf.create_xrcdf(xrarrays,
                                 globattrs=globattrs,
                                 outfile=ofile) #  skip_fillValues=True)
#            sys.exit()

    if one_big_output:
        ofile = odir+'/outcdf_' + 'ALL' + '_%d.nc' % year
        xrout = cdf.create_xrcdf(xrarrays,
                             globattrs=globattrs,
                             outfile=ofile) #,
                            # skip_fillValues=True)

