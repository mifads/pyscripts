#!/usr/bin/env python
"""
  code to print equations which are formatted in the EMEP GenChem notation,
  skipping comments and blank lines.
"""
import sys

#ifile='VBS_POAageing.reactions'

with open(sys.argv[1]) as f:
#with open(ifile) as f:
  for row in f:
    if row.startswith('*'): continue
    if  not ';' in row: continue # blank lines
    semicolon=row.index(';')
    print(row[:semicolon])
