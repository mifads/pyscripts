#!/usr/bin/env python3
"""
    Provides land-cover info and
    emission potentials from wet and dry areas, loosely based upon
    Steinkamp & Lawrence 2011 Table 5 (geometric mean) values.
"""
#  biomeYL95 = [ &                      ! Aw     Ad   LAI   CRF   season
#    biome_t(0, 'Grassland',             0.36, 2.65,  3.6,  0.64, 'Y') &! >30N
#   ,biome_t(0, 'Grassland/savanna',     0.36, 2.65,  4.0,  0.61, 'Y') &! Tropic
#   ,biome_t(0, 'Coniferous',            0.03, 0.40, 12.0,  0.39, 'Y') &! >30N
#   ,biome_t(0, 'Rain(conif?)',          0.03, 0.40,  8.0,  0.25, 'Y') &! > Tropic rain as conif
#   ,biome_t(0, 'Deciduous',             0.03, 0.40,  5.0,  0.55, 'F') &!> 30N why F?  
#   ,biome_t(0, 'Deciduous(rain?)',      0.03, 0.40,  8.0,  0.25, 'Y') &! Tropic rain as decid 
#   ,biome_t(0, 'Drought deciduous',     0.06, 0.22,  5.0,  0.41, 'W') &!
#   ,biome_t(0, 'Tundra',                0.05, 0.37,  2.0,  0.77, 'Y') &
#   ,biome_t(0, 'Woodland',              0.17, 1.44,  4.0,  0.64, 'F') & !> 30N
#   ,biome_t(0, 'Woodland',              0.17, 1.44,  4.0,  0.54, 'F') & !> 30N
#   ,biome_t(0, 'AgriculturalPlants',    0.17, 1.44,  4.0,  0.57, 'G') & !> 30N  Aw, Ad??
#   ,biome_t(0, 'AgriculturalPlants',    0.17, 1.44,  4.0,  0.57, 'Y') & ! Tropic Aw, Ad??
#  ]
#
# Didn't bother much with LAI or seasions here

biome_t= dict()

def biomeTab():
    """ geometric means of Aw and Ad (ngN/m2/s) """

      #biome= [ &                          ! Aw     Ad   LAI   CRF   season
    biome_t['CF'] = [                       1.66, 12.18,  4.0, 0.50, 'Y'] # !SL18
    biome_t['DF'] = [                       0.36,  2.39,  4.0, 0.50, 'Y'] # !SL16=15
    biome_t['NF'] = [                       1.66, 12.18,  4.0, 0.50, 'Y'] # !SL18
    biome_t['BF'] = [                       0.08,  0.62,  4.0, 0.50, 'S'] # !SL19
#A20    biome_t['TC'] = [                       0.44,  2.47,  4.0, 0.50, 'S'] # !SL20
#A20    biome_t['MC'] = [                       0.44,  2.47,  4.0, 0.50, 'S'] # !SL20
#A20    biome_t['RC'] = [                       0.44,  2.47,  4.0, 0.50, 'S'] # !SL20
#A20 should have been SL21, and zero emis for Ad:
    biome_t['TC'] = [                       0.44,  0.00,  4.0, 0.50, 'S'] # !SL21,A20, dry not used
    biome_t['MC'] = [                       0.44,  0.00,  4.0, 0.50, 'S'] # !SL21,A20, dry not used
    biome_t['RC'] = [                       0.44,  0.00,  4.0, 0.50, 'S'] # !SL21,A20, dry not used
    biome_t['SNL'] = [                      0.09,  0.65,  2.5, 0.50, 'S'] # ! SL6,7
    biome_t['GR'] = [                       0.42,  3.07,  2.5, 0.50, 'S'] # ! SL12=warm
    biome_t['MS'] = [                       0.09,  0.65,  2.5, 0.50, 'S'] # ! SL6,7
    biome_t['WE'] = [                       0.0,   0.0,   0.0, 0.50, '-'] # !
    biome_t['TU'] = [                       0.01,  0.05,  1.5, 0.50, 'S'] # ! SL8
    biome_t['DE:EMEP'] = [                   0.0,   0.0,   0.0, 0.50, '-'] # !
    biome_t['W:EMEP'] = [                    0.0,   0.0,   0.0, 0.50, '-'] # !
    biome_t['ICE:EMEP'] = [                  0.0,   0.0,   0.0, 0.50, '-'] # !
    biome_t['U:EMEP'] = [                    0.57,  0.0,   0.0, 0.50, '-'] # !SL22
#N3    biome_t['BARE:CLM'] = [                 0.0,   0.0,   0.0, 0.50, '-'] # !
    biome_t['BARE:CLM'] = [                 0.06,  0.43,   0.0, 0.50, '-'] # !SL5=barren.Not desert!
    biome_t['NDLF_EVGN_TMPT_TREE:CLM'] = [  1.66, 12.18,  4.0, 0.50, 'Y'] # !SL18
    biome_t['NDLF_EVGN_BORL_TREE:CLM'] = [  1.66, 12.18,  4.0, 0.50, 'Y'] # !SL18
    biome_t['NDLF_DECD_BORL_TREE:CLM'] = [  0.35,  2.35,  4.0, 0.50, 'S'] #& !SL17
    biome_t['BDLF_EVGN_TROP_TREE:CLM'] = [  0.44,  2.47,  4.0, 0.50, 'Y'] #!SL20
    biome_t['BDLF_EVGN_TMPT_TREE:CLM'] = [  0.36,  2.39,  4.0, 0.50, 'Y'] # !SL15
    biome_t['BDLF_DECD_TROP_TREE:CLM'] = [  0.08,  0.62,  4.0, 0.50, 'S'] # !SL19
    biome_t['BDLF_DECD_TMPT_TREE:CLM'] = [  0.36,  2.39,  4.0, 0.50, 'Y'] # !SL16=15
    biome_t['BDLF_DECD_BORL_TREE:CLM'] = [  0.36,  2.39,  4.0, 0.50, 'Y'] # !SL16=15
    biome_t['BDLF_EVGN_SHRB:CLM'] = [       0.84,  6.18,  1.5, 0.50, 'S'] # !Guess SL9,10
    biome_t['BDLF_DECD_TMPT_SHRB:CLM'] = [  0.09,  0.65,  2.5, 0.50, 'S'] # !SL6,7
#N3    biome_t['BDLF_DECD_BORL_SHRB:CLM'] = [  0.84,  6.18,  1.5, 0.50, 'S'] # !SL9,10=grass/savan? should be 8 maybe?
    biome_t['BDLF_DECD_BORL_SHRB:CLM'] = [  0.01,  0.05,  1.5, 0.50, 'S'] # !SL8 for Polar maybe? :-(
    biome_t['C3_ARCT_GRSS:CLM'] = [         0.84,  6.18,  1.5, 0.50, 'S'] # !SL9,10=cold
    biome_t['C3_NARC_GRSS:CLM'] = [         0.42,  3.07,  2.5, 0.50, 'S'] # !SL12=warm
    biome_t['C4_GRSS:CLM'] = [              0.42,  3.07,  2.5, 0.50, 'S'] # !SL12=warm
#N3    biome_t['CROP:CLM'] = [                 0.44,  2.47,  4.0, 0.50, 'S'] # !SL20
#BUG?    biome_t['CROP:CLM'] = [                 0.57,  0.57,  4.0, 0.50, 'S'] # !SL21, dry not used
    biome_t['CROP:CLM'] = [                 0.57,  0.0,  4.0, 0.50, 'S'] # !SL21, dry not used
    biome_t['IAM_CR'] = [               0.0,   0.0,   0.0, 0.50, '-'] # !
    biome_t['IAM_DF'] = [               0.0,   0.0,   0.0, 0.50, '-'] # !
    biome_t['IAM_MF'] = [               0.0,   0.0,   0.0, 0.50, '-'] # !
    biome_t['Wheat_Irrigated'] = [      0.0,   0.0,   0.0, 0.50, '-'] # !
    biome_t['Wheat_NonIrrig'] = [       0.0,   0.0,   0.0, 0.50, '-'] # !

    return biome_t


def SteinkampLawrenceTab():

 SL_t = dict()
#  Steinkap & Lawrence  (also ngN/m2/s)
# CRFs are loosely based upon YL and YanX, 30% for rainforest,
# 50% for other trees, 75% for sparser veg
#biome= [ &  ! Aw     Ad   LAI   CRF   season
 SL_t[0]  = [ 0.0,  0.0,   0.0, 0.00, 'Y', '00_water']                             
 SL_t[1]  = [ 0.0,  0.0,   0.0, 0.50, 'Y', '01_permanent_wetlands']  #CRF-Y
 SL_t[2]  = [ 0.0,  0.0,   0.0, 0.00, 'Y', '02_snow_and_ice']                      
 SL_t[3]  = [ 0.0,  0.0,   0.0, 0.00, 'Y', '03_barren_or_sparsely_vegetated_DE']   
 SL_t[4]  = [ 0.0,  0.0,   0.0, 0.00, 'Y', '04_Unclassified']
 SL_t[5]  = [0.06,  0.43,  0.0, 0.75, '-', '05_barren_or_sparsely_vegetated_ABC']  
 SL_t[6]  = [0.09,  0.65,  2.5, 0.75, 'S', '06_closed_shrubland']                  
 SL_t[7]  = [0.09,  0.65,  2.5, 0.75, 'S', '07_open_shrublands_ABC']               
 SL_t[8]  = [0.01,  0.05,  1.5, 0.75, 'S', '08_open_shrublands_DE']                
 SL_t[9]  = [0.84,  6.18,  1.5, 0.75, 'S', '09_grasslands_DE']                     
 SL_t[10] = [0.84,  6.18,  1.5, 0.75, 'S', '10_savannas_DE']                       
 SL_t[11] = [0.24,  1.76,  1.5, 0.75, 'S', '11_savannas_ABC']                      
 SL_t[12] = [0.42,  3.07,  2.5, 0.75, 'S', '12_grasslands_ABC']                    
 SL_t[13] = [0.62,  5.28,  2.5, 0.75, 'S', '13_woody_savannas']                    
 SL_t[14] = [0.03,  0.25,  2.5, 0.50, 'S', '14_mixed_forests']                     
 SL_t[15] = [0.36,  2.39,  4.0, 0.50, 'Y', '15_evergreen_broadleaf_forest_CDE']    
 SL_t[16] = [0.36,  2.39,  4.0, 0.50, 'Y', '16_deciduous_broadleaf_forest_CDE']    
 SL_t[17] = [0.35,  2.35,  4.0, 0.50, 'S', '17_deciduous_needleleaf_forest']       
 SL_t[18] = [1.66, 12.18,  4.0, 0.50, 'Y', '18_evergreen_needleleaf_forest']       
 SL_t[19] = [0.08,  0.62,  4.0, 0.50, 'S', '19_deciduous_broadleaf_forest_AB']     
 SL_t[20] = [0.44,  2.47,  4.0, 0.30, 'Y', '20_evergreen_broadleaf_forest_AB'] # =rainforest in SL
 SL_t[21] = [0.57,  0.0,   4.0, 0.75, 'S', '21_croplands']                         
 SL_t[22] = [0.57,  0.0,   0.1, 0.75, 'S', '22_urban_and_built-up']                
 SL_t[23] = [0.57,  0.0,   4.0, 0.75, 'S', '23_cropland_natural_vegetation_mosaic']
 return SL_t

def biome(lc):

   if len(biome_t) < 1:
     ini = biomeTab()
   assert lc in biome_t.keys(), 'Not in biome_t!! :'+lc
   b=dict()
   b['Aw'] = biome_t[lc][0]
   b['Ad'] = biome_t[lc][1]
   return b


# times Aw
if __name__ == '__main__':
  import sys
  tab = biomeTab()
  SLtab = SteinkampLawrenceTab()
 # y=biome('C4_GRSS:CLM')
 # print(y)
