#!/usr/bin/env python

"""Distance helpers."""
 
import math
 
 
EARTH_RAD = 6378137.0     # earth circumference in meters
 
 
def great_circle_distance(latlong_a, latlong_b):
    """
    >>> coord_pairs = [
    ...     # between eighth and 31st and eighth and 30th
    ...     [(40.750307,-73.994819), (40.749641,-73.99527)],
    ...     # sanfran to NYC ~2568 miles
    ...     [(37.784750,-122.421180), (40.714585,-74.007202)],
    ...     # about 10 feet apart
    ...     [(40.714732,-74.008091), (40.714753,-74.008074)],
    ...     # inches apart
    ...     [(40.754850,-73.975560), (40.754851,-73.975561)],
    ... ]
    
    >>> for pair in coord_pairs:
    ...     great_circle_distance(pair[0], pair[1]) # doctest: +ELLIPSIS
    83.325362855055...
    4133342.6554530...
    2.7426970360283...
    0.1396525521278...
    """
    lat1, lon1 = latlong_a
    lat2, lon2 = latlong_b
 
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
            math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = EARTH_RAD * c
    
    return d


if ( __name__ == '__main__' ):
  print("1deg@60N EW", great_circle_distance(latlong_a=( 60.0,0.0), latlong_b=( 60.0,1.0)))
  print("1deg@60N NS", great_circle_distance(latlong_a=( 60.0,0.0), latlong_b=( 61.0,0.0)))
  print("1deg 45EW", great_circle_distance(latlong_a=( 45.0,0.0), latlong_b=( 45.0,1.0)))
  print("1deg@45 NS", great_circle_distance(latlong_a=( 45.0,0.0), latlong_b=( 46.0,0.0)))

