#!/usr/bin/env python3
"""
From Geron 2001:
"""
SLM = 99.0  #  g/m2 = Leaf mass per unit area (i.e., specifc leaf mass, SLM, in g m2)

Q: rubra   30 nmole/m2/s         =>  67 ug C/g/h in Tab 1
             # nmol -> ug
ugCgh = 30 * 1.0e-9 * 60 * 1.0e6 / SLM * 3600

print(ugCgh) # 65 

