#!/usr/bin/env python3
"""
Simple but useful script to print out daynumbers at the start
of each month. The user is left to add one themselves in the
case of leap-years
"""

print(__doc__)
days = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
jd=0
for m in range(12):
    print(m+1, jd )
    for dd in range(days[m]):
        jd += 1

