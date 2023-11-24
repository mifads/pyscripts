#!/usr/bin/env python3
import os
import sys
import subprocess
#from subprocess import *

#print(sys.argv)
#srchlist=[ 'locate' ] + sys.argv[1:]
#print(srchlist)
#sys.exit()
args=["locate"]
if '-i' in sys.argv: args=["locate", "-i"]
args = args + [sys.argv[1]] 
#s=subprocess.run(["locate"] + [ sys.argv[1]] ,stdout=subprocess.PIPE)
#s=subprocess.run(["locate"] + ["-i"] + [ sys.argv[1]] ,stdout=subprocess.PIPE)
s=subprocess.run(args,stdout=subprocess.PIPE)
res=s.stdout.split()

anycase = False
if '-i' in  sys.argv:
  anycase = True
  sys.argv.remove('-i')

if '-x' in sys.argv:
  ix=sys.argv.index('-x')
  wanted = sys.argv[1:ix]
  notwanted = sys.argv[ix+1:]
else:
  wanted = sys.argv[1:]
  notwanted = []

xres =res.copy()
if anycase:
  wanted = [ w.lower() for w in wanted ]
  notwanted = [ w.lower() for w in notwanted ]
  #res =    [ w.lower() for w in res ]
   
#print('AA',wanted)

for r in xres:
  #rtxt = r.decode('utf-8')
  rtxt = r.decode('latin1') # less fussy!
  xtxt = rtxt
  if anycase:  xtxt = xtxt.lower()
  
  matches=True  
  for i in wanted:
      #print('XTXT', i, xtxt)
      if i not in xtxt:
         matches=False
         #print('TESTF ', xtxt, i, matches )
      #"else:
         #print('TESTP ', xtxt, i, matches )

  for i in notwanted:
     #print('XX', i, xtxt)
     if i in xtxt:
         matches=False

  if matches:
      print('LOC:', rtxt)
  #else:
  #    print('NO', rtxt)

if __name__ == '__main__':
   sys.argv='Bvoc Region DEP'.split()

#for i in args 
