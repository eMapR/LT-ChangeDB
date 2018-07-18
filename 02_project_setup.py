# -*- coding: utf-8 -*-
"""
Created on Mon Mar 05 11:23:22 2018

@author: braatenj
"""

import os
import sys
import time

# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)

import ltcdb

 
dirName = ltcdb.get_dir("Select or create and select a project head folder")

if dirName == '':
  sys.exit('A "project folder" was not selected')

startTime = time.time()

dirs = [
  os.path.join(dirName, 'timesync'),
  os.path.join(dirName, 'timesync', 'images'),
  os.path.join(dirName, 'timesync', 'prep'),
  os.path.join(dirName, 'raster'),
  os.path.join(dirName, 'vector'),
  os.path.join(dirName, 'scripts'),
  os.path.join(dirName, 'raster', 'prep'),
  os.path.join(dirName, 'raster', 'prep', 'gee_chunks'),            
  os.path.join(dirName, 'raster', 'landtrendr'),
  os.path.join(dirName, 'raster', 'landtrendr', 'segmentation'),
  os.path.join(dirName, 'raster', 'landtrendr', 'change')
]

for thisDir in dirs:
  if not os.path.exists(thisDir):
    os.makedirs(thisDir)
    
    
print('\nDone!')      
print("LT-GEE project setup took {} minutes".format(round((time.time() - startTime)/60, 1)))
