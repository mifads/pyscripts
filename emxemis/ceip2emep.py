#!/usr/bin/env python3
#formatted with yapf3 --style=google
import glob
import numpy as np
import pandas as pd
import xarray as xr
import os
import sys

#----------- user changable ----------------------------------
ceipdir = '/home/davids/MDISKS/Nebula/Agnes/work/emis01degEMEP'  # Dave's sshfs mount
ceipdir = '/nobackup/forsk/sm_agnny/emis01degEMEP'  # nebula
polls = "CO NH3 NMVOC NOx PM2_5 PMcoarse SOx".split()  # skips PM10, BC
pollmap = dict(CO='co',
               NH3='nh3',
               NMVOC='voc',
               NOx='nox',
               SOx='sox',
               PM2_5='pm25',
               PMcoarse='pmco')
dx = 0.1
dy = 0.1  # set by hand. Safest.
years = range(2015, 2016)
one_big_output = False  # If true, one big file created with all polls for each year. Otherwise one per poll
sigfigs = 6  # number significant figures in output. Set negative to skip
#----------- end of user changable ---------------------------
assert os.path.isdir(ceipdir), 'Missing CEIP dir %s' % ceipdir

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


def create_xrcdf(xrarrays,
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
        '_FillValue': False,
        'standard_name': 'longitude'
    }
    outxr.lat.attrs = {
        'long_name': 'latitude',
        'units': 'degrees_north',
        '_FillValue': False,
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
    #print(chr(letter), k+1,   end=', ')

for year in years:  #  range(2015,2016):

    # Start by scanning for lat/lon limits
    idir = '%s/%d' % (ceipdir, year)
    files = glob.glob('%s/*.txt' % idir)
    xmin = 999.
    xmax = -999.
    ymin = 999.
    ymax = -999.
    # from frac file:
    xmin = -29.95
    xmax = 89.95
    ymin = 30.05
    ymax = 81.95

    if xmax < 0:  # find domain from files:
        for nfile, ifile in enumerate(files):
            df = pd.read_csv(ifile, sep=";", header=4)
            lats = np.sort(np.unique(df.LATITUDE.values))
            lons = np.sort(np.unique(df.LONGITUDE.values))
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

    countries_used = set('tot')  # will store totals
    srcfiles = dict() # will store file name

    # Now, start data processing...
    if one_big_output:
        xrarrays = []  # stores arrays for netcdf

    for poll in polls:

        if not one_big_output:
            xrarrays = []  # stores arrays for netcdf

        idir = '%s/%d' % (ceipdir, year)
        files = glob.glob('%s/%s*.txt' % (idir, poll))

        sectemis = dict()

        for nfile, ifile in enumerate(files):

            #if nfile > 3: continue

            df = pd.read_csv(ifile, sep=";", header=4)
            tmpiso = df.columns[0]  # Includes "  # Format: ISO2"
            countries = set(df[tmpiso].unique())
            countries_used = countries_used | countries  # Union of sets -> all
            print('Countries:', len(countries), len(countries_used))
            tmpname = os.path.basename(ifile).replace(
                'PM2_5', 'PM25')  # simplify to allow next split for all polls
            fields = tmpname.split(
                '_')  # e.g. PM25_A_PublicPower_2021_GRID_2015.txt
            #xpoll=fields[0]
            sect = fields[1]
            if sect == 'NT':
                continue  # totals
            isect = np.int32(sectorcodes[sect])  # from A to 1
            secname = fields[2]
            print(ifile, sect, poll, secname, isect)

            vtot = '%s_%s_sec%2.2d' % ('tot', sect, isect)
            if vtot not in sectemis.keys():
                sectemis[vtot] = np.zeros([len(lats), len(lons)])

            for index, row in df.iterrows():
                iso2 = row[tmpiso]  # .ISO2

                lon = row.LONGITUDE
                lat = row.LATITUDE
                if lon < xleft or lon > xright or lat < ybottom or lat > ytop:
                    print('XXLL', iso2, lon, lat, sect, poll)
                ix = int((lon - xleft) / dx)
                iy = int((lat - ybottom) / dy)
                if ix > nlons - 1 or iy > nlats - 1:
                    continue  # just skip
                    print('OOPS', lon, lat, iso2, ix, iy, ifile)
                    sys.exit()

                x = row.EMISSION

                if x > 0.0:

                    v = '%s_%s_sec%2.2d' % (iso2, pollmap[poll], isect)  
                             # e.g. AT_PM25_sec03

                    if v not in sectemis.keys():
                        sectemis[v] = np.zeros([len(lats), len(lons)])
                        srcfiles[v] = tmpname

                    sectemis[v][iy, ix] += x
                    sectemis[vtot][iy, ix] += x

        # Now, add to xrarrays (alph and number order)
        for iso2 in sorted(countries_used):  #  + [ 'tot' ]:
            for isect in range(1, 20):
                v = '%s_%s_sec%2.2d' % (iso2, pollmap[poll], isect)
                if v in sectemis.keys():

                    print('ENDING %4s %d %12s   %20s %12.5f' %
                          (iso2, isect, poll, v, 1.0e-6 * np.sum(sectemis[v])))

                    if np.sum(sectemis[v]) > 0.0:
                        attrs = {
                            'units': 'tonnes',
                            'country_ISO': iso2,
                            'srcfile': srcfiles[v],
                            'species': pollmap[poll],
                            '_FillValue': False,
                            'sector': np.int32(isect)
                        }
                        if iso2 == 'tot':
                            attrs = {
                                'units': 'tonnes',
                                'sector': isect
                            }  # Skip species, stops emissions being used
                        xrarrays.append(
                            dict(varname=v,
                                 dims=['lat', 'lon'],
                                 attrs=attrs,
                                 coords={
                                     'lon': lons,
                                     'lat': lats
                                 },
                                 data=sectemis[v].copy()))

        #---end poll
        if not one_big_output:
            ofile = 'outcdf_' + poll + '_%d.nc' % year
            xrout = create_xrcdf(xrarrays,
                                 globattrs=globattrs,
                                 outfile=ofile, skip_fillValues=True)
#            sys.exit()

    if one_big_output:
        ofile = 'outcdf_' + 'ALL' + '_%d.nc' % year
        xrout = create_xrcdf(xrarrays,
                             globattrs=globattrs,
                             outfile=ofile,
                             skip_fillValues=True)
