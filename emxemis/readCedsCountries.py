#!/usr/bin/env python3
import numpy as np
from collections import OrderedDict as odict
import os
import pandas as pd
import sys


# CEDS country_mappin_DS.csv  (DS was oocalc csv export pga funny chars)
#Country Name,ISO Code,IEA Name,Aggregate Region,,
#Afghanistan,afg,Other Asia,Other Asia/Pacific,,
#Albania,alb,Albania,Europe,,

def get_ceds_countries():

   tdir=os.environ['HOME'] + '/Work/D_Emis/CEDS/'
   ceds=pd.read_csv('%s/Supplement/Data_Supplement/country_mapping_DS.csv' % tdir , delimiter=',')
   
   # Added _ for headers, so:
   ceds_iso3  = ceds['ISO Code'].values     # [ i.decode().upper() for i in ceds['ISO_Code'] ]
   ceds_names = ceds['Country Name'].values # [ i.decode() for i in ceds['Country_Name'] ]
   ceds_IEA = ceds['IEA Name']         #  [ i.decode() for i in ceds['IEA_Name'] ]
   ceds_Reg = ceds['Aggregate Region'] # [ i.decode() for i in ceds['Aggregate_Region'] ]

   return ceds_iso3, ceds_names

if __name__ == '__main__':

  iso3, names = get_ceds_countries()
  for cc, nam in zip( iso3, names):
    print( nam, cc )
   
