#!/usr/bin/env python3
import numpy as np

def Daily2MeanValue(sday,eday,vals,dbg=False,overrunFrac=0.5):
   """ calculates mean for the given period from daily values. Copes with
      non-integer start and end day. 
      NOTE: As in Ebas, day numbers assumed to start from day 0 = 1/Jan
      If a requested period runs over the end of the year, by
      default we provide a model value if 50% of the period is covered.
      (user changeable.)
   """

   d1 =int(sday)
   d2 =int(eday)  #  allows
   ddays = eday - sday
   
   concSum = 0.0
   timeSum =0.0
   
   txt='ok'
   if eday < sday:  txt=' ERRROR! eday < sday'
   overrun = eday - len(vals)
   if overrun > 0:
    if overrunFrac*ddays: txt= 'FAILED: Overrun %7.1f Days' % overrun
    else: print('ALLOWED: overrun %7.1f Days' % overrun )

   # ie we have more than one day
#   if d2>d1 and drunover >  accept_runOverFrac * ddays:
#        txt=' period runs over end of model'

#       if d2 >=  len(vals):  txt='eday  after end of vals'

   if txt != 'ok':
      print('FAILED!! '+txt, sday, eday, overrun, d1, d2, len(vals) )
      return np.nan

   for jday in range(d1,d2):  # Assumed to start from day 0 = 1/Jan
     #day = min( jday, len(vals)-1 ) # to stop problems at end
     day = jday # , len(vals)-1 ) # to stop problems at end
     print( sday, eday, d1, d2, len(vals), day, eday-len(vals) )
     v= vals[day]

     if day ==  d1:
        dt= 1.0 - (sday-day)  # Often 0.25 or so, but not always
        if d2==d1: dt = 1.0   # Just use daily value
        case='A '
     elif day == d2 :
        dt= eday-day  # Often 0.25 or so, but not always
        case='B '
     else:
        dt=1.0
        case='C '
     #if dbg: print('D2: ', case, sday, eday, d1,d2, day, dt, v )
   
     concSum  += (dt*v)
     timeSum  += dt

     if dbg: print('D2%s: %6.2f%6.2f %3d %7.2f %8.2f %8.3f' % (  case, sday,eday, day, dt, timeSum,  v ))
   
   meanVal = concSum/timeSum
   if dbg: print('D2M:',sday, eday, 'timeSum ', timeSum, 'MEAN ',  meanVal )
   return meanVal
   
if __name__ == '__main__':
  vals = ( 0.0, 10.0, 20.0, 30.0,  40.0, 50.0, 60.0, 70.0 )
  sday = 3.29
  
  def testme(sday,eday,vals=vals):
     print('\nTesting sday, eday: ', sday, eday, \
     ' vals=', vals) # ( 0.0, 10.0, 20.0, 30.0,  40.0, 50.0, 60.0, 70.0 )
     m= Daily2MeanValue(sday,eday,vals,dbg=True)
     print('==> ', m)

  testme(sday,eday = 5.29)
  testme(sday,eday = 1.29)
  testme(sday,eday = 7.0)
  testme(sday,eday = 8.0)
  testme(sday=6,eday = 8.1)
  testme(sday=6,eday = 7.1)
  testme(sday=6,eday = 8.1)
  testme(sday=7,eday = 8.1)
  testme(sday=7,eday = 10.1)

#  print('\n Testing sday, eday: ', sday, eday)
#  m= Daily2MeanValue(sday,eday,vals,dbg=True)
#  eday = 1.59
#  print('\n Testing sday, eday: ', sday, eday)
#  m= Daily2MeanValue(sday,eday,vals,dbg=True)
#  eday = 7.0  
#  print('\n Testing sday, eday: ', sday, eday)
#  m= Daily2MeanValue(sday,eday,vals,dbg=True)
#  eday = 8.0  
#  print('\n Testing sday, eday: ', sday, eday)
#  m= Daily2MeanValue(sday,eday,vals,dbg=True)
#  sday = 7.0  
#  print('\n Testing sday, eday: ', sday, eday)
#  m= Daily2MeanValue(sday,eday,vals,dbg=True)
#  eday = 8.1  
#  print('\n Testing sday, eday: ', sday, eday)
#  print('vals=', vals) # ( 0.0, 10.0, 20.0, 30.0,  40.0, 50.0, 60.0, 70.0 )
#  m= Daily2MeanValue(sday,eday,vals,dbg=True)
