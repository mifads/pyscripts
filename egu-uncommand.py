#!/usr/bin/env python3
# some help from https://www.codeconvert.ai/perl-to-python-converter
import re
import sys

# careful with order. Take simplest last (e-g- \deg) among
# similar commands
cmds = {
   r'\ugN'      : r'\unit{\mu g(N)~m^{-3}}'
  ,r'\ug'      : r'\unit{\mu g~m^{-3}}'
  ,r'\degrees' : r'\unit{^\circ}'
  ,r'\degC'    : r'\unit{^\circ C}'
  ,r'\deg'     : r'\unit{^\circ}'
  ,r'\pmfine'  : r'PM$_{2.5}$'
  ,r'\pmten'   : r'PM$_{10}$'
  ,r'\ResEqPtOne'   : r'\ensuremath{0.1^\circ \times 0.1^\circ}' 
  ,r'\BLUE'   : r'\color{Blue}'
  ,r'\GREEN'   : r'\color{Green}'
  ,r'\ORANGE'   : r'\color{Orange}'
}

# had to hard.edit ResEq and ignore GREEN etc

with open(sys.argv[1],'r') as f:
  for line in f.readlines():
    #line = input()
    for old, new in cmds.items():
      if line.startswith('%'):
       pass
      elif r'\newcommand' in line and old in line:
       line = '%NONEW:' + line
      else:
       line = line.replace(r'%s'%old, r'%s'%new)
    #line = line.replace(r'\ug', cmds[r'\ug'])
    print(line,end='')

#with open('TESTR.tex','r') as f:
#  for line in f.readlines():
#    xline = re.sub(r'\\ug \b', '$\\mu$g~m^{-3}', line)
#    print(xline)


