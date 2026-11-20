#!/usr/bin/env python3
import numpy as np
import pandas as pd
import sys
import emxbio.getMeganSpecs as gs
import os

# IMPORTANT: This Dave's location. Adjust as needed
megan3_file=f'{os.environ['HOME']}/bin/pyscripts/emxbio/Megan3_EFv240120.csv'
assert os.path.exists(megan3_file)

def getM3eps(specs,dbg=False):
   gspecs = gs.getMeganChemicals()
   
   ds=pd.read_csv(megan3_file)
   
   
   """ File has: 
   VegID,CommonName,GenusGroup,Family,GrowthForm,Type,EF1,EF2,EF3,EF4,EF5,EF6,EF7,EF8,EF9,EF10,EF11,EF12,EF13,EF14,EF15,EF16,EF17,EF18,EF19,LDF3,LDF4,LDF5,LDF6,References,Comment
   Abies alba,silver fir,AbiesIso2,Pinaceae,Ntr,species,8,0.003,0.2,0.2,0.05,0.2,0.03,0.05,0.09,0.06,1.6,0.4,0.7,0.4,1.5,0.1,0.2,0.04,1,0.5,0.8,0.3,0.4,,

     where: 
       EF1=Isop = row[6]
       EF2=MBO
       EF3..EF7 = MT = row[7..11]
       EF8 = NO
       EF9,10 = SQT
   See also notes at end

    EF has units nmole/m2(leaf)/s; we want ug/g(leaf)/h
                 nmol->mol   MW      g->ug /  SLW  *  hr  
    e.g. isop2ug =  1.0e-9 * 68.0 *  1.0e6 /  100  * 3600
   """

   # specific leaf weight, defaults for Megan ("mostly")
   slw = dict(Ntr=150.0,Btr=100.0,Shrub=175.0,Herb=50.0, Unknown=100.0) # Unknown included Q. petr
   #LAIstd = 5.0 # Megan 3, not needed though

   print(f'{"VegID":<40s} {"pft":<8s}  {"Is":>10s} {"mtl":>10s} {"mtp":>10s} {"mt":>10s} {"sqt/mt(mass)":>10s}')

   for n, row in ds.iterrows():
     #for tree in specs:
     #  if dbg: print(tree, row.VegID, tree in row.VegID)
     #  if tree in row.VegID:

     if all(x in row.VegID for x in specs):

         pft = row.GrowthForm  # e.g. Ntr or Btr
         #D = LAIstd * slw[pft]
         isop2ug =  1.0e-9 * 68.0 *  1.0e6 / slw[pft] * 3600
         mt2ug   =  1.0e-9 * 136.0 * 1.0e6 / slw[pft] * 3600

         xmt  = row[8:13]  # monoterpenes, excludes MBO (C5H12O)

         ldf = np.ones(len(xmt))  # light dependent factors
         ldf[0] = row.LDF3 # apin
         ldf[1] = row.LDF4
         ldf[2] = row.LDF5
         ldf[3] = row.LDF6
         mt  = np.sum( xmt)

         if dbg:
           for nn in range(1,12):
             ef = f"EF{nn}"
             print(f"{tree:<12s}  {nn:02d} {gspecs[nn][:10]:<12s} {row[ef]:8.3f}  {mt:12.3f}")
           sys.exit()

         mtp = np.sum( xmt*ldf )       # pool emissions
         mtl = np.sum( xmt*(1-ldf) )   # light-dep emissions
         sqt = np.sum(row[6+9:6+12])

        # sqt/mt ratio based upon nmol, so just scale with 1.5 for mass-based ratio
         print(f'{row.VegID:<40s} {pft:<8s}  {isop2ug*row.EF1:10.2f}'
               f'{mt2ug*mtl:10.2f} {mt2ug*mtp:10.2f} {mt2ug*mt:10.2f} {1.5*sqt/mt:10.2f}')


if __name__ == '__main__':
   import sys
   usage = """
      getMegan3_EPs.py returns biomass-bsed emission factors (ug/gdw/h) for pattern provided

      e.g. getMegan3_EPs.py Sali
       => VegID         pft            Is     mtl     mtp         mt    sqt/mt(mass-ratio)
          Salicaceae    Unknown     90.58    0.71    1.15       1.86       8.05
          Salix         Btr         90.58    0.71    1.15       1.86       8.05
          .... etc

      or getMegan3_EPs.py "Quercus il" gives Quercus ilex and Quercus ilicifoilia


   """

   if len(sys.argv) > 1:
      specs = sys.argv[1:]

   else:
     # Just some examples
     cf='Abies alba,Picea abies,Picea sitchensis'.split(",")
     oaks = 'Quercus petraea,Quercus pubescens,Quercus robur,Quercus cerris,Quercus ilex'.split(",")
     #pines='Pinus halepensis,Pinus pinaster,Pinus ponderosa,Pinus pinea,Pinus sylvestris'.split(",")
     #juni='Juniperus'.split()
     specs=cf+oaks

   print('SPECS:', specs)
   getM3eps(specs)

   if len(sys.argv) == 1: print(usage)


"""
From Alex, 2025-12-06

MEGAN EF and LDF file
The emission factors (EF, nmol m-2 s-1) is the emission rate at conditions of 30C and 1000 micromoles m-2 s-1 of PPFD). The 19 MEGAN3.2 comopund categories (see list below) are referred to as EF1 …. EF19

The Light Dependence Factor (LDF, unitless) is the fraction of emissions that follow the light dependent algorithm (instead of the light independent algorithm). This factor is constant for most compound categories but can vary for four of them (categories 3 to 6) and so the ability of specific LDF3, LDF4 , LDF5 and LDF6 are included in MEGAN3.   

MEGAN V3.2 COMPOUND CATEGORIES
Category 1. Isoprene
Category 2. Methyl butenol
Category 3. a-pinene
Category 4. Trienes (monoterpenes with 3 double bonds): myrcene, all ocimenes
Category 5. monoterpene 1: b-pinene, camphene, 3-carene, sabinene, terpineols, terpinyl acetates, other MT (except oxygenated or aromatic) 
Category 6. monoterpene 2: limonenes, phellandrenes, terpinenes, terpinolene, verbenene 
Category 7. Oxygenated and aromatic monoterpenes: aromatic (e.g., cymenes, cymenenes) and oxygenated (except those in category 5): camphor, linalool, bornyl acetate, thujones, cineoles, myrtenals, fenchones, ionones, ipsenols, coniferyl alcohol, santene, borneol, estragole, piperitone
Category 8. Nitric oxide
Category 9. Reactive sesquiterpenes: acoradienes, bergamotenes, bisabolenes, cadinenes, calarenes, caryophyllenes, elemenes, farnescenes, germacrenes, humulenes, muurolenes, nerolidols, patchoulenes, selinenes, all other sesquiterpenes 
Category 10. Other sesquiterpenes and large VOC: aromadendrenes, bourbonenes, cadinols, cedrenes, cedrols, copaenes, cubebenes, gurjunenes, isolongifolenes, kaurenes (and other diterpenes), longicyclenes, longifolenes, longipinenes, salates (e.g. homosalate, ethyl hexyl salate), thujopsenes, vlangenes, zingiberenes, all other compounds with molecular weight equal to or greater than 204 g/mol
Category 11. Methanol
Category 12. Acetone
Category 13. ethanol, acetaldehyde
Category 14. formic acid, acetic acid, pyruvic and other light (< C6) organic acids
Category 15. C2 to C4 alkanes and alkenes: ethane, ethene, propanes, propenes, butanes, butenes
Category 16. Oxidation products: formaldehyde, pentanal, heptanal, methyl heptenone, decanal, octanala, nonanal, oxopentanal, nonenal, octenal, geranyl acetone, neryl acetone  
Category 17.  Stress compounds: Hexanal, guiacol, eugenol, phenylacetaldehyde, anisole, ethyl cinnamate, cinnamaldehyde, cinnamic acid, jasmone, chavicol, salicylaldehyde, p-courmic acid, linalool oxides, dimethyl nonatriene, trimethyl nonatriene, 1-pentanol, benzene, hydrogen cyanide, isobutyronitrile, methacrolein, methyl vinyl ketone, methyl acetate, methyl benzoate, safrole, 3-pentanone, acetophenone, benzyl alcohol, benzaldehyde, toluene, phenol, pentenes, hexanols, methyl salicylate, benzyl benzoate, benzyl acetate, hexenals, methylthiophene, pentenols, hexenols, methyl furans, methyl jasmonate, xylenes, pentenols, hexenals, indole, heptadecane, hexenyl butyrate, methylbutanenitrile.
Category 18. Other BVOC: , methane, methyl bromide, methyl chloride, methyl iodide, methyl mercaptan, octenol, octanol,  carbon disulfide, dimethyl sulfide, butanone, skatole, napthalene, pentane, heptanone, hexane, dodecene, decane, heptane, carbonyl sulfide, methylbutenols, dimethyl disulfide, undecane, tetradecene, diallyl disulfide, propenyl propyl disulfide, methyl propenyl disulfide, hydrogen sulfide
Category 19. Carbon monoxide

"""
