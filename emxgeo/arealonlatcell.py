#!/usr/bin/env python3
# From: http://badc.nerc.ac.uk/help/coordinates/cell-surf-area.html
#See also (for polygon areas)
#https://stackoverflow.com/questions/4681737/how-to-calculate-the-area-of-a-polygon-on-the-earths-surface-using-python
# Note, earlier version used simpler R=6371, later uses 
import math
from math import pi, log, sqrt,atanh
from numpy import pi,sin, sqrt

R         = 6371.0       #! km
EARTH_RAD = 6378.1370    # earth equatorial radius, =a, WGS-84
R2 = R*R
RAD2= EARTH_RAD*EARTH_RAD
deg2Rad = pi/180.0

##def AreaLonLatCell(lon1,lon2,lat1,lat2):

def km2_areaLonLatCell(clat,dLat,dLon): 
  """ area matches calculation based on spherical cap, e.g.
      http://mathforum.org/library/drmath/view/63767.html
      Also uses WGS-84 R """
  assert clat> -90.0 and clat<90,'emxgeo: Impossible lat %f' % clat
  drLon = dLon*deg2Rad
  rLat1 = (clat-0.5*dLat)*deg2Rad
  rLat2 = (clat+0.5*dLat)*deg2Rad
  S = RAD2*drLon*(sin(rLat2)-sin(rLat1))  # ie uses WGS-84
  return S

def km2_areaLatCell(clat,dll): 
  """ area matches calculation based on spherical cap, e.g.
      http://mathforum.org/library/drmath/view/63767.html
      Also uses WGS-84 R """

  assert clat> -90.0 and clat<90,'emxgeo: Impossible lat %f' % clat
  drLon = dll*deg2Rad
  rLat1 = (clat-0.5*dll)*deg2Rad
  rLat2 = (clat+0.5*dll)*deg2Rad
  S = RAD2*drLon*(sin(rLat2)-sin(rLat1))  # ie uses WGS-84
  return S

def km2_areaLonLatCellX(clat,dLat,dLon): 
  """ area matches calculation based on spherical cap, e.g.
      http://mathforum.org/library/drmath/view/63767.html
      Also uses WGS-84 R """
  drLon = dLon*deg2Rad
  rLat1 = (clat-0.5*dLat)*deg2Rad
  rLat2 = (clat+0.5*dLat)*deg2Rad
  S = R2*drLon*(sin(rLat2)-sin(rLat1))
  return S


def km2_AreaLonLatCell(clat,dll): # centres
#  #R = 6371.0  ! km
  #dLon = (lon2-lon1)*deg2Rad
  drLon = dll*deg2Rad
  rLat1 = (clat-0.5*dll)*deg2Rad
  rLat2 = (clat+0.5*dll)*deg2Rad
  S = R*R*drLon*(sin(rLat2)-sin(rLat1))
  #print rLat1, rLat2, S 
  return S

def km2_areaLonLat_of_wgs84pixel(clat,dLat,dLon): 
    """ uses RGS84 pixel calc, but accounts for unequal dlat, dlon """
    km2pixel=km2_area_of_wgs84pixel(clat,dLat)
    return dLon/dLat * km2pixel  # simple scale

def km2_area_of_wgs84pixel(center_lat, pixel_size): #DS re-ordered, center_lat):
    """Calculate km^2 area of a wgs84 square pixel.

    Adapted from: https://gis.stackexchange.com/a/127327/2397
    see: https://gis.stackexchange.com/questions/127165/more-accurate-way-to-calculate-area-of-rasters  

    Parameters:
        pixel_size (float): length of side of pixel in degrees.
        center_lat (float): latitude of the center of the pixel. Note this
            value +/- half the `pixel-size` must not exceed 90/-90 degrees
            latitude or an invalid area will be calculated.

    Returns:
        Area of square pixel of side length `pixel_size` centered at
        `center_lat` in m^2.

    """
    a = 6378137  # meters
    b = 6356752.3142  # meters
    e = math.sqrt(1 - (b/a)**2)
    area_list = []
    for f in [center_lat+pixel_size/2, center_lat-pixel_size/2]:
        zm = 1 - e*math.sin(math.radians(f))
        zp = 1 + e*math.sin(math.radians(f))
        area_list.append(
            math.pi * b**2 * (
                math.log(zp/zm) / (2*e) +
                math.sin(math.radians(f)) / (zp*zm)))
    return 1.0e-6 * pixel_size / 360. * (area_list[0] - area_list[1]) #DS now km2

def km2_area_wgs84cell(center_lat, pixel_size): #DS re-ordered, center_lat):
    """Calculate km^2 area of a wgs84 square pixel. As with area_of_pixel above
       but with atanh idea from same website

    Adapted from: https://gis.stackexchange.com/a/127327/2397

    Parameters:
        pixel_size (float): length of side of pixel in degrees.
        center_lat (float): latitude of the center of the pixel. Note this
            value +/- half the `pixel-size` must not exceed 90/-90 degrees
            latitude or an invalid area will be calculated.

    Returns:
        Area of square pixel of side length `pixel_size` centered at
        `center_lat` in km^2.

    """
    a = 6378137  # meters
    b = 6356752.3142  # meters
    e = math.sqrt(1 - (b/a)**2)
    area_list = []
    for f in [center_lat+pixel_size/2, center_lat-pixel_size/2]:
        zm = 1 - e*math.sin(math.radians(f))
        zp = 1 + e*math.sin(math.radians(f))
        area_list.append(
            math.pi * b**2 * (
                2*atanh(e*sin(math.radians(f)))  / (2*e) +
                #math.log(zp/zm) / (2*e) +
                math.sin(math.radians(f)) / (zp*zm)))
    return 1.0e-6 * pixel_size / 360. * (area_list[0] - area_list[1]) #DS now km2

# from same site:
def areaf(f):
  """ area between equator and latitude f """
  a = 6378137.0 #  meters,
  b = 6356752.3142
  e= sqrt(1-(b/a)**2)  # eccentricity
  zm= 1 - e*sin(f)
  zp= 1 + e*sin(f)
  return pi*b**2 * ( log(zp/zm) / (2*e) + sun(f)/(zp*zm) )

#def area_of_pixel2(pixel_size,center_lat):
#  q=1.0/360  # where pixel_size in degrees

def globArea_km2():

  dll=0.5
  dLon = dLat = dll
  lats=[ -89.75 + i*dll for i in range(360) ] # do 0.5 deg 
  globArea=dict( areaLatCell=0.0, area_of_pixel2=0.0  )
  for clat in lats:
     globArea['areaLatCell']    += km2_areaLatCell(clat,dll)
     globArea['area_of_pixel2'] += km2_area_wgs84cell(clat,dll)
  for key, val in globArea.items():
    val *= 720 # 720 lon cells
    print("Glob area,%15s, %15.7e km2, %15.7e m2" % (  key, val, 1.0e6*val ))
  print("cf: http://www.jpz.se/Html_filer/wgs_84.html:", 510065621.724 )

def globArea_comp():
    """ from https://scipython.com/book/chapter-2-the-core-python-language-i/questions/problems/estimating-the-surface-area-of-the-earth/"""
    import math
    a = 6378137.0           # semi-major axis, m
    c = 6356752.314245      # semi-minor axis, m
    e2 = 1 - (c/a)**2
    e = math.sqrt(e2)
    A_WGS84 = 2*math.pi*a**2*(1 + (1-e2)/e * math.atanh(e))
    A_WGS84                 # 510065621724078.94  # fits _pixel v. well!
    r = 6371000.            # mean radius, m
    A_sphere = 4 * math.pi * r**2
    A_sphere                # 510064471909788.25 
    #(A_WGS84 - A_sphere)/A_WGS84 * 100 =  0.00022542477707103626,  ie 0.00023%
    print("Glob area from comp (km2): %15.7e %15.7e" % ( 1.0e-6*A_WGS84, 1.0e-6*A_sphere) ) 

if __name__ == '__main__' :
  dll = 1.0
  print("Area XX Oslo,%f deg"%dll , km2_AreaLonLatCell(60.0,1.0))
  print("Len-km  XX Oslo, %f deg"%dll ,         sqrt(km2_AreaLonLatCell(60.0,dll)) )
  print("AreaLonLatCell  Oslo,  %f"%dll ,       km2_AreaLonLatCell(60.0,dll))
  print("areaLonLatCell  Oslo,  %f"%dll ,       km2_areaLonLatCell(60.0,dll,dll))
  print("AreaLonLatCellX Oslo,  %f"%dll ,       km2_areaLonLatCellX(60.0,dll,dll))
  print("Area  SPole, %f deg"%dll ,             km2_AreaLonLatCell(-89.0,dll))
  print("Area  Sahara, 15degN res %f deg"%dll , km2_AreaLonLatCell(15.0,dll))
  print("area  Sahara, 15degN res %f deg"%dll , km2_areaLonLatCell(15.0,dll,dll))
  print("area  SaharaX, 15degN res %f deg"%dll, km2_areaLonLatCellX(15.0,dll,dll))
#fails  lats = [  10.0, 30.0, 85.0 ]
#  print("Area  SPole, 1deg" , AreaLonLatCell(lats,1.0))

# Borrowing ideas from 
# https://stackoverflow.com/questions/28372223/python-call-function-from-string#28372280
# and *val from https://note.nkmk.me/en/python-argument-expand/

# https://gis.stackexchange.com/questions/127165/more-accurate-way-to-calculate-area-of-rasters/127327#127327
# Latter suggests 3077.2300079129 km2 for equator, 13.6086152 for cell touching pole
# 30-min vals from equator to pole
  refs = [ 3077.2300079,3077.0019391,3076.5458145,3075.8616605,3074.9495164,3073.8094348,3072.4414813,3070.8457347,3069.0222870,3066.9712434,3064.6927222,3062.1868550,3059.4537865,3056.4936748,3053.3066912,3049.8930202,3046.2528597,3042.3864209,3038.2939285,3033.9756204,3029.4317480,3024.6625762,3019.6683833,3014.4494612,3009.0061153,3003.3386648,2997.4474422,2991.3327939,2984.9950800,2978.4346744,2971.6519646,2964.6473522,2957.4212526,2949.9740951,2942.3063230,2934.4183938,2926.3107788,2917.9839636,2909.4384482,2900.6747464,2891.6933866,2882.4949115,2873.0798782,2863.4488581,2853.6024374,2843.5412166,2833.2658109,2822.7768503,2812.0749792,2801.1608571,2790.0351582,2778.6985716,2767.1518013,2755.3955665,2743.4306011,2731.2576543,2718.8774905,2706.2908892,2693.4986451,2680.5015685,2667.3004848,2653.8962347,2640.2896746,2626.4816763,2612.4731271,2598.2649300,2583.8580035,2569.2532818,2554.4517149,2539.4542684,2524.2619238,2508.8756783,2493.2965451,2477.5255533,2461.5637477,2445.4121891,2429.0719545,2412.5441367,2395.8298444,2378.9302026,2361.8463521,2344.5794500,2327.1306692,2309.5011988,2291.6922441,2273.7050264,2255.5407830,2237.2007674,2218.6862492,2199.9985139,2181.1388633,2162.1086151,2142.9091030,2123.5416769,2104.0077025,2084.3085615,2064.4456516,2044.4203864,2024.2341953,2003.8885234,1983.3848318,1962.7245972,1941.9093120,1920.9404843,1899.8196375,1878.5483108,1857.1280585,1835.5604507,1813.8470724,1791.9895239,1769.9894206,1747.8483931,1725.5680867,1703.1501618,1680.5962932,1657.9081707,1635.0874985,1612.1359952,1589.0553936,1565.8474409,1542.5138984,1519.0565410,1495.4771578,1471.7775513,1447.9595378,1424.0249466,1399.9756206,1375.8134157,1351.5402005,1327.1578567,1302.6682785,1278.0733724,1253.3750574,1228.5752643,1203.6759360,1178.6790272,1153.5865040,1128.4003439,1103.1225355,1077.7550785,1052.2999830,1026.7592702,1001.1349711,975.42912705,949.64378940,923.78101904,897.84288636,871.83147097,845.74886152,819.59715539,793.37845851,767.09488512,740.74855748,714.34160569,687.87616739,661.35438752,634.77841811,608.15041795,581.47255240,554.74699308,527.97591765,501.16150951,474.30595754,447.41145586,420.48020351,393.51440422,366.51626611,339.48800143,312.43182627,285.34996030,258.24462644,231.11805066,203.97246162,176.81009042,149.63317034,122.44393648,95.244625564,68.037475592,40.824725575,13.608615243 ]

  clat=60.0; dLat=dLon=dll= 30.0/60
  clat=60.0; dLat=dLon=dll=1.0

  print("30' cell touching pole_")
  dLat=dLon=dll=0.5
  for clat in [ 89.975, 0.0 ]:
    functions = dict( km2_areaLonLatCell=(clat,dLat,dLon), km2_areaLatCell=(clat,dll), 
                    km2_areaLonLatCellX=(clat,dLat,dLon), km2_AreaLonLatCell=(clat,dll),
                    km2_area_of_wgs84pixel=(clat,dll),  km2_area_wgs84cell=(clat,dll) )
    for key, args in functions.items():
      print( f'AREA FUNC {clat:.3f} {key:<15s} {locals()[key](*args):14.5f} km2'  ) # % ( clat, key, locals()[key](*args) ) )

  for n, ref in enumerate(refs):
    clat = 0.25 + n*0.5
    print( f'REF {clat:6.3f}  {km2_area_of_wgs84pixel(clat,dll):12.5f}  {ref:12.5f}')

  
  x=globArea_km2()
  globArea_comp()
  
