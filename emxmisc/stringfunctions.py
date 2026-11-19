#!/usr/bin/env python3
# -*- coding: utf8 -*-
import string
"""
  stringClean - Function to get rid of funny chars in names, e.g Bratt's Lake
  blankRemove - obvious ...
  multiwrite  - combines elements from an array with given format string
  endofpath   - grabs last n iterms from pathname
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
def multiwrite(a,fmt,sep=''):
  """ formats an array into a text string, with new f format using tips from
      https://realpython.com/how-to-python-f-string-format-float
  """
  fmt = fmt.replace('%','') # from old style to new f format
  return sep.join( f'{num:{fmt}}' for num in a )

#---------------------------------------------------------------------------- 
def endofpath(txt,n):
  """ grabs last n terms from pathname, e.g. dd/ee.txt from endofpath('aa/bb/dd/ee.txt',2) """
  from pathlib import Path
  return str(Path(*Path(txt).parts[-n:]))

#---------------------------------------------------------------------------- 
if __name__ == '__main__':
  strings = ( "Bratt's Lake" , "LÃ¼ckendorf", "Ã„htÃ¤ri", "mace  head" )
  for s in strings:
    print ("String clean ?? ", s, stringClean(s) )

  a = [ 1.2, 2.3, 4.5, 6.7 ]
  print( 'MultiWrite: ', multiwrite(a,'%7.2f') )
  print( 'MultiWrite: ', multiwrite(a[0:3],'%7.2f') )
  print( 'MultiWrite: ', multiwrite(a[0:3],'%7.2f',sep=',') )
  print( 'endofpath: ', endofpath('aa/bb/dd/ee.txt',2) )
  #OLD print( 'MultiWrite: ', multiwrite(a,', %7.2f') )
