#!/usr/bin/env python3
import emxgeo.check_coord_deltas as cc
#-----------------------------------------------------------------------------
def find_coord_index(crds,crd):
  dc=cc.check_coord_deltas(crds)
  crd0= crds[0]-0.5*dc
  return int( (crd-crd0)/dc )

