#!/usr/bin/env python3
# https://earthscience.stackexchange.com/questions/12057/how-to-interpolate-scattered-data-to-a-regular-grid-in-python
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import emxmisc.printMatrix as pm
import emxplots.plotmap as pmap
import emxcdf.makecdf as cdf
import sys

"""
def ndimage_fill(data, invalid=None):
def fill_arctics(lons,lats,vals):
def box_fill(lons,lats,vals,facs=[10,2,3,3]):  #  0.5*10*6*12=360 30,60,120]):
def astro_fill(vals, stddevs = [ 0.5, 1, 2, 5, 10] ):
def astro_box_fill(lons,lats,vals,stddevs=[0.5,2],boxfacs=None):
def interp_RegGrid(x,y,z,xx,yy,method='linear'):
def interp_coarse_to_fine(x,y,xx,yy,nfiner=5,method='linear'):
def nninterp(lons,lats,vals,method='nearest',demo=False):
def NNinterp(lonsdata,mask):
def scat_interp(x,y,z,xi,yi,mask=None,method='linear'):
"""

dtxt='geo_interp:'
# some debug x-sections
i1=332; i2=406; jxs=286 # Eur
i1=250; i2=406; jxs=286; area_txt = 'NW-Eur' # Eur
i1=100; i2=250; jxs=250; area_txt = 'N-USA-Can' #  Northern USA/Canada?
#   i1=215; i2=240; j=250; area_txt = 'N-USA-Can' #  Northern USA/Canada?
j1=jxs-10; j2=jxs+20
#i=218 # DBG USA
idbg=i1+13  # 214-i1
jdbg=j1+24
xsec= np.linspace(i1,i2,i2-i1+1)

   #F fig, axs = plt.subplots(nrowsvals=4,ncols=1,sharex=True) #,sharey=True) #,heightratios=)
   #F axf = axs.flat

#-----------------------------------------------------------------------------
def scat_interp(x,y,z,xi,yi,mask=None,method='linear'):
  """
  From https://earthscience.stackexchange.com/questions/12057/how-to-interpolate-scattered-data-to-a-regular-grid-in-python
  x,y,z are point data
  xi, yi are grid data coords, e.g. lons, lats
  mask has shape of xi, yi
  """
  from scipy.interpolate import griddata
  X, Y = np.meshgrid(xi,yi)
  z = griddata((x, y), z, (X, Y), method=method)
  if mask is not None:
    z[mask] = np.nan
  return z

#-----------------------------------------------------------------------------
# https://stackoverflow.com/questions/5551286/filling-gaps-in-a-numpy-array/9262129#9262129
def ndimage_fill(data, invalid=None):
  from scipy import ndimage as nd

  #DS indices = nd.distance_transform_edt(invalid_cell_mask, return_distances=False, return_indices=True)
  #indices = nd.distance_transform_edt(invalid, return_distances=False, return_indices=True)
  #data = data[tuple(ind)]
  if invalid is None: invalid = np.isnan(data)

  ind = nd.distance_transform_edt(invalid,
                                    return_distances=False,
                                    return_indices=True)
  return data[tuple(ind)]
#-----------------------------------------------------------------------------
def fill_arctics(lons,lats,vals):
  jS = 60
  vals[:jS,:] = np.nanmean(vals[jS:jS+60,:])
  jN=320
  vals[jN:,:] = np.nanmean(vals[jN-20:jN,:]) # N Canada, Eur
  return vals

#-----------------------------------------------------------------------------
def box_fill(lons,lats,vals,facs=[10,2,3,3],dbgij=None):  #  0.5*10*6*12=360 30,60,120]):
  """
   The raw data here have 0.5 x 0.5 deg
      start with 10 x 5 deg boxes, then ....
      CONSIDER 3*3*2*10
               2*3*6*5
  """
  import emxmisc.grid_coarsen as gc
  dtxt='BoxFill:'
  xnew=vals.copy()
  nvals=vals.copy()
  nlons=lons.copy()
  nlats=lats.copy()
  assert np.prod(facs) == 180,f'box_fill should reach 180. Has {np.prod(facs)}'
  dbg=False
  if dbgij is not None:
     dbg=True
     idbg, jdbg = dbgij
     print(dtxt+f'INBF {idbg} {jdbg} {nlons[idbg]} {nlats[jdbg]} {nlons.shape}'
                f'{nlats.shape} {nvals.shape} {xnew[jdbg,idbg]}') 
     print(dtxt+f'IJBF {lons[idbg]} {lats[jdbg]} {nvals[jdbg,idbg]}') 

  cumfdx = 1; cumfdy = 1
  for nf, f in enumerate(facs): # factors of 360, 720
    fdx = f; fdy = f
    if nf==0: fdx *= 2
    cumfdx *= fdx
    cumfdy *= fdy
    ndx=nlons[1]-nlons[0]
    ndy=nlats[1]-nlats[0]
    nvals = gc.coarsen(nvals,dx=fdx,dy=fdy)
    #jS1 = 56; jS2 = 65  # S and N of Antacrtic box
    #print(f'\nZONEB {nf:2d} {f:2d} fdy:{fdy:2d} ndy:{ndy:.1f} cum:{cumfdy:3d} {lats[cumfdy]:.2f} {lats[jS1]:.2f} {lats[jS2]:.2f}')

    for j, lat in enumerate(lats):
      jc = j//cumfdy
      assert jc < len(nlats), dtxt+f'WRONG J LEN: {j} {jc} {nlats[j]}'
      for i, lon in enumerate(lons):
        ic = i//cumfdx
        assert ic < len(nlons), dtxt+f'WRONG I LEN: {i} {ic} {nlons[i]}'
        if dbg and i==idbg and j==idbg: print(f'{dtxt}IJ {ic} {jc} {xnew[j,i]} {nvals[jc,ic]} fin?{np.isfinite(xnew[j,i])}')
        if ~np.isfinite(xnew[j,i]): # transfer back to fine 
          xnew[j,i] = nvals[jc,ic]
          if dbg and i==idbg and j==idbg: print(f'{dtxt}XN {ic} {jc} {xnew[j,i]} {nvals[jc,ic]}')

    # Put new values into coarser array, before restarts
    nlons = gc.coarsen(nlons,dx=fdx)
    nlats = gc.coarsen(nlats,dx=fdy)
    if len(nlons) > 1:
      ndx=nlons[1]-nlons[0]
    if dbgij is not None: 
       print(dtxt+f'BOXUT {nf} {f} {fdx} {fdy} {ndx} {nlons.shape} {nlats.shape} {xnew[jdbg,idbg]}')

  return xnew
#-----------------------------------------------------------------------------
def printMat(txt,x,i,j,dij=3):
   for jj in range(j-dij,j+dij+1):
     print(f'{txt}: ',end='')
     for ii in range(i-dij,i+dij+1):
        print(f'{x[j,i]:8.5f}',end='')
     print('')
#-----------------------------------------------------------------------------

def astro_fill(vals, stddevs = [ 0.5, 1, 2, 5, 10] ):
   """ keep as fine-scale as possible, but increase std to fill world """
   import emxmisc.astropy_convolve as ap
   xnew = vals.copy()

   dbg=False; i=425;j=232
   if dbg: print(f'ABFastA: {vals[j,i]} {np.max(vals[j-5:j+6,i-5:i+6])}')

   for std in stddevs: #  [ 0.5, 1, 2, 5, 10 ]: # orig was 10
     if dbg: pmap.plotmap(vals[j-20:j+21,i-20:i+21],f'{dtxt}_{__name__}_{std:.1f}',
             plotfile=f'plot{dtxt}{int(10*std):02d}AAA.png')
     znew=ap.astro_conv2d(vals[:,:],stddev_x=std,stddev_y=0.5*std,dbg=False)
     if dbg:
       pmap.plotmap(znew[j-20:j+21,i-20:i+21],f'bbbb{std:.1f}',plotfile=f'plot{int(10*std):02d}BBB.png')
       printMat(f'ABFMATzz{std}',znew,i,j,dij=8)
     xnew= np.where(np.isfinite(xnew),xnew,znew)
     if dbg:
       pmap.plotmap(xnew[j-20:j+21,i-20:i+21],f'cccc{std:.1f}',plotfile=f'plot{int(10*std):02d}CCC.png')
       printMat(f'ABFMATxx{std}',xnew,i,j,dij=16)
       print(f'ABFastX: {std} {xnew[j,i]} {np.max(xnew[j-5:j+6,i-5:i+6])} --------------------')
   return xnew

#-----------------------------------------------------------------------------
def astro_box_fill(lons,lats,vals,stddevs=[0.5,2],boxfacs=None,dbgij=None):
   dtxt='AstBoxFill:'
   dbg =  dbgij is not None
   if dbg:
     i, j = dbgij
     print(f'{dtxt} ABFPreA: {vals[j,i]}')
   znew = astro_fill(vals,stddevs=stddevs)
   if dbg: print(f'{dtxt} ABFPosA: {znew[j,i]} {np.mean(znew)}')
   if boxfacs is None:
     znew = box_fill(lons,lats,znew)
     if dbg: print(f'{dtxt} ABFPosB: {znew[j,i]} {np.mean(znew)}')
   else:
     znew = box_fill(lons,lats,znew,facs=boxfacs,dbgij=dbgij)
     if dbg:
       print(f'{dtxt} ABFPosC:  {i} {j} {znew[j,i]} {np.mean(znew)}')
       pmap.plotmap(znew[j-20:j+21,i-20:i+21],'dddd',plotfile=f'plotgeo_{dtxt}C.png')
   return znew
  
#-----------------------------------------------------------------------------
# from interp_regGrid.py
def interp_RegGrid(x,y,z,xx,yy,method='linear'):
  """ x,y,z are from input file to be interpolated
     xx,yy are new coords to be interpolated to
  """
  import scipy.interpolate as si
  assert x[-1]>x[0],'WRONG order x'
  assert xx[-1]>xx[0],'WRONG order xx'
  assert y[-1]>y[0],'WRONG order y'
  assert yy[-1]>yy[0],'WRONG order yy'
  interp = si.RegularGridInterpolator((x, y), z,method=method, bounds_error=False, fill_value=np.nan)
  X, Y = np.meshgrid(xx, yy, indexing='ij')
  return interp((X,Y))
#-----------------------------------------------------------------------------
def interp_coarse_to_fine(x,y,xx,yy,nfiner=5,method='linear'):
  """ x,y,z are from input file to be interpolated
     xx,yy are new coords to be interpolated to
     This is just a help function 
  """
  nx=len(x)
  ny=len(y)
  xx=np.linspace(x[0],x[-1],nx*nfiner,endpoint=True)
  yy=np.linspace(y[0],y[-1],ny*nfiner,endpoint=True)
  finegrid=dict()
  finegrid['lons'] = xx
  finegrid['lats'] = yy
  finegrid['vals'] = interp_RegGrid(x,y,z,xx,yy,method='linear')
  return finegrid
#-----------------------------------------------------------------------------

# from mk2025bvoc.py
def nninterp(lons,lats,vals,method='nearest',demo=False):
  from scipy.interpolate import griddata

  xi= lons.copy() #np.linspace(xmin,xmax,ndx)
  yi= lats.copy() #np.linspace(ymin,ymax,ndy)

  x=[]; y=[]; z=[]; a=[]
  for j, lat in enumerate(lats):
    for i, lon in enumerate(lons):
      if np.isfinite(vals[j,i]):
        x.append(lon)
        y.append(lat)
        z.append(vals[j,i])

  if demo:
    print(f'OUTPRE: {np.min(z):12.2f}  {np.max(z):12.2f}')
    for meth in 'cubic nearest linear'.split():
      zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method=meth)
      print(f'OUTPOS {meth:<10s}: {np.nanmin(zi):12.2f}  {np.nanmax(zi):12.2f}')
      pmap.plotmap(zi,'nnint'+meth)
  else:
      zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method=method)

  return zi
#-----------------------------------------------------------------------------
# NNint.py:
def NNinterp(lonsdata,mask):
   # NOT FIXED YET
   # a boolean array of (width, height) which False where there are missing values and True where there are valid (non-missing) values

   #?  xi,yi = np.meshgrid(lons,lats)
   #?  dense_points=np.vstack((xi.ravel(),yi.ravel())).T
   # array of (number of points, 2) containing the x,y coordinates of the valid values only
   xx, yy = numpy.meshgrid(numpy.arange(data.shape[1]), numpy.arange(data.shape[0]))
   xym = numpy.vstack( (numpy.ravel(xx[mask]), numpy.ravel(yy[mask])) ).T

   # the valid values in the first, second, third color channel,  as 1D arrays (in the same order as their coordinates in xym)
   data0 = numpy.ravel( data[:,:][mask] )

   # interpolate
   interp0 = scipy.interpolate.NearestNDInterpolator( xym, data0 )
   print('DATA0 ', np.max(data0), np.min(data0) )
   print('INTER ', np.max(interp0), np.min(interp0) )
   print('INTER0 ', interp0  )

   try:
     result0 = interp0(numpy.ravel(xx), numpy.ravel(yy)).reshape( xx.shape )
   except:
     result0 = data
   print('RESTUL ', np.max(result0), np.min(result0), result0.shape )
   return result0
#-----------------------------------------------------------------------------


#pmap.plotlonlatmap(lons,lats,vals,levels=levs,cmap='tab20c',img_bounds=[-179,179,-89,89])
#pmap.plotlonlatmap(lons,lats,vals,levels=levs,cmap='tab20',img_bounds=[-179,179,-89,89])


if __name__ == '__main__':

  
   ds=xr.open_dataset('emepd_YuanPFT.nc')
   lons=ds.lon.values
   lats=ds.lat.values # from N ro S so far
   maxvals=ds.max_C3_Crop.values[:,:]
   maxvals = np.where(maxvals>0.0,maxvals,np.nan)
   vals=maxvals.copy()
   mask= np.isfinite(vals)
   xsout={'Orig':vals[jxs,i1:i2+1]}

   #testr = nninterp(lons,lats,maxvals)
   #sys.exit()
   
   levs = [ 0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0 ]
   pmap.plotlonlatmap(lons,lats,vals,levels=levs,cmap='Paired',
     img_bounds=[-179,179,-89,89],title='Orig LAI',ofile='plotMaxLAI_orig.png')
   
   xrarrays = []
   months=list(range(1,13))

   #for method in 'nninterp nninterpU box_fill box_fill2 box_fill3 astro_box_fill astro_box_fill2 astro_box_fill3'.split():
   for method in 'scat_interp nninterp nninterpU box_fill2 astro_box_fill2'.split():
      znew = np.zeros([12,len(lats),len(lons)])
      for mm in range(12):
        vals=ds.Norm_C3_Crop.values[mm,:,:]
        print('VALS 22', vals[2,2] )
        valsUnfilled = vals.copy()
        vals = fill_arctics(lons,lats,vals)
        print('NVALS 22', vals[2,2], valsUnfilled[2,2] )

        if method == 'scat_interp':
           x=[];y=[];z=[]
           for j,lat in enumerate(lats):
             for i,lon in enumerate(lons):
               if valsUnfilled[j,i] > 0.:
                 x.append(lon)
                 y.append(lat)
                 z.append(valsUnfilled[j,i])
           znew[mm,:,:] = scat_interp(x,y,z,lons,lats,mask=None,method='linear')
        if method == 'box_fill':
          print(f'{method}FILL {lons.shape} {lats.shape} {vals.shape}') 
          znew[mm,:,:]  = box_fill(lons,lats,vals)
        elif method == 'box_fill2':
          znew[mm,:,:]  = box_fill(lons,lats,vals,facs=[2,3,5,6])
        elif method == 'box_fill3':
          znew[mm,:,:]  = box_fill(lons,lats,vals,facs=[3,3,2,10])
        elif method == 'nninterp':
          znew[mm,:,:] = nninterp(lons,lats,vals)
          print('UVALSA 22', vals[2,2], valsUnfilled[2,2], znew[mm,2,2] )
        elif method == 'nninterpU':
          znew[mm,:,:] = nninterp(lons,lats,valsUnfilled)
          print('UVALSU 22', vals[2,2], valsUnfilled[2,2], znew[mm,2,2] )
        elif method == 'astro':
          znew[mm,:,:]  = astro_fill(vals)
        elif method == 'astro_box_fill':
          znew[mm,:,:]  = astro_box_fill(lons,lats,vals)
        elif method == 'astro_box_fill2':
          znew[mm,:,:]  = astro_box_fill(lons,lats,vals,boxfacs=[2,3,5,6]) # prod=180
        elif method == 'astro_box_fill3':
          znew[mm,:,:]  = astro_box_fill(lons,lats,vals,boxfacs=[3,3,2,10])
        elif method == 'ndimage_fill':
            znew[mm,:,:] =ndimage_fill(vals,~mask)
        print('DBGXR ',method, mm,  np.nanmax(vals), np.nanmax(znew[mm,:,:]), vals[jxs,500], znew[mm,jxs,500], vals[2,2] )
      
         #maxznew = np.max(znew,axis
         #znew = np.where(np.isfinite(znew),znew/np
      znew /= np.max(znew,axis=0)
      print('DBGZNEW ', method, np.nanmax(znew), znew[:,jxs,500] )
      xrarrays.append( dict(varname=f'NormedLAI_{method}', dims=['month', 'lat','lon'],
             attrs = {'note':'test xx','NOTE':f'InterpMethod:{method}'},
             coords={'month':months, 'lat':lats,'lon':lons},data=znew ) )
   xrtest =  cdf.create_xrcdf(xrarrays,globattrs={'AA':'AA'},outfile=f'testing_geo_interps.nc')
       
      
   """
      # odd value at 218  1.781...
      # XS plots:
     lw=2
     plt.clf()
     for key, values in xsout.items():
        if lw==2:
          plt.plot(xsec,values,marker='+',color='k',label=key)
        else:
          plt.plot(xsec,values,lw=lw,label=key)
        lw=1
        print(f'XS {key} {xsout[key][16:23]}')
     plt.legend()
     plt.title(f'{area_txt}  {lons[i1]} - {lons[i2]} E {lats[jxs]} N')
     plt.tight_layout()
     plt.savefig(f'plotYuanXSLAI_{method}_{area_txt}.png')
     plt.clf()
      
   """
   sys.exit('DONE')
      
      
     # https://gis.stackexchange.com/questions/150874/interpolation-grid-for-scattered-data-having-latitude-longitude-coordinates
      
# https://sqlpey.com/python/top-5-methods-to-perform-two-dimensional-interpolation-using-scipy/

   """
   if method == 'box_fill':
   
       znew = box_fill(lons,lats,vals)
       pmap.plotlonlatmap(lons,lats,znew,title=f'method:{method}',levels=levs,cmap='Paired',
         img_bounds=[-179,179,-89,89],ofile=f'plotMaxLAI_{method}.png')
       xsout[f'{method}'] = znew[jxs,i1:i2+1]
     
     if method == 'Rbf':  # FAILS - killed on PC, 
       # crude - get scattered
       from scipy.interpolate import griddata
       import scipy.interpolate as si
       x=[]; y=[]; z=[]
       for j, lat in enumerate(lats):
         for i, lon in enumerate(lons):
            if maxvals[j,i] > 0.0:
               x.append(lon)
               y.append(lat)
               z.append(vals[j,i])
     
       # from https://www.tutorialspoint.com/scipy/scipy_interpolate_rbfinterpolator_function.htm
       points = np.array([ [x[n],y[n]] for n in range(len(x)) ])
       for N in [ 3, 5, 10, 50]:
         f = si.RBFInterpolator(points,z,kernel='linear',neighbors=N)
         xi,yi = np.meshgrid(lons,lats)
         dense_points=np.vstack((xi.ravel(),yi.ravel())).T
         zi=f(dense_points)
         znew = zi.reshape([360,720])
         pmap.plotlonlatmap(lons,lats,znew,title=f'method:{method}',levels=levs,cmap='Paired',
           img_bounds=[-179,179,-89,89],ofile=f'plotMaxLAI_{method}.png')
         xsout[f'{method}{N}'] = znew[jxs,i1:i2+1]
     
     elif method=='fill':
     
       znew=fill_world(vals,~mask)
       pmap.plotlonlatmap(lons,lats,znew,title=f'method:{method}',levels=levs,cmap='Paired',
         img_bounds=[-179,179,-89,89],ofile=f'plotMaxLAI_{method}.png')
       xsout[f'{method}'] = znew[jxs,i1:i2+1]
     
     
     elif method == 'astro':
        # from Work/D_Emis/Timefactors/CAMS_TEMPO/scripts
        # tricky point was in S. Pacific, at j=286, i=506, lai=8.777
        # Looks bad if using std=10
        import emxmisc.astropy_convolve as ap
     
        #F f1= axf[0].imshow(boxvals,origin='lower')
     
        tst=pm.print_xymatrix(f'Orig',lons[idbg],lats[jxs],lons,lats,vals,nij=5)
        print('XSOUTOrig', xsout['Orig'][idbg:idbg+10])
        #axf[4].plot(xsec,vals[j,i1:i2+1],label=f'Orig')
     
        n=1
        #for std in [ 0.5, 1, 2, 5, 10 ]: # orig was 10
        for std in [ 0.5, 1, 2, 5, 10 ]: # orig was 10
          znew=ap.astro_conv2d(vals[:,:],stddev_x=std,stddev_y=0.5*std,dbg=False)
     
          #F f2= axf[n].imshow(boxvals,origin='lower')
          key=f'Std:{std}'
          xsout[key] = znew[jxs,i1:i2+1]
          tst=pm.print_xymatrix(key,lons[idbg],lats[jdbg],lons,lats,znew,nij=5)
     
          n += 1
          pmap.plotlonlatmap(lons,lats,znew,title=f'method:{method}{std}',levels=levs,cmap='Paired',
           img_bounds=[-179,179,-89,89],ofile=f'plotMaxLAI_{method}{std}.png')
     
        #F plt.colorbar(f1,shrink=0.8)
        #F plt.show()
   """
