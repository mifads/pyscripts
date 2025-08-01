#!/usr/bin/env python3
# www.codeconvert.ai/perl-to-python-converter
# tips from https://stackoverflow.com/questions/15260652/how-do-i-replace-multiple-spaces-with-just-one-character

import sys
import re

print(sys.argv)
if sys.argv[1] != '<':
  sys.exit('ERROR!! Need to use <')

for line in sys.stdin:
    line = line.strip()
    #line = line.replace(" ", ",")
    #FAILS:  line = re.sub("\s+", ",",line)
    #print(line)
    print(','.join(line.split()) )
#    print()

