#!/usr/bin/env python3
import jdcal

d1= sum( jdcal.gcal2jd(2018,3,8) )
d2= sum( jdcal.gcal2jd(2011,11,10) )
print(d1, d2, d2-d1)
