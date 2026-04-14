#!/usr/bin/env python3
#https://stackoverflow.com/questions/36074074/smooth-circular-data
import numpy as np
import matplotlib.pyplot as plt

def circle_smooth2(y,plots=False):
  print(y)
  pre = np.roll(y,-1)
  print(pre)
  pos = np.roll(y,+1)
  print(pos)
  new= (pre+y+pos)/3.0
  print('New:', new)
  x = list(range(1,len(y)+1))
  #plt.plot(y,label='Orig')
  #plt.plot(new,label='smooth2')
  plt.bar(x,y,label='Orig')
  plt.bar(x,new,label='smooth2')
  plt.title('Smooth2')
  plt.show()
  plt.clf()
  return new

def circle_smooth(y,plots=False):
  """ Assigns 25% of month m to m-1 and 25% to m+1
      Returns new array """
  yL=0.25*np.roll(y,-1)
  yR=0.25*np.roll(y,+1)
  yn = 0.5 *  y
  yf= (yn + yL + yR) 
  #print(np.sum(y), np.sum(yf) )
  xx = np.array(range(1,len(y)+1))
  if plots:
    #plt.plot(y,label='Orig')
    #plt.plot(yL,label='Left')
    #plt.plot(yR,label='Right')
    #plt.plot(yf,ls='--',label='New')
    #plt.legend()
    #plt.show()
    #plt.clf()
    print('XX', len(xx), len(y), xx)
    plt.step(xx,y,label='Orig') #,color='none',edgecolor='r',width=1.0)
    plt.step(xx+0.1,yf+0.1,ls='--',label='New') #,color='none',edgecolor='r',width=1.0)
    plt.legend()
    plt.show()
  return yf
#yf = yf * np.sum(y)/np.sum(yf)


if __name__ == '__main__':
  x=range(12)
  y=np.zeros(12)
  y[2] = 5.0
  y[2:] = 5.0
  new=circle_smooth(y,plots=True)
  new2=circle_smooth2(y,plots=True)
  print(np.sum(y), np.sum(new), np.sum(new2) )

#yy = np.concatenate((y, y))
#smoothed = np.convolve(np.array([1] * 5), yy)[5: len(x) + 5]

