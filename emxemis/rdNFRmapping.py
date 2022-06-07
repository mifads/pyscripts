#!/usr/bin/env python3
"""
Reads NFR sector mapping from latest (?) CEIP 
"""

def get_sec_mapping():
  """ Reads:
  'NACE Rev1.1 Eurostat', 'NACE Rev.2 SECTOR', 'NACE Rev.2 ACTIVITY',
         'SNAP', 'SNAP name', 'NFR19', 'NFR19 Longname', 'GNFR19',
         'CRF (2006 GLs)', 'CRF name', 'NFR14', 'NFR Longname', 'GNFR14',
         'NFR09', 'NFR09 Longname', 'NFR08', 'IPPC ', 'IPPC  name', 'E-PRTR',
         'E-PRTR name', 'GAINS/ RAINS (not fully complete)'
  """
  import numpy as np
  import pandas as pd
  
  idir='/home/davids/Work/D_Emis/NFR_SNAP_etc/'
  ds=pd.read_excel(idir+'06122019_conversiontablereportingcodes_.xlsx',
          sheet_name='NACE_SNAP_NFR_CRF_GAINS',header=1)
  
  sec_mapping=dict()
  
  for sec in 'K_AgriLivestock L_AgriOther'.split():
  
    sec_mapping[sec] = dict()
  
    dsX=ds[ds['GNFR19']==sec]
  
    nfr14list= dsX['NFR14'].unique()  # can be nan
  
    elems = [ str(i).replace(' ','') for i in nfr14list if isinstance(i,str) ]
    sec_mapping[sec]['nfr14s'] = elems.copy()
    if sec.startswith('K'):
     sec_mapping['tot'] =  elems.copy()
    else:
     sec_mapping['tot'] = np.unique( sec_mapping['tot'] + elems.copy()  )
  
  return sec_mapping

if __name__ == '__main__':

    secmaps = get_sec_mapping()
  
