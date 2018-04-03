# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 14:48:18 2018

@author: braatenj
"""

import os
from rasterstats import zonal_stats
from glob import glob
import numpy as np
import pandas as pd
import fiona
from shapely.geometry import shape
import math
import sys
import subprocess 





# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb

# get the polygon directory
polyDir = ltcdb.get_dir("Select a folder that contains LT change polgyon files\n\n(*\\raster\\landtrendr\\change\\*\\polygon)")
if polyDir == '':
  sys.exit('ERROR: No folder containing LT change polgyon files files was selected.\nPlease re-run the script and select a folder.')


# get the annual polygon files
polyFiles = glob(os.path.join(polyDir,'*.shp'))

# get the attribute list file
attributeList = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-change_attributes.csv"


print('\nAdding disturbance attributes to the shapefile table...\n')

attrList = np.genfromtxt(attributeList, delimiter=',', dtype='object')
info = ltcdb.get_info(os.path.basename(attributeList))
bandIndex =  ltcdb.year_to_band(os.path.basename(attributeList))
indexID = info['indexID']

# loop through the polygons
for fn, polyFile in enumerate(polyFiles):
  #polyFile = polyFiles[8]
  year = int(os.path.splitext(os.path.basename(polyFile))[0])
  print('Working on year: '+str(fn+1)+'/'+str(len(polyFiles))+' ('+str(year)+')')
  band = bandIndex[year]  
  fullDF = pd.DataFrame()
  for attr in attrList:
    #attr = attrList[1,]
    attrBname = attr[1]
    print('    attribute: '+attrBname)
    stats = zonal_stats(polyFile, attr[0], band=band, stats=['mean', 'std'])
    statsDF = pd.DataFrame.from_dict(stats).round().astype(int)
    statsDF.columns = [attrBname+'Mean', attrBname+'Std']
    fullDF = pd.concat([fullDF, statsDF], axis=1)
  
  # make a temp dir to hold the new file
  tmpDir = os.path.join(os.path.dirname(polyFile),'tmp')
  newPolyFile = os.path.join(tmpDir, os.path.basename(polyFile))
  if not os.path.exists(tmpDir):
    os.mkdir(tmpDir) 
  
  # open the polygon file to use as a template for adding new info
  with fiona.open(polyFile, 'r') as src:
    # make a copy of the schema
    schema = src.schema.copy()
    
    # add fields to the schema
    schema['properties']['index'] = 'str:10'
    schema['properties']['annualID'] = 'int:10'
    schema['properties']['uniqID'] = 'str:20'
    
    for col in fullDF.columns:
      schema['properties'][col] = 'int:6'
    
    schema['properties']['area'] = 'int:10'
    schema['properties']['perim'] = 'int:10'
    schema['properties']['shape'] = 'float'
    
    # copy info as template for the new polgon file
    crs = src.crs
    driver = src.driver
    
    # open the new shapefile for writing to using info from the source polygon file
    with fiona.open(newPolyFile, 'w', crs=crs, driver=driver, schema=schema) as poly:
      # loop through all the features
      for i, feature in enumerate(src):
        # add all the attributes from the attribute list
        for col in fullDF.columns:
          feature['properties'][col] = fullDF.loc[i, col]        
        
        # add the id attributes
        annualID = i+1
        feature['properties']['annualID'] = annualID 
        feature['properties']['index'] = indexID
        feature['properties']['uniqID'] = indexID+str(year)+str(annualID)
        
        # add the shape attributes
        geom = shape(feature['geometry'])
        area = geom.area
        areaCircle = math.sqrt(area/math.pi)*2*math.pi # use the area as a circle as the standard for most simple
        perim = geom.length
        pa = round(perim/areaCircle, 6)
        feature['properties']['area'] = area 
        feature['properties']['perim'] = perim
        feature['properties']['shape'] = pa
        
        # write the feature to disk 
        poly.write(feature)

shpFiles = glob(os.path.join(tmpDir,'*.shp'))     

# check if there are shpFiles
if len(shpFiles) == 0:
  sys.exit('ERROR: No .shp files were found in directory: '+tmpDir)

# merge the polygons
vectorDir = os.path.normpath(os.path.join(polyDir, os.sep.join([os.pardir]*5), 'vector'))
bname = info['name']
mergedPolyOutPath = os.path.join(vectorDir, bname+'-dist_info.shp')

mergeCmd = 'ogr2ogr -f "ESRI Shapefile" ' + mergedPolyOutPath + ' ' + shpFiles[0]
subprocess.call(mergeCmd, shell=True)

for i in range(1,len(shpFiles)):
  mergeCmd = 'ogr2ogr -f "ESRI Shapefile" -append -update ' + mergedPolyOutPath + ' ' + shpFiles[i]  
  subprocess.call(mergeCmd, shell=True)




changeDBfile = os.path.join(os.path.dirname(mergedPolyOutPath),'test.sqlite')
convertCmd = 'ogr2ogr -f "SQLite" -nlt PROMOTE_TO_MULTI -nln NBR -dsco SPATIALITE=YES ' + changeDBfile + ' ' + mergedPolyOutPath  
subprocess.call(convertCmd, shell=True)








   