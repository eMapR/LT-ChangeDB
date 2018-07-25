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
import time 





# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb



headDir = ltcdb.get_dir("Select the project head folder", scriptDname)

#headDir = r'D:\work\proj\al\gee_test\test'


if headDir == '':
  sys.exit('ERROR: No folder containing LT-GEE files was selected.\nPlease re-run the script and select a folder.')

vectorDir = os.path.join(headDir, 'vector', 'change')
if not os.path.isdir(vectorDir):
  sys.exit('ERROR: Can\'t find the vector folder.\nTrying to find it at this location: '+vectorDir+'\nIt\'s possible you provided an incorrect project head folder.\nPlease re-run the script and select the project head folder.')

# could try to find the gee_chunk folder
#[x[0] for x in os.walk(chunkDir)]

#segDir = r'D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation'
ltRunDirs = [os.path.join(vectorDir, thisRunDir) for thisRunDir in os.listdir(vectorDir)]

# make sure the dirs exist
for polyDir in ltRunDirs:
  if not os.path.isdir(polyDir):
    sys.exit('ERROR: Can\'t find the polygon folder.\nTrying to find it at this location: '+polyDir+'\nIt\'s possible you did not run the 06_make_polygons.py file.\nPlease run the script and try again.')


startTime = time.time()

firstTime = 0
for polyDir in ltRunDirs:

  # get the polygon directory
  #polyDir = ltcdb.get_dir("Select a folder that contains LT change polgyon files\n\n(*\\raster\\landtrendr\\change\\*\\polygon)")
  #if polyDir == '':
  #  sys.exit('ERROR: No folder containing LT change polgyon files files was selected.\nPlease re-run the script and select a folder.')
  
  
  # get the annual polygon files
  polyFiles = glob(os.path.join(polyDir,'*.shp'))
  if len(polyFiles) == 0:
    sys.exit('ERROR: There was no *.shp files in the folder selected.\nPlease fix this.')
  
  attributeList = glob(os.path.join(polyDir,'*.csv'))[0]
  
  if len(attributeList) != 1:
    sys.exit('ERROR: There was no *.csv file in the folder selected.\nPlease fix this.') 
  attributeList = attributeList[0]
  
  # get the attribute list file
  #attributeList = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-change_attributes.csv"
  #polyDir = r'D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\polygon'
  #attributeList = glob(os.path.join(polyDir, os.pardir, '*attributes.csv'))[0]
  
  # TODO check if there are more than one
  # TODO check if it exits
  
  
  print('\nAdding disturbance attributes to the shapefile table...\n')
  
  attrList = np.genfromtxt(attributeList, delimiter=',', dtype='object')
  info = ltcdb.get_info(os.path.basename(attributeList))
  bandIndex =  ltcdb.year_to_band(os.path.basename(attributeList), -1) # adjust this by -1 band because disturbance layers are n-1
  indexID = info['indexID']
  
  
   # make a temp dir to hold the new file
  tmpDir = os.path.join(polyDir,'tmp')
  if not os.path.exists(tmpDir):
    os.mkdir(tmpDir) 
  
  
  # loop through the polygons
  for fn, polyFile in enumerate(polyFiles):
    #polyFile = polyFiles[8]
    newPolyFile = os.path.join(tmpDir, os.path.basename(polyFile))
    year = int(os.path.splitext(os.path.basename(polyFile))[0][-4:])    
    print('Working on year: '+str(fn+1)+'/'+str(len(polyFiles))+' ('+str(year)+')')
    band = bandIndex[year]  
    fullDF = pd.DataFrame()
    for attr in attrList:
      #attr = attrList[1,]
      attrBname = attr[1]
      print('    attribute: '+attrBname)
      stats = zonal_stats(polyFile, attr[0], band=band, stats=['mean', 'std'])
      statsDF = pd.DataFrame.from_dict(stats).round().astype(int)
      statsDF.columns = [attrBname+'Mn', attrBname+'Sd']
      fullDF = pd.concat([fullDF, statsDF], axis=1)
    

    
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
  mergedPolyOutPath = os.path.join(tmpDir, os.path.splitext(os.path.basename(shpFiles[0]))[0][:-4]+'merged.shp')
  
  mergeCmd = 'ogr2ogr -f "ESRI Shapefile" ' + mergedPolyOutPath + ' ' + shpFiles[0]
  subprocess.call(mergeCmd, shell=True)
  
  for i in range(1,len(shpFiles)):
    mergeCmd = 'ogr2ogr -f "ESRI Shapefile" -append -update ' + mergedPolyOutPath + ' ' + shpFiles[i]  
    subprocess.call(mergeCmd, shell=True)
  
  # delete the original files
  search = os.path.basename(os.path.splitext(polyFile)[0])[:-4]+'*'
  shpFiles = glob(os.path.join(polyDir,search))
  extract = [i for i, thisFn in enumerate(shpFiles) if '.tif' not in thisFn]
  shpFiles = [shpFiles[i] for i in extract]
  for fn in shpFiles:
    os.remove(fn)
    

  # create/add to the database 
  if firstTime == 0:
    changeDBfile = os.path.join(vectorDir,'lt_change_database.sqlite')
    convertCmd = 'ogr2ogr -f "SQLite" -nlt PROMOTE_TO_MULTI -nln '+indexID+' -dsco SPATIALITE=YES ' + changeDBfile + ' ' + mergedPolyOutPath  
    firstTime += 1
  else:
    convertCmd = 'ogr2ogr -f "SQLite" -nlt PROMOTE_TO_MULTI -nln '+indexID+' -dsco SPATIALITE=YES -update ' + changeDBfile + ' ' + mergedPolyOutPath  

  subprocess.call(convertCmd, shell=True)
  
  # move the filled polys
  shpFiles = glob(os.path.join(tmpDir,'*'))     
  newShpFiles = [os.path.join(polyDir, os.path.basename(fn)) for fn in shpFiles]
  for old, new in zip(shpFiles, newShpFiles):
    os.rename(old, new)
    
  os.rmdir(tmpDir)
  

print('\nDone!')      
print("Appending zonal stats took {} minutes".format(round((time.time() - startTime)/60, 1)))  
  
  
  
     