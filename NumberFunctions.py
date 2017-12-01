#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
  Simple numerical functions to help remember what to do

    round_int - equivalent to nint. Copes with negative numbers
                which int ot int(x+0.5) gets wrong
"""

def round_int(x):
      return int(round(x))


