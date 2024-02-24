#!/usr/bin/env python3

# defaults, rv5.0
sectors_def=dict()
header='!                                           tf  h  spl'
sectors_def[1]  = [ 'GNFR_CAMS', 'GNFR_A',  'sec01',  1, 1,  1, 'Public Power', 'ALL', ]
sectors_def[2]  = [ 'GNFR_CAMS', 'GNFR_B',  'sec02',  2, 3,  2, 'Industry', 'ALL', ]
sectors_def[3]  = [ 'GNFR_CAMS', 'GNFR_C',  'sec03',  3, 2,  3, 'OtherStationaryComb', 'ALL', ]
sectors_def[4]  = [ 'GNFR_CAMS', 'GNFR_D',  'sec04',  4, 5,  4, 'Fugitive', 'ALL', ]
sectors_def[5]  = [ 'GNFR_CAMS', 'GNFR_E',  'sec05',  5, 2,  5, 'Solvents', 'ALL', ]
sectors_def[6]  = [ 'GNFR_CAMS', 'GNFR_F',  'sec06',  6, 2,  6, 'RoadTransport', 'ALL', ]
sectors_def[7]  = [ 'GNFR_CAMS', 'GNFR_G',  'sec07',  7, 8,  7, 'Shipping', 'ALL', ]
sectors_def[8]  = [ 'GNFR_CAMS', 'GNFR_H',  'sec08',  8, 7,  8, 'Aviation', 'ALL', ]
sectors_def[9]  = [ 'GNFR_CAMS', 'GNFR_I',  'sec09',  9, 2,  9, 'Offroad', 'ALL', ]
sectors_def[10] = [ 'GNFR_CAMS', 'GNFR_J', 'sec10', 10, 6, 10, 'Waste', 'ALL', ]
sectors_def[11] = [ 'GNFR_CAMS', 'GNFR_K', 'sec11', 11, 2, 11, 'AgriLivestock', 'ALL', ]
sectors_def[12] = [ 'GNFR_CAMS', 'GNFR_L', 'sec12', 12, 2, 12, 'AgriOther', 'ALL', ]
sectors_def[13] = [ 'GNFR_CAMS', 'GNFR_M', 'sec13', 13, 5, 13, 'Other', 'ALL', ]
sectors_def[14] = [ 'GNFR_CAMS', 'GNFR_A1','sec14', 14, 1,  1, 'PublicPower_Point', 'ALL', ]
sectors_def[15] = [ 'GNFR_CAMS', 'GNFR_A2','sec15', 15, 3,  1, 'PublicPower_Area', 'ALL', ]
sectors_def[16] = [ 'GNFR_CAMS', 'GNFR_F1','sec16', 16, 2, 16, 'RoadTransportExhaustGasoline', 'ALL', ]
sectors_def[17] = [ 'GNFR_CAMS', 'GNFR_F2','sec17', 17, 2, 17, 'RoadTransportExhaustDiesel', 'ALL', ]
sectors_def[18] = [ 'GNFR_CAMS', 'GNFR_F3','sec18', 18, 2, 18, 'RoadTransportExhaustLPGgas', 'ALL', ]
sectors_def[19] = [ 'GNFR_CAMS', 'GNFR_F4','sec19', 19, 2, 19, 'RoadTransportNonExhaustOther', 'ALL', ]

sectors_new=sectors_def.copy()

def swapsecs(old,orig,newgnfr,newtxt):
  sectors_new[old] = sectors_new[orig].copy()  # Cb replaces A1
  sectors_new[old][1] = newgnfr
  sectors_new[old][6] = newtxt
  return sectors_new

def print_sectors(label, secs):
  txtout=header+'\n'
  for i in range(1,1+len(secs)):
    s=secs[i]
    txtout += "SECTORS_ADD(%d) = '%s', '%s', 'sec%02d', %d, %d, %d, %s, %s, \n" % ( 
                        i,  label, s[1],         i, s[3], s[4], s[5], s[6], s[7]  )
  return txtout

def getsectors(style='default'):

  if style == 'default':

     return sectors_new

  elif style=='CAMEO':
    secs = swapsecs(14,3,'GNFR_Cb','BiomassBurning')
    secs = swapsecs(15,3,'GNFR_Cf','FossilFuel')
    secs = swapsecs(13,12,'GNFR_L2','AWB')         # L2(awb) replaces M (was zero)

  return secs


if __name__ == '__main__':

  secs=getsectors('CAMEO')
  txt=print_sectors('CAMEO',secs)
  print(txt)
