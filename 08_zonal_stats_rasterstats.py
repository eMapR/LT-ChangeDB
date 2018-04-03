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





# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb


shpFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\polygon\1993.shp"
rasterFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-change_idx_mag.tif"




polyDir = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\polygon"

# get the annual polygon files
polyFiles = glob(os.path.join(polyDir,'*.shp'))

# get the attribute list file
attributeList = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-change_attributes.csv"


print('\nAdding disturbance attributes to the shapefile table...\n')


layer = add_field(layer, 'annualID', ogr.OFTInteger)
layer = add_field(layer, 'index', ogr.OFTString)
layer = add_field(layer, 'uniqueID', ogr.OFTString)
layer = add_field(layer, 'area', ogr.OFTInteger)
layer = add_field(layer, 'perim', ogr.OFTInteger)
layer = add_field(layer, 'shape', ogr.OFTReal)



attrList = np.genfromtxt(attributeList, delimiter=',', dtype='object')
info = ltcdb.get_info(attributeList)
bandIndex =  ltcdb.year_to_band(os.path.basename(attributeList))

# loop through the polygons
for fn, polyFile in enumerate(polyFiles):
  fn=9
  polyFile = polyFiles[8]
  year = int(os.path.splitext(os.path.basename(polyFile))[0])
  print('Working on year: '+str(fn+1)+'/'+str(len(polyFiles))+' ('+str(year)+')')
  band = bandIndex[year]  
  fullDF = pd.DataFrame()
  for attr in attrList:
    #attr = attrList[1,]
    attrBname = attr[1]
    print('    ...attribute: '+attrBname)
    stats = zonal_stats(polyFile, attr[0], band=band, stats=['mean', 'std'])
    statsDF = pd.DataFrame.from_dict(stats).round().astype(int)
    statsDF.columns = [attrBname+'Mean', attrBname+'Std']
    fullDF = pd.concat([fullDF, statsDF], axis=1)
  
  # make a temp dir to hold the new file
  tmpDir = os.path.join(os.path.dirname(polyFile),'tmp')
  newPolyFile = os.path.join(tmpDir, os.path.basename(polyFile))
  if not os.path.exists(tmpDir):
    os.mkdir(tmpDir) 
  
  # make a copy of the poly file and fill it with attributes
  with fiona.open(polyFile, 'r') as src:
    schema = src.schema.copy()
    for col in fullDF.columns:
      schema['properties'][col] = 'int:6'
    
    schema['properties']['area'] = 'int:10'
    schema['properties']['perim'] = 'int:10'
    schema['properties']['shape'] = 'float'
    
    crs = src.crs
    driver = src.driver
    
    with fiona.open(newPolyFile, 'w', crs=crs, driver=driver, schema=schema) as poly:
      for i, feature in enumerate(src):
        for col in fullDF.columns:
          feature['properties'][col] = fullDF.loc[i, col]        
        
        geom = shape(feature['geometry'])
        area = geom.area
        areaCircle = math.sqrt(area/math.pi)*2*math.pi # use the area as a circle as the standard for most simple
        perim = geom.length
        pa = round(perim/areaCircle, 6)
        
        feature['properties']['area'] = area 
        feature['properties']['perim'] = perim
        feature['properties']['shape'] = pa
        
        poly.write(feature)
        
        

        
      

    