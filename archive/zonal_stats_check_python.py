# -*- coding: utf-8 -*-
"""
Created on Mon Apr 02 10:21:15 2018

@author: braatenj
"""

from osgeo import gdal
import numpy as np

fn = r"D:\work\temp\junk\PARK_CODE-MORA-NBR-7-19842017-06010930-change_idx_mag_b6_1990_masked.tif"
src = gdal.Open(fn)
srcBand = src.GetRasterBand(1)
data = srcBand.ReadAsArray()
data = data[np.where(data != 0)]

count = data.shape
print('count: ' +str(count))
mean = np.mean(data)
print('mean: ' +str(mean))
sum = np.sum(data)
print('sum: ' +str(sum))
median = np.median(data)
print('median: ' +str(median))
std = np.std(data)
print('std: ' +str(std))
min = np.min(data)
print('min: ' +str(min))
max = np.max(data)
print('max: ' +str(max))




