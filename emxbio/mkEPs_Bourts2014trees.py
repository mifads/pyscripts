#!/usr/bin/env python3
from math import exp
import emxbio.getG93 as g93
""" Bourtsoukidis-Trees2024eb.pdf, saplings in pots 
    Quercus robur and Prunus serotina, Trees, DOI 10.1007/s00468-013-0942-5
    ca 18 month old seedlings, in pots """
T=20.0

f = exp(0.09*(10.0)) # =2.46,  20 to 30C, with MT equan
f2 = exp(0.14*(10.0)) # sqt maybe?
fIso = g93.getG93isoCt(30.0)/g93.getG93isoCt(20.0)
fmt  = g93.getG93mtCt(30.0)/g93.getG93mtCt(20.0)
fsqt = g93.getG93mtCt(30.0,beta=0.14)/g93.getG93mtCt(20.0,beta=0.14) # test


# Q.robur
Is  = 2.2071; mt = 0.043; sqt = 0.014
print(f"Is: {fIso*2.21:.2f} MT: {fmt*0.043:.2f} SQT: {fmt*0.014:.2f} {sqt/mt:.2f} {sqt*fsqt/mt/fmt:.2f}") 


