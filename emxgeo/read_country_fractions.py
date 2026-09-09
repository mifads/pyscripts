#!/usr/bin/env python3
"""
Processes country data from emep_ll_gridfraction_{res}degCEIP_2018.nc
  
METHODS:
 get_country_fractions: returns (ccodes_wanted=None,res='01',cfmapWanted=False,smallNorway=True,
    excl_nums_from=400, txt='', dbg=False): # eg IE, BG

    returns dict with:
      lats, lons, dx, dy, cflon0, cflat0 - grid settings of grid used
      cell_km2
      codes_used # e.g. DK, MED,
      sum_seas 
      sum_land
      [iso]['fractions']
      [iso]['sum_area_km2']
      if cfmapWanted:
        ['cfmap'][j,i], e.g. "NL;NOS" or " ATL"

 get_country_sums_or_masks(lons,lats,vals,ccodes=None,masksWanted=False,txt=''): # emep 01 landcover France

   returns country sums for given grid and values
   or masks

"""
import numpy as np
import os
import sys
import xarray as xr
import emxgeo.check_coord_deltas as ccd

#hdir=os.environ['HOME']
tdir='/lustre/storeB/users/davids'
if not os.path.exists(tdir):
  tdir= tdir.replace('storeB','storeA')
  datadir=f'{tdir}/Data_Geo/EMEP_files'
  ecosdir=f'{tdir}/scripts_lc2emep_mapping' # for __main tests
if 'ppi' not in  os.uname().nodename:
  tdir='/home/davids/Work/LANDUSE/'
  datadir='/home/davids/Data'
  ecosdir='/home/davids/Work/LANDUSE/LandInputs_2025' # for __main tests
assert os.path.exists(tdir),'NO INPUT DIR:'+tdir

idbg=341;jdbg=184    # France
idbg= 478; jdbg= 59  # MED 
idbg=391; jdbg=263   # DK in 01 gridfraction file
idbg=259;jdbg=23  # Marocko
idbg=400;jdbg=23  # Algeria
#-----------------------------------------------------------------------------
def get_country_fractions(ccodes_wanted=None,res='01',cfmapWanted=False,smallNorway=True,
    excl_nums_from=400, txt='', dbg=False): # eg IE, BG
  """
   For Norway we usually exclude Svalbard
   We also by default exclude numbers from 400 = sea areas
   We also sum sea-areas:
   BAS=30,NOS=31,ATL=32,MED=33,BLS=34,NAT=35,
  """
  seas = 'ATL BAS NOS MED BLS'.split()

  dtxt='get_coun_frac:' + txt
  ifile= f'{datadir}/EMEP_CountryStuff/emep_ll_gridfraction_{res}degCEIP_2018.nc'
  """  float cell_area(lat, lon) ;
          cell_area:units = "km^2" ;
       short CC_22(lat, lon) ;
                CC_22:units = "%" ;
                CC_22:long_name = "ES" ;
       byte CC_407(lat, lon) ;
             CC_407:long_name = "Kattegat" ;
             CC_407:area_km2 = 23659.4f ;
  """
  ds=xr.open_dataset(ifile)
  isea=402; jsea= 268 # 22% BAS
  dksea = ds['CC_30'].values

  km2=ds.cell_area.values

  countries= dict()
  cflons=ds.lon.values   # 400
  cflats=ds.lat.values   # 260
  countries['lats'] = cflats
  countries['lons'] = cflons
  countries['dx'] = ccd.check_coord_deltas(ds.lon.values)
  countries['dy'] = ccd.check_coord_deltas(ds.lat.values)
  countries['cflon0'] = cflons[0] - 0.5*countries['dx']
  countries['cflat0'] = cflats[0] - 0.5*countries['dy']
  countries['cflon1'] = cflons[-1] + 0.5*countries['dx']
  countries['cflat1'] = cflats[-1] + 0.5*countries['dy']

  countries['cell_km2']  = km2

  if cfmapWanted: #need dtype object for strings
     countries['cfmap'] = np.full_like(km2,dtype=object,fill_value='')

  # get list of codes and numbers
  ccodes = dict()
  for key in ds.keys():
    if key == 'cell_area': continue
    if key.startswith('CC'):            # eg CC_27
       iso = ds[key].long_name  # eg GB
       txt, num = key.split('_')
       #print(dtxt, txt, num, iso )
       try:   # fails for num == ARO, etc - not numbers
         if (int(num) >= excl_nums_from): continue 
       except:
         pass
       if (iso == 'all'): continue 
       if (iso == 'sum'): continue 
       iso = iso.replace(' ','_')  # for e.g. Bothnian Bay
       ccodes[iso] = dict(iso=iso,num=num,key=key)
       if dbg: print(dtxt, txt, num, iso )

  if ccodes_wanted is None:
    ccodes_used = ccodes
  else:
    ccodes_used = {k:ccodes[k] for k in sorted(ccodes_wanted)}
    ccodes_used = set(ccodes_wanted) | set(seas) # Ensure we have seas
  #print('USED ', ccodes_used)



  for iso in ccodes_used: #  in ds.variables:   # eg CC_14 for IE
  
      countries[iso] = dict()
      countries[iso]['fractions'] =  np.full_like(km2,0.0)
      countries[iso]['sum_area_km2'] =  0.0

      key = ccodes[iso]['key']
      c   = ds[key].values  

      if iso=='NO' and  smallNorway: 
         for j, lat in enumerate(ds.lat.values):
           if lat > 72.0:
            break
         if dbg: print('FIX NORWAY', j, ds.lat.values[j]  )
         c[j:,:] = 0.0
      if dbg: print(dtxt+'CCODE', iso, np.max(c), np.min(c) )
      countries[iso]['fractions'][:,:] =  0.01* c
      countries[iso]['sum_area_km2'] = np.sum(km2*countries[iso]['fractions'],where=c>0.0)

      if cfmapWanted:
        for j, lat in enumerate(ds.lat.values):
          for i, lon in enumerate(ds.lon.values):
            #if jdbg==j and idbg == i: print(dtxt+'DBGIJ', i,j, iso, c[j,i])
            if c[j,i]>1.0e-6:
               #countries['cfmap'][j,i] += f' {iso}'
               if countries['cfmap'][j,i] == '':
                 countries['cfmap'][j,i] += iso
               else:
                 countries['cfmap'][j,i] += f';{iso}'
               if jdbg==j and idbg == i: print('DBGIJMAP', i,j, iso, countries['cfmap'][j,i], c[j,i], c[j,i] )


      #if iso=='MED':
      #    print('DEBUG', countries[iso]['sum_area_km2'] )
      #    sys.exit()
      f = countries[iso]['fractions'] 
      if dbg:
        print(dtxt, 'IN', iso, countries[iso]['sum_area_km2'], np.shape(f), np.max(f), np.min(f) )
        if cfmapWanted: print(dtxt+' MAP:', iso, countries['cfmap'][jdbg,idbg])


  # collect sea-areas
  countries['codes_used'] = ccodes_used # Now includes seas
  countries['sum_seas'] =  np.full_like(km2,0.0)
  for sea in seas:
    countries['sum_seas'] +=  countries[sea]['fractions']
  countries['sum_land'] = 1 - countries['sum_seas']
  #print( 'DKSEA', dksea[jsea,isea], countries['sum_seas'][jsea,isea], countries['sum_land'][jsea,isea])
  print('DONE ',dtxt, countries.keys())
  return countries

#-----------------------------------------------------------------------------
def get_country_sums_or_masks(lons,lats,vals,ccodes=None,masksWanted=False,txt=''): # emep 01 landcover France
  """ country sums or masks in the given lat/lon domain.
      By default gets area of vals for countries in ccodes
      if wanted, can return mask (frac) in coords of inputs
  """

  dtxt= f'gcsums({txt}):'

  print('INTO ',dtxt, ccodes)
  cfdata=get_country_fractions(ccodes_wanted=ccodes,cfmapWanted=True)
  cfcodes = cfdata['codes_used'] # usually addes seas
  print('NOW: ',dtxt, cfcodes)
  cflons=cfdata['lons']
  cflats=cfdata['lats']
  km2    = cfdata['cell_km2']
  cfmap  = cfdata['cfmap']

  dx = ccd.check_coord_deltas(lons)
  dy = ccd.check_coord_deltas(lats)
  lon0 = lons[0] - 0.5*dx
  lat0 = lats[0] - 0.5*dx

  # for box calulculation - number of cells before and after mid e.g. with 0.5 deg array get 2,  :
  njj = int(0.001 + dy/cfdata['dy'])//2
  nii = int(0.001 + dx/cfdata['dx'] )//2
  print('NII JJ', nii, njj, dx, dy, cfdata['dx'], cfdata['dy'])

  # coords of idbg,jdbg in local vals coords:
  jvv = int( 0.001+ ( cflats[jdbg] - lat0)/dy)
  ivv = int( 0.001+ ( cflons[idbg] - lon0)/dx)
  #print(f'{dtxt}lons CFRAC: {cflons[0]} {cflons[-1]} {len(cflons)} VALS: {lons[0]} {lons[-1]} {len(lons)}')
  #print(f'{dtxt}lats CFRAC: {cflats[0]} {cflats[-1]} {len(cflats)} VALS: {lats[0]} {lats[-1]} {len(lats)}')
  #print(f'{dtxt}DBGdbg CF:{idbg} {jdbg} {cflons[idbg]:.2f} {cflats[jdbg]:.2f} V: {ivv} {jvv} {lons[ivv]} {lats[jvv]}')


  sumcc=dict()

  if ccodes is None:
    ccodes = list(cfdata.keys())
    for i in 'lons lats cell_km2 cfmap'.split():
      ccodes.remove(i)

  cc_km2=dict()  # Area for each country

  masks = dict()
  ninmask = dict()
  print('THEN: ',dtxt, ccodes)
  #for cc in ccodes:
  for cc in cfcodes:
    if cc.startswith('sum_'): continue
    cc_km2[cc] = cfdata[cc]['fractions'] * km2

    print('CCSUM', cc,  np.sum(cc_km2[cc])) # , cfdata[cc]['sum_area_km2'] ) # =same
    sumcc[cc] = 0.0

    if masksWanted:
      masks[cc] = np.zeros([len(lats),len(lons)])
      ninmask[cc] = np.zeros([len(lats),len(lons)])

  # Loop over input array
  for j, lat in enumerate(lats):
    if lat < cfdata['cflat0']: continue
    if lat > cfdata['cflat1']: continue
    jcc = int( 0.001+ ( lat - cfdata['cflat0'])/cfdata['dy'])

    for i, lon in enumerate(lons):
      if vals[j,i] < 1.0e-6: continue
      if lon < cfdata['cflon0']: continue
      if lon > cfdata['cflon1']: continue
      icc = int( 0.001+ ( lon - cfdata['cflon0'])/cfdata['dx'] )

      for jj in range(-njj,njj+1):
        jjj = jcc + jj
        if jjj < 0 or jjj+1 > len(cflats): continue

        for ii in range(-nii,nii+1):
          iii = icc + ii
          if iii < 0 or iii+1 > len(cflons): continue

          if len( cfdata['cfmap'][jjj,iii] ) < 1: continue # avoids empty ''

          for cc in cfdata['cfmap'][jjj,iii].split(';'):

            if i==ivv and j==jvv: # dbg in local coords
              print(f'BOX {cc} {lon} {lat}  {iii:4d} {jjj:4d}  CF:{cflons[iii]:.3f}'
                   f' {cflats[jjj]:.3f} {cfdata["cfmap"][jjj,iii]} cc_km2:{cc_km2[cc][jjj,iii]}') 
            #try:
            #  area = vals[j,i] * cc_km2[cc][jjj,iii]
            #except:
            #  print(f'BOX {cc} {lon} {lat}  {iii:4d} {jjj:4d}  CF:{cflons[iii]:.3f}'
            #        f' {cflats[jjj]:.3f} {cfdata["cfmap"][jjj,iii]} cc_km2:{cc_km2[cc][jjj,iii]}') 
            area = vals[j,i] * cc_km2[cc][jjj,iii]

            sumcc[cc] += area
            if masksWanted:
               masks[cc][j,i] += cfdata[cc]['fractions'][jcc,icc]
               ninmask[cc][j,i]   += 1

      #dbg = ( i==idbg and j==jdbg )
      #if dbg:
      #print(f'DBGijlat  V: {j} {lat} {dy} jCF: {jcc} {cflats[jcc]:.2f}  {cfdata['dy']:.2f} {cfdata['cfmap'][jcc,icc]}')

  if masksWanted:
    #for cc in masks.keys():
    xmasks = dict() # will only include asked-for ccodes
    for cc in ccodes:
      print('MASKING ', cc, masks.keys() )
      xmasks[cc] = np.where(ninmask[cc]>0,masks[cc]/ninmask[cc],0.0)
    return xmasks
  else: # no easy way to sort dicts as dicts, except:
    return { k:v for k, v in sorted(sumcc.items()) }
  
#-----------------------------------------------------------------------------
#def get_country_mask(lons,lats,vals,ccodes=None,txt=''): # emep 01 landcover France
#
#  dx = ccd.check_coord_deltas(lons)
#  dy = ccd.check_coord_deltas(lats)
#  lon0 = lons[0] - 0.5*dx
#  lat0 = lats[0] - 0.5*dx

#-----------------------------------------------------------------------------
if __name__ == '__main__':

  import emxplots.plotmap as pmap
  testing='sums'  # or fracs
  codes='PT ES FR IT HR GR DE NL DK NO SE FI RU'.split()
  codes='DE NL DK NO SE FI RU'.split()
  codes='DK ES'.split()
  label='ifs'
  label='ecosg-emep'
  testing='fracs'  # or fracs

  cfdata=get_country_fractions(codes,cfmapWanted=True,dbg=True)
  print( cfdata.keys())  # includes codes + sea areas + LL, dx, dy, cfdata['cflon0']

  lons=np.linspace(-20,40,121)  # 0.5 deg test grid
  lats=np.linspace(30,65,71)
  tstvals = np.ones([len(lats),len(lons)])
  tst = get_country_sums_or_masks(lons,lats,tstvals,txt='tst',masksWanted=True,ccodes=codes) #,idbg=idbg,jdbg=jdbg)
  for tstcc in tst.keys():
    pmap.plotmap(tst[tstcc],tstcc)






#ABC  # testing application to landcover
#ABC
#ABC  if label=='ecosg-emep':
#ABC    ifile= f'{ecosdir}/landcover_ecosg4emep_0p5_v1.nc'
#ABC    matching = [ 'Tr', ]
#ABC    shortstrs = {'DUMMY':'DUMMY'}
#ABC
#ABC  elif label=='ifs':
#ABC    ifile= f'{tdir}/Data_IFS/scripts_IFS/IFS4emep_0p5.nc'
#ABC    matching = 'trees forest'.split()
#ABC    shortstrs = {'_Evergreen':'Ev','_Deciduous':'De' ,'_broadleaf':'Br',
#ABC       '_needleleaf':'Ne' ,'_Mixed_forest':'Mixed' ,'_trees':'Tr' }
#ABC
#ABC  lcds=xr.open_dataset(ifile)
#ABC  lons=lcds.lon.values
#ABC  lats=lcds.lat.values
#ABC  areas=dict()
#ABC
#ABC  vegs=[]
#ABC  ccs = set()
#ABC
#ABC  for veg in lcds.keys():
#ABC    found=True
#ABC    for m in matching:
#ABC     if m not in veg:
#ABC       found=False
#ABC     else:
#ABC       found=True
#ABC       break
#ABC    if found: print('FOUND', veg, m)
#ABC    else:
#ABC      print('SKIP', veg)
#ABC      continue
#ABC
#ABC    vegs.append(veg)
#ABC    vals = lcds[veg].values
#ABC    #--------------------------------------------
#ABC    areas[veg] = get_country_sums(lons,lats,vals,txt=veg,ccodes=codes) #,idbg=idbg,jdbg=jdbg)
#ABC    ifr=370;jfr=277
#ABC    #print('VEGAREA ', veg, vals[jfr,ifr], areas[veg]['FR'])
#ABC    #--------------------------------------------
#ABC    ccs = ( ccs | areas[veg].keys() )
#ABC
#ABC  print('VEGES', vegs, vegs[0] )
#ABC  vegcodes = vegs.copy()
#ABC
#ABC  def shorten(veg,pairs):
#ABC    newveg = veg
#ABC    for long, short in pairs.items():
#ABC      newveg = newveg.replace(long,short)
#ABC    return newveg
#ABC
#ABC  if label=='ifs':
#ABC    vegrow = ''.join( [ f'{shorten(v[6:],shortstrs):9s}' for v in vegcodes ])
#ABC  else:
#ABC    vegrow = ''.join( [ f'{v.replace('LC:',''):9s}' for v in vegcodes ])
#ABC  #vegrow = ''.join( [ f'{shorten(v[6:],shortstrs):9s}' for v in vegcodes ])
#ABC
#ABC  with open(f'Table_{label}.txt','w') as tab:
#ABC    #print(f'{'Land':<17s} {vegrow}     Sum')
#ABC    tab.write(f'{'Land':<17s} {vegrow}     Sum\n')
#ABC    for cc in sorted(ccs):
#ABC      vegrow=''
#ABC      for v in vegs:
#ABC        if cc not in areas[v].keys():
#ABC           areas[v][cc] = 0.0
#ABC        vegrow += f'{0.001*areas[v][cc]:9.2f}'  # Now in 1000 km2
#ABC      sumveg = 0.001 * np.sum ( [areas[v][cc] for v in vegs ])
#ABC      #vegrow = ''.join( [ f'{areas[v][cc]:10.1f}' for v in vegs ])
#ABC      #print(f'{cc:<15s} {vegrow}  {sumveg:12.2f}')
#ABC      tab.write(f'{cc:<15s} {vegrow}  {sumveg:12.1f}\n')
#ABC   
#ABC   
#ABC   
