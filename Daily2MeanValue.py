#!/usr/bin/env python3

def Daily2MeanValue(sday,eday,vals,dbg=False):
   """ calculates mean for the given period from daily values. Copes with
      non-integer start and end day. 
   """

   d1 =int(sday)
   d2 =int(eday)  #  allows
   dd = eday - sday
   
   concSum = 0.0
   timeSum =0.0
   
   for day in range(d1,d2+1):  # Assumed to styart from day 0 = 1/Jan
     v= vals[day]
     if day ==  d1:
        dt= 1.0 - (sday-day)  # Often 0.25 or so, but not always
        if d2==d1: dt = 1.0   # Just use daily value
        valThisDay = dt * v
     elif day == d2 :
        dt= eday-day  # Often 0.25 or so, but not always
        valThisDay = dt * v
     else:
        dt=1.0
        valThisDay = v
   
     concSum  += dt*valThisDay
     timeSum  += dt
     if dbg: print( '%3d %7.2f %8.2f %8.3f %8.3f' % (  day, dt, 
                      timeSum, valThisDay, vals[day] ))
   
   meanVal = concSum/timeSum
   if dbg: print(sday, eday, 'timeSum ', timeSum, 'MEAN ',  meanVal )
   return meanVal
   
if __name__ == '__main__':
  vals = ( 0.0, 10.0, 20.0, 30.0,  40.0, 50.0, 60.0, 70.0 )
  sday = 1.29
  
  eday = 4.29
  m1= Daily2MeanValue(sday,eday,vals,dbg=True)
  eday = 1.59
  m2= Daily2MeanValue(sday,eday,vals,dbg=True)
