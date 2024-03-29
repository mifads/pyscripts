#!/usr/bin/env python3
""" call typically with "codetxt(__file__) from another script """
from datetime import date
import os

def codetxt(ifile=__file__):
  home=os.environ['HOME']
  src =    '%s'% os.path.basename(ifile)
  dir_path='%s'% os.path.dirname(os.path.realpath(ifile))
  dir_path = dir_path.replace(home,'~') # + '/%s'% os.path.basename(__file__)
  today = date.today()
  return '%s from %s on %s' % ( src, dir_path, today )
  #return 'Generated by %s from %s on %s' % ( src, dir_path, today )

if __name__ == '__main__':
  print(codetxt())
  testSub= """
   aaa bbb ccc %s
  """ % codetxt()
  print(testSub)
  #dir_path=os.path.dirname(os.path.realpath(__file__))

#FAILED  import lib_programname
#FAILED  print('LIB:', lib_programname.get_path_executed_script() )  # type: pathlib.Path
