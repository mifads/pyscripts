#!/usr/bin/env python3
import zxcvbn

text=input("Give pwd\n")
res=zxcvbn.zxcvbn(text)

for p in 'score crack_times_display'.split():

  print(p, res[p])
