#!/usr/bin/env python3
import numpy as np

def distancePoint2line(x0,y0,a,b,c):
  """ distance from point xp, yp to line ax + by + c = 0 
      using formula from
      https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
  """

  d =  np.abs( a*x0 + b * y0 + c )/ np.sqrt( a*a + b*b )
  return d

if __name__ == '__main__':

# Test regression line, y = 1.1 x + c
# Re-arranges to:  1.1 x -y + c = 0, or a=1.1, b = -1, c = 0.0

  print('dist ', distancePoint2line( 20.0,50.0,1.1,-1.0,0.0) )
