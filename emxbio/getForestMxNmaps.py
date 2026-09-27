#!/usr/bin/env python3
""" 
  Reads JRC maps (in PS projection)
  uses moving YxX average of the PS grid cells

  Provides, eg
    treefracs['BDLF']['que']['robu'] as a fraction of que
    treefracs['BDLF']['que']         as a fraction of BDLF
    treefracs['BDLF']['que']['Total'] as a fraction of BDLF
    treefracs['BDLF']['Total']        as a fraction of BDLF

  Some notes:

  JRC: D_Qmaps have fractions of grid/forest with no reference to total BDLF or NDLF,
        thus we can't get absolute magnitudes. (The script mk.sumIJtest reports a
        total percentage fraction of 22.5 for one i,j. Also has 100% for SNL, GR, CR

  Skjoth: has similar situation

  Need to make weighted averages of % maps 
  Use /home/davids/Work/LANDUSE/EMEP_files/Landuse_PS_5km_LC.nc
  OOOPS .... change of mind. No need to use EMEP
"""
import copy
import glob 
import numpy as np
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
import scipy.ndimage as snd
import emxbio.rdMasterVegTable as rdveg
import emxplots.plotmap as pm
import emxplots.plot2maps as p2

dtxt="fmaps:"
SMALLFRAC = 1.0e-6
   
ii=72; jj=87  # Northern Nor/Swe - hihj Eiso_BDLF
ii=89; jj=81  # FInland Eiso_BDLF
jj=50; ii=136 # debug below
jj=47; ii= 96 # France
jj=82; ii= 84 # Sweden
ixmax = 98; iymax = 38 # loc of max DF iso

def nicevals(x):
  """  Crude clean-up. but had lots of trouble with tiny +/- values """
  x =np.clip(x,a_min=0.0,a_max=None)
  x = np.where(x>SMALLFRAC, x,0.0)
  return x

hdir='/home/davids'
ddir=f'{hdir}/Data'
tdir=f'{hdir}/Work/LANDUSE/BVOC/BVOC_2026'
src = 'jrc'
if src == 'jrc':
  treedir=f'{hdir}/Work/LANDUSE/SEI_JRC_dec2004/D_Qmaps'


def get_tree_fracs(ftypes= 'BDLF NDLF'.split(),
   #sizey=5,sizex=10, # for sizes of smoothing grid, in PS50
   sizey=2,sizex=3, dbgGenus=None,dbg=False ):
   """ Step 1: get PS to LL coordiates
       #OLD dsxy=pd.read_table(f'{tdir}/xyll_from_emepmet.dat',delim_whitespace=True,comment='#')
       ix   iy    lat           lon
       1    1    33.72468948   308.70999146
       NEW: head EMEPmodelgridarea.txt , so nothing from 1-35, 1-11
         ix iy  Area(km2)    Long   Lat
        36  12  1953.8383789   -35.6744995  40.6476746
        36  13  1966.3502197   -35.7084274  41.0454826
   """
   dtxt='getTreeFracs:'
   grid_dat = dict()
   dsxy=pd.read_table(f'{ddir}/EMEPmodelgridarea.txt',delim_whitespace=True) # ,comment='#')
   nx = dsxy.ix.max()  # 170
   ny = dsxy.iy.max()  # 133
   #grid_dat['lat2d']   = np.zeros([ny,nx])
   #grid_dat['lon2d']   = np.zeros([ny,nx])
   #grid_dat['area_m2'] = np.zeros([ny,nx])
   #grid_dat['BDLF']    = np.zeros([ny,nx])
   #grid_dat['NDLF']    = np.zeros([ny,nx])
   #grid_dat['Forest']  = np.zeros([ny,nx])
   #grid_dat['npts']    = np.zeros([ny,nx])


   """========== Read MasterVegTable (Oderbolz+EMEP tab for EFs =======================================
   Latin Name;Common Name;D-O;LAI;Type;ISOP-O;MTS-O;MTP-O;SQT-O;OVOC-O;;SLW-O;;E-Code;Species;Common_name;D-E;ISOP-E;MTP-E;MTL-E;D-O/D-E;Comment;SLW-EO
   Abies alba;White ﬁr;1200;5;3;1;0.5;1;0.1;2;;240;;ENF;abi_alba;Silver_fir......;1200;0;0;1;1.0;;240
   
     => e.g. vegtab[s][xx] for xx in LAI laifac pft D Dlai5, uggh_Is
   """
   vegtab    = rdveg.read_MasterVegTable()
   
   # ========== Qmaps ===========================================================
   
   psdat = dict()  # polar stereo data
   pft_types = 'ENF DNF MNF DBF EBF'.split()
   outfracs = dict()
   
   ftot = np.zeros([ny,nx])
   for ftype in ftypes:
     psdat[ftype] = dict()
     psdat[ftype]['Specs'] = []
     psdat[ftype]['Total'] = np.zeros([ny,nx])
     psdat[ftype]['Npts']  = np.zeros([ny,nx])
   
   # Read maps and calculate average EFs. Strange files were Q-eri_... , empty
   # Q-lau-nobi and Q-not_class. Added some safety tests below
   
   jj=iymax; ii= ixmax # Sweden
   
   nvalid = 0
   notvalid = 0
   # SPEC LOOP ---------------------------------------------------------------
   for spec in vegtab.keys():  # abi_alba, ...
   
      if 'EMEP' in spec:     continue   # skip Russia and Ukraine?
      if 'not_clas' in spec:     continue   # skip mixed forest TEST  ************* NOT CLASSIF
      if vegtab[spec]['NotJRC']: continue  # Not in JRC files
   
      ifile= f'{treedir}/Q-{spec}.out'
      if not os.path.exists(ifile):
        print(f'MISSING {ifile}')   # e.g. SNL, C4G...
        continue
   
      ds=pd.read_table(ifile,delim_whitespace=True,
         names=['ix','iy','frac'],dtype={'ix':int,'iy':int,'frac':float})
   
      pft= vegtab[spec]['pft']  # DBF, EBF, MNF or ENF
      genus, sname = spec.split('_')  # abi, alba
      if pft == 'EBF' or pft == 'DBF': ftype = 'BDLF'
      if pft == 'ENF' or pft == 'MNF' or pft == 'DNF': ftype = 'NDLF'
      assert pft not in ftypes,f"MISSING FTYPE {pft}, {ftype}, {ftypes}"
      if dbg: print(dtxt+'INP', spec, genus, sname, pft, ftype, len(ds))
      if len(ds) < 3:
         print(dtxt, 'TOO FEW', spec, len(ds) ) # lau, eri, ...
         continue  # exludes lau, eri, 
      if ftype not in ftypes: continue

      if dbgGenus is not None and genus != dbgGenus: continue
   
      for n in  range(len(ds)):

        ix   = ds.ix[n] - 1
        iy   = ds.iy[n] - 1
        if ix < 35:       continue #Some files had odd values at 33, 132
        if iy < 10:       continue # odd values at 83, 2
   
        frac = 0.01 * ds.frac[n]  
        if frac < SMALLFRAC: continue

        #grid_dat[ftype][iy,ix]  += frac
        #grid_dat['npts'][iy,ix] += 1
        if n==0 and (spec not in psdat[ftype]['Specs']): psdat[ftype]['Specs'].append(spec)
        psdat[ftype]['Npts'][iy,ix] += 1
   
        if genus not in psdat[ftype].keys():
          psdat[ftype][genus] = dict()
          #psdat[ftype][genus]['Total'] = np.zeros([ny,nx])
   
        if sname not in psdat[ftype][genus].keys():
          psdat[ftype][genus][sname] = np.zeros([ny,nx])
   
        psdat[ftype][genus][sname][iy,ix]   += frac
   
      # ------------- smoothing  start
      xveg = psdat[ftype][genus][sname].copy()
      psdat[ftype][genus][sname] = snd.generic_filter(psdat[ftype][genus][sname],
                                   np.nanmean, size=(sizey,sizex),mode='nearest')
      # ------------- smoothing  end
      # add totals after smoothing:
      # psdat[ftype][genus]['Total'] += psdat[ftype][genus][sname]
      psdat[ftype]['Total']        += psdat[ftype][genus][sname]
   
      if xveg[jj,ii] > SMALLFRAC:
        print(f"{dtxt}PSdat {ftype} {genus} {sname:>4s}"
            f" {xveg[jj,ii]:12.7f}"
            f" {psdat[ftype][genus][sname][jj,ii]:12.7f}"
            #f" {psdat[ftype][genus]['Total'][jj,ii]:12.7f}"
            f" sum{ftype}={psdat[ftype]['Total'][jj,ii]:12.7f}" )

   # END SPEC LOOP ------------------------------------------------------------

   #pm.plotmap(psdat['pic']['abie'],'pic_abi')
   # MAX MIN ij  31-147, 11-132
   # MAX MIN ij  71-147, 11-132 after ix=35 correction
   # domain is -169 to 32E,  34N to 82N. -169 also near 82N
   # =>    -17.1 to 47.7E;  25.04 to 73.4 N
   
   # ===============================================================================
   # Getting fractions. We keep genus as fraction of ftype, and calculate spec as fraction of genus
   # Apply filter which smoothes, also over nan
   # ===============================================================================
   
   
   # -------
   pstot  = psdat['BDLF']['Total'] + psdat['NDLF']['Total']  
   # -------
   nodata_mask=( pstot< SMALLFRAC )

   print('SUMS', pstot[jj,ii])

  # Make fractions per ftype and genus category, and mask for cells with any forest:
  #--------------------------------

   for ftype in ftypes:

     psfrac = copy.deepcopy(psdat[ftype])
     print('PSFRAC', psfrac.keys()) #  'Total', 'ace', 'aln',...
   
     ftot = psfrac['Total'].copy() # simple np array
     psfrac['Total'] = np.zeros([ny,nx])  # RESET!
     print('PSTOT ', ftype, ftot[jj,ii])
     sum_ftype =  0.0
     nf = 0

     for genus in psfrac.keys(): # abi ace..., exclude Total

       if genus=='Total' or genus == 'Npts' or genus == 'Specs' : continue
       #print('GG', ftype, genus)
       psfrac[genus]['Total'] = np.zeros([ny,nx])

       #print('SSS', ftype, genus, psfrac[genus].keys() )

       for sname in psfrac[genus].keys(): # now exclude Total
         if sname=='Total': continue
         """ 
             #psfrac[ftype][genus] = np.divide(gtot, sumf,where=gtot>0.0,out=np.zeros_like(gtot))
             Gave warnings: AI says:
             The where parameter only controls where the division
             is performed — it doesn't prevent NumPy from attempting
             the division at all locations. Even though you specify
             where=gtot>0.0, NumPy still computes gtot / sumf for all
             elements before applying the mask. When sumf contains zeros
             (and those positions don't satisfy gtot>0.0), you get the
             divide-by-zero warning. Could also say where
             (gtot>0.0 & (and?) ftot!=0) in 1 line. Suggests explicit:
         """
         mask = ftot > 0.0
         psfrac[genus][sname][mask]    = psfrac[genus][sname][mask]/ ftot[mask] # eg Frac Que ilex of BDLF
         psfrac[genus]['Total'][mask] += psfrac[genus][sname][mask]          # eg Frac Que in BDLF
         psfrac['Total'][mask]        += psfrac[genus][sname][mask]          # eg Frac Que in BDLF
         # ----------------------------------------
         xveg = psfrac[genus][sname]
         psfrac[genus][sname][nodata_mask] = 0.0

         dbg = ftot[jj,ii] > 1.0e-6 and xveg[jj,ii] > 1.0e-6
         if dbg:

            if nf==0: print(f"GEN   ftyp gen spec     psDatTot      psFracTot"
                            f"    psDatSnam    psFracSnam   psFracTot    sum_ftype")
            nf += 1

            if sname != 'Total':
               sum_ftype += psfrac[genus][sname][jj,ii]

            print(f"GEN   {ftype} {genus:<5s} {sname:<5s}"
                       f" {psdat[ftype]['Total'][jj,ii]:12.7f}"
                       f" {psfrac[genus]['Total'][jj,ii]:12.7f}"
                       f" {psdat[ftype][genus][sname][jj,ii]:12.7f}"
                       f" {psfrac[genus][sname][jj,ii]:12.7f}"
                       f" {psfrac['Total'][jj,ii]:12.7f}"
                       f" {sum_ftype:12.7f}") # should be 1.0
   
         #if np.max(xxveg)>1.0:
         #  jj, ii = np.unravel_index(xveg.argmax(),xveg.shape)  # 53, 134, as above
         #  print(f"DIVDBG-A {jj} {ii}  {ftot[jj,ii]} {xveg[jj,ii]}"
         #         f" {psdat[ftype][genus][sname][jj,ii]}")

       psfrac[genus]['Total'][nodata_mask] = np.nan
       #SNAME

#     if dbg: print(f"ENDGEN  {ftype} "
#                       f" {psdat[ftype]['Total'][jj,ii]:12.7f}"
#                       f" {psfrac[ftype]['Total'][jj,ii]:12.7f}"
     #G
     outfracs[ftype] = copy.deepcopy(psfrac)
     print(dtxt, 'OUTG', ftype,  outfracs[ftype]['Total'][jj,ii], psfrac['Total'][jj,ii] )

   print(dtxt, 'OUTSUMS', outfracs['BDLF']['Total'][jj,ii],
                    outfracs['NDLF']['Total'][jj,ii],
                    outfracs['BDLF']['Total'][jj,ii] +
                    outfracs['NDLF']['Total'][jj,ii])

   return outfracs
   
if __name__ == '__main__':

  #treefracs =  get_tree_fracs(ftypes=['NDLF'],dbgGenus='pic')

  treefracs =  get_tree_fracs()
  #pm.plotmap(treefracs['BDLF']['que']['robu'],'Qrob')

  ii=ixmax; jj=iymax
  ii=35+35; jj=30+11   # UK?

  for f in 'BDLF NDLF'.split():
    print( f, list( treefracs[f].keys()) )
    #sys.exit()

    if  treefracs[f]['Total'][jj,ii] < SMALLFRAC: continue
    print(f"FINTOTS: {f}: {treefracs[f]['Total'][jj,ii]:12.7f} max: {np.max(treefracs[f]['Total']):12.7f}")

    print(f"FIN   ftyp gen   spec      fracGenus    fracSpec")
    for genus in treefracs[f].keys():
      if genus == 'Total': continue
      for sname in treefracs[f][genus]:
        if sname == 'Total': continue
        if  treefracs[f][genus]['Total'][jj,ii] > SMALLFRAC:
            print(f"FIN   {f} {genus} {sname:>6s}"
                  f" {treefracs[f][genus]['Total'][jj,ii]:12.7f}"
                  f" {treefracs[f][genus][sname][jj,ii]:12.7f}")

  print(f"ENDTOTS: {f}: "
        f"{treefracs['BDLF']['Total'][jj,ii]:12.7f} "
        f"{treefracs['NDLF']['Total'][jj,ii]:12.7f} "
        f"{treefracs['BDLF']['Total'][jj,ii]+treefracs['NDLF']['Total'][jj,ii]:12.7f} ")
   
