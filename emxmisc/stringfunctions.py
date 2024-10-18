#!/usr/bin/env python3
# -*- coding: utf8 -*-
import string
"""
  stringClean - Function to get rid of funny chars in names, e.g Bratt's Lake
  blankRemove - obvious ...
  multiwrite  - combines elements from an array with given format string
"""

#---------------------------------------------------------------------------- 
valid_chars = "-_. %s%s" % ( string.ascii_letters, string.digits )
def stringClean(str):
  nstr = str.strip().replace(' ','_') # Use _ for spaces
  return ''.join( c for c in nstr if c in valid_chars)
#---------------------------------------------------------------------------- 
def blankRemove(str):
  nstr = str.replace(' ','_') # Use _ for spaces
  return ''.join( c for c in nstr)

#---------------------------------------------------------------------------- 
def multiwrite(a,fmt):
 """ formats an array into a text string, with new f format using tips from
      https://realpython.com/how-to-python-f-string-format-float """
  fmt = fmt.replace('%','') # from old style to new f format
  return "".join( f'{num:{fmt}}' for num in a )
#OLD  return "".join( fmt%num for num in a )

#---------------------------------------------------------------------------- 
if __name__ == '__main__':
  strings = ( "Bratt's Lake" , "LÃ¼ckendorf", "Ã„htÃ¤ri", "mace  head" )
  for s in strings:
    print ("String clean ?? ", s, stringClean(s) )

  a = [ 1.2, 2.3, 4.5, 6.7 ]
  print( 'MultiWrite: ', multiwrite(a,'%7.2f') )
  print( 'MultiWrite: ', multiwrite(a[0:3],'%7.2f') )
