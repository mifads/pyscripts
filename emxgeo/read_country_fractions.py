#!/usr/bin/env python3
"""   float cell_area(lat, lon) ;
            cell_area:units = "km^2" ;
      byte CC_407(lat, lon) ;
             CC_407:long_name = "Kattegat" ;
             CC_407:area_km2 = 23659.4f ;
"""
import numpy as np
import os
import sys
import xarray as xr
import emxgeo.check_coord_deltas as ccd

tdir='/lustre/storeB/users/davids'
if not os.path.exists(tdir):
  tdir= tdir.replace('storeB','storeA')
if 'ppi' not in  os.uname().nodename:
  tdir='/home/davids/Work/LANDUSE/'
assert os.path.exists(tdir),'NO INPUT DIR:'+tdir

idbg=391; jdbg=263   # DK in 01 gridfraction file
idbg=341;jdbg=184    # France
idbg= 478; jdbg= 59  # MED 
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
  ifile= f'{tdir}/Data_Geo/EMEP_files/EMEP_CountryStuff/emep_ll_gridfraction_{res}degCEIP_2018.nc'
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
               countries['cfmap'][j,i] += f' {iso}'
               #countries['cfmap'][j,i].append(iso)
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
def get_country_sums(lons,lats,vals,ccodes=None,txt=''): # emep 01 landcover France

  dtxt= f'gcsums({txt}):'

  #print('INTO ',dtxt, ccodes)
  cfdata=get_country_fractions(ccodes_wanted=ccodes,cfmapWanted=True)
  ccodes = cfdata['codes_used']
  cflons=cfdata['lons']
  cflats=cfdata['lats']
  cfdx = cfdata['dx']      # 0.1
  cfdy = cfdata['dy']
  cflon0 = cflons[0]  - 0.5*cfdx
  cflat0 = cflats[0]  - 0.5*cfdy
  cflon1 = cflons[-1] + 0.5*cfdx
  cflat1 = cflats[-1] + 0.5*cfdy
  km2    = cfdata['cell_km2']
  cfmap  = cfdata['cfmap']

  dx = ccd.check_coord_deltas(lons)
  dy = ccd.check_coord_deltas(lats)
  lon0 = lons[0] - 0.5*dx
  lat0 = lats[0] - 0.5*dx

  # for box calulculation:
  njj = int(0.001 + dy/cfdy)//2
  nii = int(0.001 + dx/cfdx)//2

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

  for cc in ccodes:
    if cc.startswith('sum_'): continue
    cc_km2[cc] = cfdata[cc]['fractions'] * km2

    #print('CCSUM', cc,  np.sum(cc_km2[cc])) # , cfdata[cc]['sum_area_km2'] ) # =same
    sumcc[cc] = 0.0
  #sys.exit()

  for j, lat in enumerate(lats):
    if lat < cflat0: continue
    if lat > cflat1: continue
    jcc = int( 0.001+ ( lat - cflat0)/cfdy)

    for i, lon in enumerate(lons):
      if vals[j,i] < 1.0e-6: continue
      if lon < cflon0: continue
      if lon > cflon1: continue
      icc = int( 0.001+ ( lon - cflon0)/cfdx)

#        if cc=='DK':
#            print('SPLDK', cc, vals.shape, cc_km2[cc].shape, i,j,icc,jcc, lons[i],lats[j],cflons[icc],cflats[jcc], vals[j,i], cc_km2[cc][jcc,icc])
      for jj in range(-njj,njj+1):
        jjj = jcc + jj
        for ii in range(-nii,nii+1):
          iii = icc + ii
          for cc in cfdata['cfmap'][jjj,iii].split():
            if i==ivv and j==jvv:
              print(f'BOX {cc} {lon} {lat}  {iii:4d} {jjj:4d}  CF:{cflons[iii]:.3f} {cflats[jjj]:.3f} {cfdata["cfmap"][jjj,iii]} cc_km2:{cc_km2[cc][jjj,iii]}') 
            try:
              area = vals[j,i] * cc_km2[cc][jjj,iii]
            except:
              print(f'BOX {cc} {lon} {lat}  {iii:4d} {jjj:4d}  CF:{cflons[iii]:.3f} {cflats[jjj]:.3f} {cfdata["cfmap"][jjj,iii]} cc_km2:{cc_km2[cc][jjj,iii]}') 

            sumcc[cc] += area

      #dbg = ( i==idbg and j==jdbg )
      #if dbg:
      #print(f'DBGijll0  V: {lon} {lon0} iCF: {icc} {cflons[icc]:.2f}  {cfdx:.2f} {cfdata['cfmap'][jcc,icc]}')
      #print(f'DBGijlon  V: {i} {lon} {dx} iCF: {icc} {cflons[icc]:.2f}  {cfdx:.2f} {cfdata['cfmap'][jcc,icc]}')
      #print(f'DBGijlat  V: {j} {lat} {dy} jCF: {jcc} {cflats[jcc]:.2f}  {cfdy:.2f} {cfdata['cfmap'][jcc,icc]}')
      #print(f'DBGij {lon} {lat} {cflons[icc]} {icc} {jcc} {cflats[jcc]} {cfdata['cfmap'][jcc,icc]}')

  # no easy way to sort dicts as dicts, except:
  return { k:v for k, v in sorted(sumcc.items()) }
  

#-----------------------------------------------------------------------------
if __name__ == '__main__':

  testing='fracs'  # or fracs
  testing='sums'  # or fracs
  codes='DE NL DK NO SE FI RU'.split()
  codes='PT ES FR IT HR GR DE NL DK NO SE FI RU'.split()
  label='ifs'
  label='ecosg-emep'

  if testing=='fracs':
    cfdata=get_country_fractions(codes,cfmapWanted=True,dbg=True)
    #cfdata=get_country_fractions(dbg=True)
    print( cfdata.keys())
    sys.exit()

  # testing application to landcover

  if label=='ecosg-emep':
    ifile= f'{tdir}/Data_Geo/EMEP_files/landcover_ecosg4emep_0p5_v1.nc'
    matching = [ 'Tr', ]
    shortstrs = {'DUMMY':'DUMMY'}

  elif label=='ifs':
    ifile= f'{tdir}/Data_IFS/scripts_IFS/IFS4emep_0p5.nc'
    matching = 'trees forest'.split()
    shortstrs = {'_Evergreen':'Ev','_Deciduous':'De' ,'_broadleaf':'Br',
       '_needleleaf':'Ne' ,'_Mixed_forest':'Mixed' ,'_trees':'Tr' }

  lcds=xr.open_dataset(ifile)
  lons=lcds.lon.values
  lats=lcds.lat.values
  areas=dict()

  vegs=[]
  ccs = set()

  for veg in lcds.keys():
    found=True
    for m in matching:
     if m not in veg:
       found=False
     else:
       found=True
       break
    if found: print('FOUND', veg, m)
    else:
      print('SKIP', veg)
      continue

    vegs.append(veg)
    vals = lcds[veg].values
    #--------------------------------------------
    areas[veg] = get_country_sums(lons,lats,vals,txt=veg,ccodes=codes) #,idbg=idbg,jdbg=jdbg)
    ifr=370;jfr=277
    #print('VEGAREA ', veg, vals[jfr,ifr], areas[veg]['FR'])
    #--------------------------------------------
    ccs = ( ccs | areas[veg].keys() )

  print('VEGES', vegs, vegs[0] )
  vegcodes = vegs.copy()
  #def shortenIFS(ifsveg):
  #  return ifsveg[6:].replace('_Evergreen','Ev').replace('_Deciduous','De').replace('_broadleaf','Br').replace('_needleleaf','Ne').replace('_Mixed_forest','Mixed').replace('_trees','Tr')

  def shorten(veg,pairs):
    newveg = veg
    for long, short in pairs.items():
      newveg = newveg.replace(long,short)
    return newveg

  if label=='ifs':
    vegrow = ''.join( [ f'{shorten(v[6:],shortstrs):9s}' for v in vegcodes ])
  else:
    vegrow = ''.join( [ f'{v:9s}' for v in vegcodes ])
  #vegrow = ''.join( [ f'{shorten(v[6:],shortstrs):9s}' for v in vegcodes ])

  with open(f'Table_{label}.txt','w') as tab:
    #print(f'{'Land':<17s} {vegrow}     Sum')
    tab.write(f'{'Land':<17s} {vegrow}     Sum\n')
    for cc in sorted(ccs):
      vegrow=''
      for v in vegs:
        if cc not in areas[v].keys():
           areas[v][cc] = 0.0
        vegrow += f'{0.001*areas[v][cc]:9.2f}'  # Now in 1000 km2
      sumveg = 0.001 * np.sum ( [areas[v][cc] for v in vegs ])
      #vegrow = ''.join( [ f'{areas[v][cc]:10.1f}' for v in vegs ])
      #print(f'{cc:<15s} {vegrow}  {sumveg:12.2f}')
      tab.write(f'{cc:<15s} {vegrow}  {sumveg:12.1f}\n')
   
   
   
