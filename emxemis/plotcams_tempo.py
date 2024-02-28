#!/usr/bin/env python3
import matplotlib.pyplot as plt
gnfrC= [0.3830,0.3010,0.2670,0.1980,0.2200,0.3700,0.4490,0.4090,0.4180,0.3990,0.3280,0.2960,0.2760,0.6260,0.6810,0.9820,1.5640,2.8990,3.2120,3.0250,2.5290,1.8980,1.7090,0.5610 ]
plt.plot(gnfrC)
plt.ylim(0.0)
plt.title('GNFR C diurnal profile, CAMS-TEMPO v3.2')
#plt.show()
plt.savefig('Plot_cams_tempo_gnfrC.png')

