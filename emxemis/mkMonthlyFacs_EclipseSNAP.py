#!/usr/bin/env python3
import codetxt  # my: gets script name
readme="""
 (DO NOT EDIT THIS README. Generated by script!)

 README and data:

   %s

 Creates MonthlyFac files from ECLIPSE emissions. With keep_old = True the
 values are only created for countries which are not in the original emep
 MonthlyFac files (from Jun2012). With keep_old = False all factors are
 from ECLIPSE (labelled "pure"). Thus, we produce:

   Timefactors/MonthlyFacs_eclipse_V6b_snap_xJune2012
   (DEPRECATED!! SNAP10 was weird!)

   Timefactors/MonthlyFacs_eclipse_V6b_snap_pure
   Timefactors/MonthlyFacs_eclipse_V6b_snap_may2021
   
 ECLIPSE has agr, agr_NH3, awb, dom,ene, flr, ind, shp, slv, tra, wst
 but slv, tra, wst have 1.0 (/nmdays) only, and awb,flr,wst very irregular

 ECLIPSE factors only created for "robust" sectors 1, 2, 3,4, and 10. For
 10 (agr) the NH3 data are from ECLIPSE agr_NH3, otherwise from agr.

 MonthlyFacs look like, e.g.:
$head MonthlyFacs.nox 
1 10    0.781   0.841   0.841   0.960   1.080   1.199   1.199   1.199   1.080   1.080   0.900   0.841
1 02    1.931   1.651   1.313   0.759   0.624   0.602   0.621   0.621   0.602   0.661   0.910   1.705

 (DO NOT EDIT THIS README. Generated by script!)
""" %  codetxt.codetxt()
import glob
import matplotlib.pyplot as plt
import sys
import xarray as xr
import numpy as np
import os

# We will use:
DataDir='/home/davids/MDISKS/Nebula/Peter/work/Data/' # Dave's mounted version
workDir='/home/davids/Work/D_Emis/Timefactors/'       #  For output
eclipse_mfacs=DataDir+'ECLIPSE_V6a_monthly_pattern.nc'
eclipse_emis =DataDir+'Emis_ECLIPSEv6b/emis_ECLIPSEv6b_2015_05deg_noINTSHIP.nc'
orig_files=glob.glob(DataDir+'inputs_emepdefaults_Jun2012/MonthlyFac*')

out_dir=workDir+'MonthlyFacs_eclipse_V6b_snap_%s' # Will add label to output dir
keep_old=True
keep_old=False # True
if keep_old: odir= out_dir % 'xJun2012'
else: odir= out_dir % 'may2021' # 'pure'
os.makedirs(odir,exist_ok=True)

docFile=odir+'/README_Timefactors.txt'
#if not os.path.exists(docFile):
docs=open(docFile,'w')
docs.write(readme)
docs.close()
print('dir ', odir, docFile )
print(codetxt.codetxt())


#!) Grab current MonthlyFac files, get list of countries, and send contents as start of
#   new files. (We will append ECLIPSE data to these copies.)
cclist=[]
speclist=[]
fh=dict() # file handles, output files

for f in orig_files:
  base=os.path.basename(f)
  txt, poll = base.split('.')
  speclist.append(poll)
  fh[poll] = open('%s/MonthlyFacs.%s' % ( odir, poll ), 'w')
  with open(f) as file:
    for line in file:
      fields=line.split()
      if keep_old:
        cc=int(fields[0])
        if cc not in cclist: cclist.append(cc)
        fh[poll].write(line)
      #sec=int(fields[1])
      #y = [ float(x) for x in fields[2:] ]
      #print('SUM', poll,cc,sec, np.sum(y) )

# 2) Read in ECLIPSE monthly 

mfac2snap = dict(agr='10',dom='02',ene='01',ind='03') # Used sectors. Will add agr_NH3 below
snaps = list(mfac2snap.values())
snap2mf = dict()
for e, s in mfac2snap.items():
  snap2mf[s] = e
  print('eclipse snap', e, s )

ds=xr.open_dataset(eclipse_mfacs,decode_times=False)
print('KEYS ', ds.keys())
mds = ds[list(mfac2snap.keys()) + [ 'agr_NH3']] # only stuff we need, base of new output

# 3) Read in ECLIPSE emissions 

files=['../tmpDir/emis_ECLIPSEv6b_2010_05deg_noINTSHIP.nc']

#polls='ch4 co'.split() #  ec ecco ecfi nh3 nox oc occo ocfi pm10 pm25 remppm25 remppmco sox voc'.split()
i=380;j=280  # France
i=508;j=286  #  border grid witg 2 countries
#dbg=False # set true for extra output
jdbg=145;idbg=246 # S. America

polls='nox nh3'.split()  #  for MonthlyFac, we will copy nox to sox, voc etc.

basevars = 'NCodes Codes map_factor_i map_factor_j'.split()

ds= xr.open_dataset(eclipse_emis,decode_times=False)
lons=ds['lon'].values
lats=ds['lat'].values

codes=ds['Codes'].values[0,:,:,:].astype(int)
codelist = np.unique(codes)
ncodes=ds['NCodes'].values[0,:,:].astype(int)

ccmap=np.zeros([360,720])  # creates map of country codes; only for info

for poll in polls:
  mmEmis = dict()    # will be mmEmis[snap][cc]

  print('PRETEST ', poll,  snaps)
  for snap in snaps:  # '10', '02', '01', '03'

    #mmEmis[snap] = dict.fromkeys(codelist,np.ones(12))
    mmEmis[snap] = dict( (k,np.ones(12)) for k in codelist ) # See mkDictCheck

    vals=ds['%s_sec%s' % (poll,snap) ].values[0,:,:]
    fracs=ds['fractions_%s_sec%s' % (poll,snap) ].values[0,:,:,:]

    mfsec = snap2mf[snap]  # e.g. 10 to agr
    print('TEST ', poll,  snap, mfsec, vals[jdbg,idbg], np.max(fracs[:,jdbg,idbg]) )
    print(mfsec)
    #if poll=='nh3':print('TEST ', snap, mfsec)
    if mfsec == 'agr' and poll=='nh3':
        mfsec = 'agr_NH3'
        print('SWITCH ', snap, mfsec)
    monthly_facs=mds[mfsec].values # Each sums to 1.0

    memis=np.multiply(monthly_facs,vals)

    for j, lat in enumerate(lats):
      for i, lon in enumerate(lons):

        if vals[j,i] > 0:
          for n in range(ncodes[j,i]):
             cc=codes[n,j,i]
             if n==0: ccmap[j,i] = cc
             ccEmis = fracs[n,j,i] * memis[:,j,i]
             mmEmis[snap][cc] += ccEmis
             if j==jdbg and i==idbg: print('IJ', cc, snap, ccEmis[0], mmEmis[snap][cc][0])
              
     # Now, normalise and write out:

  if poll == 'nh3': 
    outpolls = [ 'nh3' ]
  else:
    outpolls = speclist.copy() # we will copy to sox, nox, voc etc.
    outpolls.remove('nh3')

  mmEmis['04'] =  mmEmis['03'].copy()
  for cc in codelist:
    if cc==0: continue # shipping?
    if cc in cclist: continue  #already done in emep files
    for snap in snaps+['04'] :
      mmSum =  np.sum(mmEmis[snap][cc])
      normedFac = 12 * mmEmis[snap][cc] /  mmSum
      if snap=='10': print('SNAP10',cc, poll, normedFac[11] )
      #print(poll, snap, cc,  mmSum, normedFac  )
      for p in outpolls:
        fh[p].write('%s %s '% (cc, snap) )
        for mm in range(12):
          fh[p].write('%8.3f' % normedFac[mm] )
        fh[p].write('\n')

  #plt.pcolormesh(ccmap)
  #plt.colorbar()
  #plt.show()
             
