#!/usr/bin/env python3
# Acton 2016 cites slw = 115 (Niinemets 1999)

def mgm2h_to_uggh(x,D=320.0,slw=115.0,lai=5):
   qD  = x/D            # now ug/g/h from D
   qL  = x/(lai*slw)    #     ug/g/h from SLW
   return 1.0e3*qD, 1.0e3*qL

# EPs in mg/m2/h at 30C, 1000 uE
oaks=dict(car_betu=2.25e-3,que_robu=2.39,que_rubr=0.914, que_pub_kalo=7.4, que_pub_baghi=5.4)

#for Is in [ 2.39, 0.914, 7.4, 5.4 ]:
print(f"{'Species':<14s} {'Is':>7s}  {'qD':>7s} {'qL':>7s}")
for spec, Is in  oaks.items(): # [ 2.39, 0.914, 7.4, 5.4 ]:
  qD, qL = mgm2h_to_uggh(Is)
  print(f"{spec:<14s} {Is:7.3f}  {qD:7.2f} {qL:7.2f}")
#q = 2.39   # tab 5 mg/m2/h
#meg = 13 # uggh
#print( 1000*q/(5*100), 1000*q/320.0, meg)

