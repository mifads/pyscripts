#!/usr/bin/env python3
#from openpyxl import load_workbook
import numpy as np
import pandas as pd
import sys
""" Reads xls file which contains:
 numid;network_name;station_id;station_name;station_country;station_type;
 station_type_of_area;station_lat;station_lon;
 station_alt;station_google_alt;station_etopo_relative_alt;
 station_population_density;station_max_population_density_5km;
 station_max_population_density_25km;station_nightlight_1km;
 station_nightlight_5km;station_max_nightlight_25km;station_htap_region;
 station_climatic_zone;station_dominant_landcover;
 station_landcover_description;station_nox_emissions;station_omi_no2_column;
 station_toar_category;data_capture-NH-Summer;mean-NH-Summer;
 daytime_avg-NH-Summer;avgdma8epax-NH-Summer;median-NH-Summer;p25-NH-Summer;
 p75-NH-Summer;p95-NH-Summer;p98-NH-Summer;dma8epax-NH-Summer;count

 NOTE: uses station file from Dave's disc. Sorry!
"""
toar='/home/davids/Data/TOAR/ReportData/AVG_summer_global_2008-2015_aggregated'
ifile=toar+'.xlsx'

# From http://www.pythonexcel.com/openpyxl.php but just shows cell be cell # access.
# data_only=True gets evaluated values, not formulii
#wb=load_workbook(filename=ifile,data_only=True)
#sheets=wb.get_sheet_names()  # gives list, here just 'Stage 1'
#s=wb['Sheet1']

defwanted = 'station_country station_id station_name station_lat station_lon station_alt station_google_alt station_etopo_relative_alt'.split()
#idlist=list(pp['station_id'])
#iloc=idlist.index('NO0015R')
#site=pp.iloc[iloc]
#defwanted = 'station_etopo_relative_alt station_lon'.split()
#pp=pd.read_excel(ifile,sheet_name=0)
#sites=list(pp['station_id'])
#iloc=sites.index('NO0015R')
#site=pp.iloc[iloc]
#print(pp.keys())
#print(defwanted)
#sys.exit()

def read_toar_file(wantedvars=defwanted,wantedland=[],wantedID=None,dbg=False):
  pp=pd.read_excel(ifile,sheet_name=0)
  sites=pp['station_name']
  country=pp['station_country']
  if wantedID is not None:
    assert len(wantedland)==0,'Cannot have wantedID and wantedland'
    idlist=list(pp['station_id'])
    #iloc=idlist.index(wantedID) if wantedID in idlist else 
    if wantedID in idlist:
      iloc=idlist.index(wantedID)
      site=pp.iloc[iloc]
    else:
      site='NotFound'
    return site

  for n, site in enumerate(sites):  #  range(len(pp)
    land= country[n]
     #if land == 'India' or land  == 'China': 
    if len(wantedland) > 0:  # 
      if land not in wantedland: continue
    for varname in wantedvars:
        val=pp[varname][n]
        if dbg: print('WANTED ',n, land, site, varname, type(val))
        if isinstance(val,str):
           if 'name' in varname: print('%-40s' % val,end='' )
           else: print('%-10s' % val,end='' )
        elif isinstance(val,(int,np.integer)):
           print('%8d' % val,end='' )
        elif isinstance(val,(float,np.float)):
          maxval=max(np.abs(pp[varname][:]))
          if maxval>999.0 : print('%8.1f' % val, end='') # likely altitude
          else : print('%8.3f' % val, end='') # likely altitude
        else:
          return val
          print('ERROR', varname, val, type(val))
          sys.exit('UNKNOWN TYPE'+varname)
    print()
    
if __name__ == '__main__':
 v=read_toar_file(wantedvars=defwanted,wantedland=['Norway']) # ,dbg=True)
 s=read_toar_file(wantedvars=defwanted,wantedID='NO0015R') # ,dbg=True)
 print('SITE:', s['station_name'], s['station_lat'])

#   cc=  s.cell(row=k,column=1).value 
#   site =  s.cell(row=k,column=2).value 
#ABC#   lat =  s.cell(row=k,column=5).value 
#ABC#   lon =  s.cell(row=k,column=6).value 
#ABC#   alt = -999
#ABC#   xlat =  s.cell(row=k,column=5).value 
#ABC#   alt =  s.cell(row=k,column=4).value 
#ABC#   out.write('%-20s  %8.3f %8.3f %8d\n' % ( cc+'_'+site, lon,  lat, alt))
#ABC
