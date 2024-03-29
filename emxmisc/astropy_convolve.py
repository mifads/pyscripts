#!/usr/bin/env python3
""" 1d and 2d convolve functions, with loosely designed defaults for emep
  Orig: We smooth with a Gaussian kernel with x_stddev=1 (and y_stddev=1)
  It is a 9x9 array for x_stddev=1
  btw, x_size: Size in x direction of the kernel array. Default = ⌊8*stddev + 1⌋.
"""
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from astropy.convolution import Gaussian1DKernel, Gaussian2DKernel, convolve #NO:, convolve_fft
from scipy.ndimage import convolve as scipy_convolve
import emxmisc.stringfunctions as sf
import sys

def astro_conv1d(vals,kernel=[0.2,0.6,0.2],boundary='wrap'):
  """ 1-d convolve. If kernel is supplied as list, use as-is. If a scalar
    is given, use as std-dev """

  if np.isscalar(kernel):  # if just number, use as std-dev
    kernel=Gaussian1DKernel(kernel)
  return convolve(vals,kernel=kernel,boundary=boundary)


def astro_conv2d(vals,stddev_x=0.5,stddev_y=0.25,dbg=False):
  """ 2-d convolve. Default uses x_std = 2*y_std to loosely account for lon/lat
  Methods from:
   https://docs.astropy.org/en/stable/convolution/  index-1.py
   We also create a copy of the data and set those NaNs to zero.  We will
   use this for the scipy convolution
  """ 

  img_zerod = vals.copy()
  img_zerod[np.isnan(vals)] = 0
  
  kernel = Gaussian2DKernel(x_stddev=stddev_x,y_stddev=stddev_x,mode='center') # DS TEST 1)
  # Convolution: scipy's direct convolution mode spreads out NaNs (see
  # panel 2 in link)

  scipy_conv = scipy_convolve(vals, kernel)
  
  # scipy's direct convolution mode run on the 'zero'd' image will not
  # have NaNs, but will have some very low value zones where the NaNs were
  # (see panel 3 in link)

  scipy_conv_zerod = scipy_convolve(img_zerod, kernel)
  
  # astropy's convolution replaces the NaN pixels with a kernel-weighted
  # interpolation from their neighbors
  #astropy_conv = convolve_fft(vals, kernel,boundary='wrap')  # _fft for speed

  astropy_conv = convolve(vals, kernel,boundary='wrap')  # _fft for speed

  #astropy_conv = convolve(vals, kernel)  # _fft for speed produced zeros, not NaN

  diffs=astropy_conv-vals
  diffs[np.abs(diffs)<1.0e-6] = np.nan

  if dbg:
    # dbg along lattitude for GLOBAL05
    j0=1291; i0=1695; i1=1709 # Into SPain

    print('Dbg zerod', img_zerod[j0,i0:i1])
    print('Dbg scipy_conv', scipy_conv[j0,i0:i1])
    print('Dbg conv_zerod', scipy_conv_zerod[j0,i0:i1])
    print('Dbg astropy_conv', astropy_conv[j0,i0:i1])
    print('Dbg diffs', diffs[j0,i0:i1])
    
  return astropy_conv

if __name__ == '__main__':
  y=np.ones(12)
  z=np.ones(12)
  y[11] = 20.0
  z[9] = 20.0
  print('Orig:', sf.multiwrite( y, '%8.3f'   )  )
  print('Def.:',  sf.multiwrite( astro_conv1d(y, [0.2, 0.6, 0.2]) , '%8.3f'   )  )
  print('70%.:',  sf.multiwrite( astro_conv1d(y, [0.15, 0.7, 0.15]) , '%8.3f'   )  )
  print('50%.:',  sf.multiwrite( astro_conv1d(y, [0.25, 0.5, 0.25]) , '%8.3f'   )  )
  print('nowr:',  sf.multiwrite( astro_conv1d(y, [0.2, 0.6, 0.2],boundary=None) , '%8.3f'   ), '   =Weird!'  )
  for std in [ 0.2, 0.3, 0.4, 0.5, 0.8, 1, 2 ]:
    print( '%4.1f:' % std, sf.multiwrite( astro_conv1d(y,std) , '%8.3f'   )  )

  # test sums?
  yc=astro_conv1d(y,0.8)
  zc=astro_conv1d(z,0.8)
  print( 'y0.8:', sf.multiwrite( yc , '%8.3f'   )  )
  print( 'z0.8:', sf.multiwrite( zc , '%8.3f'   )  )
  print( 's0.8:', sf.multiwrite( yc+zc , '%8.3f'   )  )


