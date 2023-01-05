# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 14:25:47 2019

@author: braatenj
"""


def get_delta(vertVals):
  segStartVal = vertVals[:-1]
  segEndVal = vertVals[1:]
  segDelta = segEndVal - segStartVal
  return segDelta

def get_dur(vertYrs):
  segStartYr = vertYrs[:-1]
  segEndYr = vertYrs[1:]
  segDur = segEndYr - segStartYr
  return segDur



thresh = 1.5

vertYrs = np.array([1984 , 1990 , 1991 , 1992 ,1993 ,2017])
npFitIDX = np.array([-700, -700 , -350 , -100 ,-50   ,-700])

vertYrs = np.array([2010 , 2011 , 2012])
npFitIDX = np.array([-801, -156 , -42 ])



def collapse_segs(vertYrs, npFitIDX, thresh):
  vertIndex = np.where(vertYrs != 0)[0]
  if len(vertIndex) > 2:
    check = True
    while check:
      vertYrsTemp = vertYrs[vertIndex]
      vertValsIDXTemp = npFitIDX[vertIndex]
      segMagIDXTemp = get_delta(vertValsIDXTemp).astype(float) 
      segDurTemp = get_dur(vertYrsTemp).astype(float) 
      slope = np.divide(segMagIDXTemp, segDurTemp)
      print(slope)
      checkLen = len(segMagIDXTemp)-1
      for i in range(checkLen):
        if np.sign(slope[i]) == np.sign(slope[i+1]):  # -1, 0, 1
          dif = abs(abs(slope[i] - slope[i+1])/((slope[i] + slope[i+1])/2.0))
          print(dif)
          if dif < thresh:
            print('collapse')
            vertIndex = np.delete(vertIndex, i+1)
            break
      if i == checkLen-1:
        check = False
  return(vertIndex)

test = collapse_segs(vertYrs, npFitIDX, thresh) 


abs(-807 )/((500 + 400)/2.0)



"""
The difference between the slopes of consecutive change segments relative to the mean of the two slopes. Is the difference 2 times the mean slope?
Is it 0.25 (1/4) of the mean slope 



"""








