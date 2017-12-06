#!/usr/bin/env python3
"""
 EmepCdf contains:
   class:
      EmepFileClass - which defines objects with name,proj,x0, etc.
   methods:
      RdEmepCdf - reads EMEP cdf file, and figures out projection. 
                  returns : EmepFile (object), and values of a 
                  specified variable for the full period or
                  particular time-slices.
                  CHECK...
         grid  (2-d array) for one time-slice, 1st if not specified
         Pt    (1-d time array)

      getEmepVal(xPt,yPt,EmepCdf,minmax=False,dbg=False):
            gets the value at xPt, yPt from bi-linear interpolation
            of nearest grids. Returns best estimate and min and max
            of those grids. 

      printme()
  Access as e.g. EmepFile.name

  Usually called as module, but a quick test can be done to get values, e.g.

    EmepCdf.py -i /home/fred/somedir/test1_fullrun.nc  -v SURF_MAXO3
"""
import datetime
import netCDF4 as cdf
from numpy import maximum, vstack
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import time # for timing CPU
#Not used: import netcdftime # ... to play with dates:
# Own:
import get_emepcoords as coords

# ---------------------------------------------------------------------------#
class EmepFileClass(object):
  """ Class to hold info on EMEP file's projection and dimensions
  """
  def __init__(self,name=None,handle=None,varname=None,proj=None,lldim=None, \
      dimx=None,dimy=None,ntime=None):
    self.name=name
    self.handle=handle
    self.varname=varname
    self.proj=proj              # lonlat or PS so far
    self.lldim= int( lldim )    # is e.g. lat 1-D or 2-D
    self.dimx=dimx              # e.g. latitude, lat
    self.dimy=dimy
    self.ntime=int ( ntime )    # 1 so far, for fullrun

    self.x0=np.NaN  # will be left edge
    self.y0=np.NaN  # will be bottom edge
    self.xmax=np.NaN  # will be left edge
    self.ymax=np.NaN  # will be bottom edge
    self.dx=np.NaN  # will be left edge
    self.dy=np.NaN  # will be bottom edge
    self.xcoords=[]
    self.ycoords=[]
    self.yAscending=True  # True for S to N in y coords
    self.xRegular=True    #  Constant spacing in x
    self.yRegular=True    #  Constant spacing in y
    self.vals=np.array([])
    #self.ht=float( ht )

  def __repr__(self):
    return str(self.__class__) + ":" + str(self.__dict__)
   # return str(self.__dict__)
   # repr better than __str__ here, see e.g. 
   # http://stackoverflow.com/questions/1436703/difference-between-str-and-repr-in-python/2626364#2626364

  def printme(self):
     """ prints out summary of EmepFile f, excluding xcoords and ycoords """
     me='EmepFileClass: '
     f=self
     print(("="*78))
     print((me+"SUMMARY     ", f.name))
     print((me+"Variable    ", f.varname))
     print((me+"PROJ, dims  ", f.proj,  " : ", f.lldim, 'D ', f.dimx, f.dimy))
     print((me+"ntime       ", f.ntime))
     print((me+"XCOORDS     ", f.xcoords.min(), f.xcoords.max(), len(f.xcoords) ))
     print((me+"yCOORDS     ", f.ycoords.min(), f.ycoords.max(), len(f.ycoords), f.yAscending ))
     print((me+"x0 y0 dx dy reg? ", f.x0, f.y0, f.dx, f.dy, f.xRegular, f.yRegular ))
     print((me+"xmax, ymax  ", f.xmax, f.ymax))
     try:
       print((me+"min max vals", f.vals.min(), f.vals.max()))
     except:
       print(me+"min max vals NOT SET YET")
     print(("="*78))


#-----------------------------------------------------

def RdEmepCdf( ifile, var, getVals=True, tStep=None, 
        getijPts = [], getijPt=[ False, 0, 0 ], dbg=False ):
  """
    Reads emep-produced (or other?) netcdf files and returns values of 
    variable 'var' as EmepCdf.vals array, along with projection, ycoords, xcoords
    and number of dimensions. 
    If tStep is specified, vals is 2-d array for that time-step, otherwise
     vals contains all data for that variable.
    For lonlat projections, xcoords is usually longitude in degrees
    For PS     projections, xcoords is usually real, e.g. 1.0 -- 100.0

    This routine can return one time-slice of gridded data, or 
    time-series for one point --- OR FULL ...
  """

  dtxt='RdEmepCdf: '
  if( not os.path.isfile(ifile) ):
      print((dtxt+"File %s doesn't exist!"% ifile))
      sys.exit()

  ecdf = cdf.Dataset(ifile,'r',format='NETCDF4')
  
  proj='lonlat' # default
  if( 'longitude' in ecdf.dimensions ):
    dimx, dimy =( 'longitude', 'latitude')
  elif ( 'lon' in ecdf.dimensions ) :
    dimx, dimy =( 'lon', 'lat')
  elif ( 'i' in ecdf.dimensions ) :
    print((dtxt+'PS PROJ assumed for %s' % ifile))
    dimx, dimy =( 'i_EMEP', 'j_EMEP')
    proj='PS'
  elif ( 'x' in ecdf.dimensions ) :
    dimx, dimy =( 'x', 'y')
    print((dtxt+'PS PROJxy assumed for %s' % ifile))
    proj='PS'
  else:
    print("ERROR w PROJ", ecdf.dimensions); sys.exit(0)
  
  # TEST IF WE HAVE THIS VAR!
  if var not in ecdf.variables.keys():
    print(dtxt+'TEST VAR NOT IN FILE! ', var,  ifile)
    return 'VarNotFound'

  try:
    tst=ecdf.variables[dimx]
    lldim=len(tst.shape)
  except:
    lldim=2 # HARD CODE CDO x y
 # Test
  t=ecdf.variables['time']
  times=ecdf.variables['time'][:]
  ntime=len(times)  #  TESTING . was =1 
  if dbg: print(" SIZE OF TIME ", len(times))
  if dbg: print(t.units)
  print(cdf.num2date( times[0],units=t.units))

  EmepFile=EmepFileClass( ifile, ecdf, var, proj,lldim,dimx,dimy,ntime) 
  EmepFile.dimx = dimx
  EmepFile.dimy = dimy
  
  if( lldim == 1):
    EmepFile.xcoords=ecdf.variables[dimx][:]
    EmepFile.ycoords=ecdf.variables[dimy][:]
    EmepFile.dx = EmepFile.xcoords[1]-EmepFile.xcoords[0]
    EmepFile.dy = EmepFile.ycoords[1]-EmepFile.ycoords[0]

   # For eg ECHAM the x-coords are from 0 to 360, and y-coords are reversed
   # (N to S). We reset to EMEP standard here, to simply rest of code. Later we
   # will also reset any 2-D variables directly after reading

    EmepFile.x0 = EmepFile.xcoords[0] - 0.5 * EmepFile.dx
    EmepFile.y0 = EmepFile.ycoords[0] - 0.5 * EmepFile.dy
    EmepFile.xmax = EmepFile.xcoords[-1] + 0.5 * EmepFile.dx
    EmepFile.ymax = EmepFile.ycoords[-1] + 0.5 * EmepFile.dy # from S to N

    if EmepFile.ycoords[-1] < EmepFile.ycoords[0]: # from  N to S
       EmepFile.y0   = EmepFile.ycoords[-1] - 0.5 * EmepFile.dy
       EmepFile.ymax = EmepFile.ycoords[0]  + 0.5 * EmepFile.dy
       EmepFile.yAscending = False
       #EmepFile.ycoords=np.flipud( EmepFile.ycoords ) # No ascending

    # Check for regular spacing... simple test if edge dx ~ mid dx
    nx2= len(EmepFile.xcoords) // 2
    ny2= len(EmepFile.ycoords) // 2
    dx2= EmepFile.xcoords[nx2]-EmepFile.xcoords[nx2-1]
    dy2= EmepFile.ycoords[ny2]-EmepFile.ycoords[ny2-1]
    dx2 = abs(dx2); dy2 = abs(dy2)
   
    if abs(dx2-EmepFile.dx) > 1.0e-5 : EmepFile.xRegular = False
    if abs(dy2-EmepFile.dy) > 1.0e-5 : EmepFile.yRegular = False
    
 # Shouldn't occur now, since we use i_EMEP for PS, lon for lonlat
  elif ( lldim == 2):  
#    EmepFile.ycoords=ecdf.variables[dimy][:,:] 
#    EmepFile.xcoords=ecdf.variables[dimx][:,:]
   # HAR CODE FOR CDO
    xx=ecdf.dimensions['x']
    yy=ecdf.dimensions['y']
    EmepFile.xcoords=np.linspace(0.5,xx.size-0.5,xx.size) # eg 0 .. 131 (2
    EmepFile.ycoords=np.linspace(0.5,yy.size-0.5,yy.size) # eg 0 .. 158 (9
    EmepFile.dx = 1.0
    EmepFile.dy = 1.0
    EmepFile.x0 = 0.0
    EmepFile.y0 = 0.0
    EmepFile.xmax = xx.size-0.5 # CHECK LATER
    EmepFile.ymax = yy.size-0.5
    print(EmepFile.ycoords)
    EmepFile.printme()
  
  if getVals: 
    # tStep will be zero for annual, or by edfault
    if tStep == None:
       print(dtxt+"getVals all time-steps " )
       EmepFile.vals=np.array( ecdf.variables[var] )  # 2 or 3d
    else:
       tmpv= np.array( ecdf.variables[var][:,:,:] ) 
       maxtstep = tmpv.shape[0]  -1   # -1 for python index
       if maxtstep < tStep: 
          print ( dtxt+'TSTEP WARNING!! Requested ', tStep, ' but len=', maxtstep )
          tStep = maxtstep
       #print ( dtxt+'SHAPE TMPV ', tStep, tmpv.shape, tmpv.shape[0]  )
       
       EmepFile.vals=np.array( ecdf.variables[var][tStep,:,:] ) 

    #Echam struggles..
    #tmpvals=ecdf.variables[var][tStep,:,:]
    #tmpvals[:,10] = 100.0
   # This flips j coordinates (for some reason...)
    #print('FLIP TEST PRE  ', tmpvals[0,5], tmpvals[-1,5] )
    #print('FLIP TEST PRE  ', tmpvals[5,5], tmpvals[-1,5] )
    #tmpvals=np.flipud(tmpvals)
    #print('FLIP TEST POST ', tmpvals[0,5], tmpvals[-1,5] )
    #print('FLIP TEST POST ', tmpvals[5,5], tmpvals[-1,5] )
    #EmepFile.vals=tmpvals.copy()
    #print('FLIP TEST Emep ', tmpvals[5,5], tmpvals[-1,5] )
    #print('ECHAM ga', EmepFile.xcoords[10], EmepFile.vals[1,10] )
    #plt.imshow(EmepFile.vals)
    #plt.colorbar()
    #plt.show()
    #plt.imshow(tmpvals2)
    #plt.colorbar()
    #plt.show()

  # O2017 - needs checking
  elif len(getijPts) > 0:
    npt=len(getijPts)
    EmepFile.vals = np.zeros([ntime,npt])
    sys.exit('ECHAM gb')
    for tStep in range(0,ntime):
     npt=0
     for i, j in getijPts:
       #if i < 1 or j < 1: sys.exit('Wrong iPt, jPt ')
       #print('IJ n', i, j, npt)
       EmepFile.vals[tStep,npt] =ecdf.variables[var][tStep,j,i]
       #print('Inside:', npt, multiwrite( EmepFile.vals[0:10,npt],'%5.1f') )
       npt += 1
  elif getijPt[0]:
    i = getijPt[1]; j = getijPt[2]
    if i < 1 or j < 1: sys.exit('Wrong iPt, jPt ')
    EmepFile.vals=ecdf.variables[var][:,j,i]
    sys.exit('ECHAM gc')
  else:
    EmepFile.vals= np.array( [ np.nan, np.nan ])
    print(dtxt+'getVals false')
  #sys.exit('Checked time')

  if dbg: print(dtxt+"DIMS ",  ifile, dimx, dimy , lldim)
  if dbg: print(dtxt+"PROJ ",  proj)
  try:
    print((dtxt+"VALS  ", EmepFile.vals.min(), EmepFile.vals.max(), 
           EmepFile.vals.shape))
  except:
    print((dtxt+'No vals requested'))

  return EmepFile

#--------------- Was getEmepPt.py ----------------------------------
#  getEmepPt comprises three methods
#    RelIj
#    RelXy
#    getEmepVal - which uses bi-linear interpolation to get best-estimate
#
#-------------------------------------------------------------------
def RelIj(x, y, x0, y0, dx, dy):
  """ gets i, j coordinates 
      x0, y0 are left and bottom edges (set in getEmepCdf usually)
      designed for lon, lat arrays but should work with i,j arrays also?
  """
  dtxt='RelIj:' # for debug txt

  i= int( (x-x0)/dx )  # now with zero as lowest coord
  j= int( (y-y0)/dy ) # now with zero as lowest coord

  if( i <  0 or j < 0 ):
    print(dtxt+"EDGE of domain ", x, xLeft, i); sys.exit(0)
  return i, j

#-------------------------------------------------------------------
def RelXy(x, y, x0, y0, dx, dy):
  """ returns (xrel,yrel) values for point (x,y)
    x0, y0 are left and bottom edges (set in getEmepCdf usually)
    This code cannot cope with edges though. """

  xrel= (x-x0 )/dx
  yrel= (y-y0 )/dy
  if xrel < 0.0 or yrel < 0.0:
    print("WARNING XYrel not coded ", x, x0, xrel, y, y0, yrel)
    print("WARNING Yrel", yrel)
    if yrel < 0.0:
        print("WARNING XYrel South Pole Fix!")
        yrel = max(0.0, yrel)
        #sys.exit('XYrel SP!')
    if xrel < 0.0:
        sys.exit('XYrel')
  return xrel,yrel

#-------------------------------------------------------------------
def IrregRelP(p, pcoords,wrapP= -999,dbg=False):
  """ Gets relative coordinates for irregular coordinate systems.  Uses simple
   search to find left+right coordinates. Assumes increasing pcoords to start
   with.  wrapP not implemented yet """
  dtxt='IrregRelP:'

  dbg=True # DEC TMP
  if p < np.min(pcoords): #2 if p < pcoords[0]:
     print('WARNING - wrap around not implemented yet for  pp', p, pcoords[0]  )
     return -888.

  ncoords = len(pcoords)
  coords  = pcoords.copy()

  flipped_coords = False
  if ( pcoords[1] < pcoords[0] ):  # Coords from -ve to +ve, e.g. N to S
    flipped_coords = True
    coords = np.flipud(coords)     # Simplifies thoughts n code, from low to high

  ip = 0
  for pp in coords:
    if dbg: print(dtxt+'pp: ',ip, p, pp, len(coords) )
    if pp > p:
      if dbg: print(dtxt+'!!: ',ip, pp,p)
      break
    ip += 1

  if ip == ncoords:
    print(dtxt+'WARNING - wrap around not implemented yet for  pp', ip, np  )
    return -999.

  dp    = coords[ip]-coords[ip-1]
  prel  = ip-1 +  ( p-coords[ip-1] )/dp
  if ( pcoords[1] < pcoords[0] ): prel = (ncoords-1) - prel
  xprel = (p-coords[0])/dp       # Approx if dp not constant, just testing
  print(dtxt+'DONE  coords', ip, ncoords, p, coords[ip-1],  coords[ip], dp, prel, xprel  )
  if flipped_coords:
    print(dtxt+'DONE pcoords', ip, ncoords, p, pcoords[ip-1],  pcoords[ip], dp, prel, xprel  )
    ip =  ncoords - ip  #CHECK
    print(dtxt+'FLIP pcoords', ip, ncoords, p, pcoords[ip-1],  pcoords[ip], dp, prel, xprel  )
    sys.exit('ECHAM tmp')

  return prel

#def IrregRelP(p, pcoords):
#  """ Gets relative coordinates for irregular coordinate systems.
#   Uses simple search to find left+right coordinates. Assumes
#   increasing pcoords to start with """
#
#  if p < np.min(pcoords): #2 if p < pcoords[0]:
#     print('WARNING - wrap around not implemented yet for  pp', p, pcoords[0]  )
#     return -888.
#
#  np = len(pcoords)
#  ip = 0
#  pStep = 1
#  if ( pcoords[1] < pcoords[0] ):  # Coords from -ve to +ve, e.g. N to S
#    pStep = -1
#  for pp in pcoords:
#    if pp > p:
#      break
#    ip += pStep
#
#  if ip == np:
#     print('WARNING - wrap around not implemented yet for  pp', ip, np  )
#     return -999.
#
#  dp    = abs(pcoords[ip]-pcoords[ip-1])
#  prel  = ip-1 +  (p-pcoords[ip-1] )/dp
#  xprel = (p-pcoords[0])/dp             # Approx if dp not constant
#  #print('TESTING pp', ip, np, p, pcoords[ip-1],  pcoords[ip], dp, prel, xprel  )
#  return prel

def IrregRelXy(x, y, xcoords, ycoords,latlon=True):
  """ Gets relative coordinates for irregular coordinate systems.
   Ensures thar IrregRelP above is called with increasing pcoords
   to cope with some grids using N to S and others S to N """

  #x = -179.95   # DEBUG
  #y = -88.4   # DEBUG

  xp = x
  #if xp > xcoords[-1]: # CRUDE EDGE PROBLEM, ARGH
  #       print('WARNING EDGING!', x, xp, xcoords[0],  xcoords[-1] )
  #       xp = xcoords[-1]-0.0001
  xrel = IrregRelP( xp, xcoords )
  print('TESTING XX', xp, xcoords[0],  xcoords[-1],  xrel )


  yrel = IrregRelP( y, ycoords )

  # All y-coordinates are now ascending.
  #if ycoords[-1] > ycoords[0]: # S to N
  #else: # N to S, 
  #  yrcoords = np.flipud( ycoords ) # alt ycoords[::-1] 
  #  print('TESTING AA RY',  len(ycoords) )
  #  yrrel = IrregRelP( y, yrcoords )
  #  yrel  = len(ycoords) - yrrel
  print('TESTING YY', y,  ycoords[0],  ycoords[-1],  yrel )

  if xrel < 0.0 or yrel < 0.0:
    print("WARNING IreggXYrel not coded ", x,  xrel, y, yrel)
  #sys.exit('ECHAM gx')
  return xrel,yrel

#-------------------------------------------------------------------
def getEmepVal(xPtin,yPtin,EmepCdf,minmax=False,dbg=False):
  """ Uses bi-linear interpolation to estmate value
    of field vals at point xPt, yPt
  """
  dtxt='getEmepVal:'

  # Get coordinates in model grid if polar stereo:

  xPt, yPt = xPtin, yPtin
  if hasattr(xPt,"__len__"): # copes with numpy class or simple list
    print('ERROR! getEmepVal needs scalar x,y; got array:', type(xPt) )
    sys.exit()

  print(dtxt+'TEST? proj, xPt, yPt ', EmepCdf.proj, xPt, yPt)
  if EmepCdf.proj == 'PS':
    xPt, yPt = coords.LonLat2emepXy(xPt,yPt)  # XPt, yPt are lon,lat
    if dbg: 
      print('PS lon,lat => model xPt, yPt ', xPtin, yPtin, ' => ',  xPt, yPt)
  elif EmepCdf.xcoords[-1] > 180:  # QUERY 180
  # if long xcoords are from 0 to 360, we shift Xpt
    if xPtin < 0.0:
       xPt = xPtin + 360
       print(dtxt+'Xshift: ', xPtin , xPt, EmepCdf.xcoords[-1] )

  #else: # lon lat already ok
  #  xemep, yemep = RelXy(xPt,yPt,EmepCdf.x0,EmepCdf.y0,EmepCdf.dx,EmepCdf.dy)

  err = np.array( [ np.NaN ] )
  if xPt > EmepCdf.xmax or yPt > EmepCdf.ymax:
    print("OUTSIDE GRID ", xPt, yPt, EmepCdf.xmax, EmepCdf.ymax )
    return  err, err, err

  #M17 Emep coords relative to grid LL point
  #M17 x, y = RelXy(xPt, yPt, EmepCdf.x0,EmepCdf.y0,EmepCdf.dx,EmepCdf.dy) 
  # Emep coords relative to grid LL centre

  if EmepCdf.xRegular and EmepCdf.yRegular :
    x, y = RelXy(xPt, yPt, EmepCdf.xcoords[0],EmepCdf.ycoords[0],EmepCdf.dx,EmepCdf.dy) 
  else:
    x, y = IrregRelXy(xPt, yPt, EmepCdf.xcoords,EmepCdf.ycoords) 
  if x < 0 or y < 0:
    print(dtxt+"OUTSIDE GRID ", xPt, yPt, x, y)
    return  err, err, err

  if dbg:
     print(dtxt+"INSIDE GRID ", xPt, yPt, x, y)
     print(dtxt+"MIN x0, y0    ", EmepCdf.x0, EmepCdf.y0)
     print(dtxt+"max XCRD YCRD ", EmepCdf.xcoords.max(), EmepCdf.ycoords.max())
     print(dtxt+"xPt, yPt    ", xPt, yPt)   #, " DLON ", xcoords[1]-xcoords[0]
     print(dtxt+"xxx XCRD YCRD ", x, y)   #, " DLON ", xcoords[1]-xcoords[0]
     EmepCdf.printme()

  iL=int(x) # left
  iR=iL+1
  #if EmepCdf.yAscending:
  jS=int(y) # from south
  jN=min( jS+1, len(EmepCdf.ycoords)-1)

  #else:
  #  jN=int(y) # from N
  #  jS=min( jN+1, len(EmepCdf.ycoords)-1) # TMP!!!

  #QUERY 180 if jS > 180:
  #QUERY 180   print(dtxt+'OOPSjS ', xPt, yPt, iL,jS, xcoords.max(), ycoords.max())
  #QUERY 180   sys.exit(0)

  # Get data for a square at 0,0,  0,1 etc for bidirectional
  # relative to grid centre-points
  #f00  =EmepCdf.vals[jS,iL]               #f00  =e.variables[varname][:,jS,iL]
  if dbg:
     print(dtxt+'iL,iR-xx ', xPt, yPt, iL, iR, 
          EmepCdf.xcoords[iL], EmepCdf.xcoords[iR])
     print(dtxt+'jS,jN-yy ', xPt, yPt, jS, jN, 
          EmepCdf.ycoords[jS], EmepCdf.ycoords[jN])

  print(dtxt+'BOX SHAPE ', EmepCdf.vals.shape )
  # Crude.... O2017
  if len( EmepCdf.vals.shape ) > 2:
    box = EmepCdf.vals[:,jS:jN+1,iL:iR+1]
  else:
    box = EmepCdf.vals[jS:jN+1,iL:iR+1]
    box = box[ np.newaxis, :, : ] # Make 3D

  f00 = box[:,0,0]
  f10 = box[:,1,0]
  f01 = box[:,0,1]
  f11 = box[:,1,1]

  # bidirectional interpolation
  dx = x-int(x)
  dy = y-int(y)
  value =  f00*(1-dx)*(1-dy) + f01*dx*(1-dy)+f10*(1-dx)*dy + f11*dx*dy

  # tips from #http://stackoverflow.com/questions/21816433/element-wise-array-maximum-function-in-numpy-more-than-two-arrays
  #maxvals = maximum.reduce([x0,x1,x2,x3])
  # 5 times faster:
  if minmax: 
    maxval = vstack([f00,f10,f01,f11]).max(axis=0)
    minval = vstack([f00,f10,f01,f11]).min(axis=0)

  if dbg:
     print(dtxt,' --------- OUTFs ------------------------------------')
     print(dtxt+"x,y -> ijcoords ", xPtin, yPtin, iL, iR, jS, jN )
     print(dtxt+"x, y, dx dy    ", x, y, dx, dy)
     print(dtxt+"x, y, dx dy    ", x, y, dx, dy)
     print(dtxt, jS, iL, EmepCdf.vals[1,jS,iL], EmepCdf.vals.min(), EmepCdf.vals.max())
     print(dtxt,x,y, dx, dy, iL,iR, jS, jN , EmepCdf.varname, EmepCdf.vals.max())
     #print('Fs ', f00, f10, f01, f11)
     #print('F00', f00, (1-dx)*(1-dy))
     #print('F10', f10, dx*(1-dy))
     #print('F01', f01, (1-dx)*dy) 
     #print('F11', f11, dx*dy)
 
     for i in range(0,len(f00)): # if var is array
        print( i, f00[i],f10[i],f01[i],f11[i], value[i] )
  if minmax: 
    return value,minval,maxval 
  else:
    return value

#=============================================================================
if ( __name__ == "__main__" ):
  import argparse
  dtxt='EmepCdf main:'
#------------------ arguments  ----------------------------------------------
  parser=argparse.ArgumentParser(epilog=__doc__,
   formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v','--varname',help='varname in nc file',required=True)
  parser.add_argument('-i','--ifile',help='Input file',required=True)
  args=parser.parse_args()
  print(dtxt+'ARGS', args)

  ifile= args.ifile
  var=args.varname
  if not os.path.isfile(ifile):
     sys.exit('FILE NOT FOUND!!!' + ifile )

  print('-'*78) #------------------------------------
  print("Testing full grid, tStep=3  ", args.ifile )

  EmepFile = RdEmepCdf( ifile, var, getVals = True, tStep=3 ) # 180 from ECHAM day.nc
  EmepFile.printme()

  #print("Testing one point ", ifile)
  #EmepFile2, ecdf2 = RdEmepCdf( ifile, var )
  #EmepFile2.vals=ecdf2.variables[var][:,10,10]
  #EmepFile2.printme()
  #print "XY emep for proj %s %6.2f %6.2f is %6.2f %6.2f:" % (EmepFile.proj, lon,lat, xemep, yemep)

  print('-'*78) #------------------------------------
  lon, lat = -9.89, 53.3  # Mace Head
  print('Testing one point:', lon, lat )
  # Now with all tsteps:
  EmepFile = RdEmepCdf( ifile, var, getVals = True ) # 180 from ECHAM day.nc

  t3 = time.time()
  v, minv, maxv = getEmepVal(lon,lat,EmepFile,minmax=True,dbg=False)
  t4 = time.time()

  print('Testing nmin, nmax:')
  print('1st: ', v[0], minv[0], maxv[0], len(v) )
  print('Last:', v[-1], minv[-1], maxv[-1], len(v) )
  #sys.exit()

#SPEED  EmepFile=  RdEmepCdf( ifile, var )
#print(EmepFile.lldim, EmepFile.dimx, EmepFile.vals.max())
#SPEED  EmepFile.printme()
 # For points, here use i,j model coordinates coordinates
 # Use getEmepPt for use of lat/long
#SPEED  EmepFile=  RdEmepCdf( ifile, var, getijPt = [ True, 23, 45]  )
#SPEED  EmepFile.printme()
#SPEED  from StringFunctions import multiwrite
#SPEED  print('Ozone series ', multiwrite( EmepFile.vals[0:10],'%5.1f') )

 # Test a few points
  print('-'*78) #------------------------------------
  print('Testing several ij points:' )
  gpts=[ [ 12, 24], [12,25], [13,23], [13, 24], [13,25], [14,24], [21, 34], [22,34] ]
  EmepFile =  RdEmepCdf( ifile, var, getVals=True )

 # Fails for ECHAM since direct ecdf.variables used:
  npt=len(gpts)
  npt=0
  for i, j in gpts:
       print('point ', npt, i, j, EmepFile.vals[:4,j,i] )
       npt += 1
  

#========================================== END
# for ipython tips, see http://stackoverflow.com/questions/22631845/how-to-pass-command-line-arguments-to-ipython
# e.g. ipython -i arg1 arg2
#import datetime as dtim #from netcdftime import utime
  # For future use, maybe ...
  #emeptime = utime('days since 1990-01-01 00:00:00')
  #t0   = dtim.datetime(1990, 1, 1, 0, 0, 0 )
  #nt0  = emeptime.date2num(t0)
  #times=e.variables['time']
