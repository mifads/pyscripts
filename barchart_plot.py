#!/usr/bin/env python3
import matplotlib.pyplot as plt
import pandas as pd

b=pd.read_csv('barchart_data.csv')
#all:b.plot.bar(x='ISO3',rot=60.0)
b.plot.bar(x='ISO3',y=['Ref1','Ref2'],rot=60.0)
plt.tight_layout()
plt.show()

