#!/usr/bin/env python3
import pandas as pd
import sys
Olson="""
<p>There are actually 73 land types, not 74, in both the 1992 and 2001 
Olson land maps. The table below shows the translation between the Olson
 2001 and Olson 1992 land maps:
</p>
<pre>	Olson 2001				Olson 1992 	# in
LC #	Description		        	Equivalent      Dry deposition
==============================================================================
1	Urban					1		2
..
13	Wooded Wet Swamp			13		14
=>
LC;name;O92;Dep
1;Urban;1;2
2;Low Sparse Grassland;2;3

"""

def getOlsonCodes(idir,oDepWanted=False):
  """ not sure first if we wanted Olson1992 or DryDep code.
      but it is the Olson1992 we need. """
  
  ds=pd.read_csv(f'{idir}/OlsonLandTypes.csv',sep=';')
  olsonO92  = dict()
  if oDepWanted: olsonDep = dict()
  for n, row in ds.iterrows():
    nname= '_'.join( c for c in row.LCname.split() )
    olsonO92[int(row.O92)] = nname
    if oDepWanted: olsonDep[int(row.Dep)] = nname
  if oDepWanted:
    return olsonO92, olsonDep
  else:
    return olsonO92

if __name__ == '__main__':
  import os
  tdir='/lustre/storeB/users/davids/Data_Geo/OLSON_MAP'
  if 'ppi' not in  os.uname():
    tdir = '/home/davids' + tdir

  #o92, oDep = getOlsonCodes()
  o92 = getOlsonCodes(tdir)
