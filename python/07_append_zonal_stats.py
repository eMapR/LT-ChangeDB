# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 14:48:18 2018

@author: braatenj
"""

from osgeo import ogr
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


# change working directory to this script's dir so we can load the ltcdb library
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb

# get the head folder
headDir = ltcdb.get_dir("Select the project head folder", scriptDname)
ltcdb.is_headDir(headDir)

vectorDir = os.path.join(headDir, 'vector', 'change')
if not os.path.isdir(vectorDir):
  sys.exit('ERROR: Can\'t find the vector folder.\nTrying to find it at this location: '+vectorDir+'\nIt\'s possible you provided an incorrect project head folder.\nPlease re-run the script and select the project head folder.')

# could try to find the gee_chunk folder
#[x[0] for x in os.walk(chunkDir)]

#segDir = r'D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation'
ltRunDirs = [os.path.join(vectorDir, thisRunDir) for thisRunDir in os.listdir(vectorDir)]

ltRunDirsBase = [os.path.basename(thisRunDir) for thisRunDir in ltRunDirs]

print('\nHere is the list of vector change definitions:')
for i, thisOne in enumerate(ltRunDirsBase):
  print(str(i+1)+': '+thisOne)

changeDirIndexGood = 0
while changeDirIndexGood is 0:
  changeDirIndex = raw_input('\nWhich one would you like to append zonal statistics to (enter the number): ')
  try:
    changeDirIndex = int(changeDirIndex)
    changeDirIndex -= 1
    changeDirIndexGood = 1
    if changeDirIndex not in range(len(ltRunDirsBase)):
      print('\nERROR: The selected value is outside the valid range.')
      print('       Please try again and make sure to enter a valid selection.')
      changeDirIndexGood = 0
  except ValueError: 
    print('\nERROR: The selected value cannot be converted to an integer.')
    print('       Please try again and make sure to enter a number.')

# index out the one requested
ltRunDirs = [ltRunDirs[changeDirIndex]]

mergeFiles = glob(os.path.join(ltRunDirs[0],'*merged*')) 
if len(mergeFiles) == 0:
  sys.exit('\nERROR: The selected polygon definition: '+ltRunDirs[0]+'\nhas already had zonal statistics appended.')



# make sure the dirs exists - TODO: seems like this is not needed - the dir has already been found
for polyDir in ltRunDirs:
  if not os.path.isdir(polyDir):
    sys.exit('\nERROR: Can\'t find the polygon folder.\nTrying to find it at this location: '+polyDir+'\nIt\'s possible you did not run the 06_make_polygons.py file.\nPlease run the script and try again.')

startTime = time.time()

firstTime = 0
for polyDir in ltRunDirs:

  # get the polygon directory
  #polyDir = ltcdb.get_dir("Select a folder that contains LT change polgyon files\n\n(*\\raster\\landtrendr\\change\\*\\polygon)")
  #if polyDir == '':
  #  sys.exit('ERROR: No folder containing LT change polgyon files files was selected.\nPlease re-run the script and select a folder.')
  
  
  # get the annual polygon files
  polyFiles = glob(os.path.join(polyDir,'change*.shp'))
  if len(polyFiles) == 0:
    sys.exit('\nERROR: There was no *.shp files in the folder selected.\nPlease fix this.')
  
  attributeList = glob(os.path.join(polyDir,'*attributes.csv'))
  
  if len(attributeList) == 0:
    sys.exit('\nERROR: There was no *.csv file in the folder selected.\nPlease fix this.') 
  attributeList = attributeList[0]
  
  # get the attribute list file
  #attributeList = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-change_attributes.csv"
  #polyDir = r'D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\polygon'
  #attributeList = glob(os.path.join(polyDir, os.pardir, '*attributes.csv'))[0]
  
  # TODO check if there are more than one
  
  print('\nAdding disturbance attributes to the shapefile table...\n')
  
  # read in the attribute list
  attrList = pd.read_csv(attributeList, header=None)
  #attrList = np.genfromtxt(attributeList, delimiter=',', dtype='object')
  if attrList.shape[0] == 0:
    sys.exit('\nERROR: There are no rows in file '+attributeList+'.\nPlease fix this.')
  
  #check for annual - need to exist
  annualAttr = attrList[(attrList.iloc[:,3] == 'annual') & (attrList.loc[:,6] == 1)]
  #if annualAttr.shape[0] == 0:
  #  sys.exit('ERROR: There are no "annual" rows in file '+attributeList+'.\nPlease fix this.')
    
  #check for dynamic  - need to exist
  dynamicAttr = attrList[(attrList.iloc[:,3] == 'dynamic') & (attrList.loc[:,6] == 1)]
  #if dynamicAttr.shape[0] == 0:
  #  sys.exit('ERROR: There are no "dynamic" rows in file '+attributeList+'.\nPlease fix this.')
  
  #check for dynamic  - need to exist
  staticAttr = attrList[(attrList.iloc[:,3] == 'static') & (attrList.loc[:,6] == 1)]
  
  # make a temp dir to hold the new files
  tmpDir = os.path.join(polyDir,'tmp')
  if not os.path.exists(tmpDir):
    os.mkdir(tmpDir) 
  
  # get the run name # TODO: need to handle figuring out the run name better - this one we need to get from the dir name - in earlier steps we get it from the file basename
  runName = os.path.basename(os.path.dirname(attributeList))
  # get file info
  info = ltcdb.get_info(runName)
  
  # set some var needed later
  annualBandIndex =  ltcdb.year_to_band(runName, 1) # os.path.basename(attributeList)    # adjust this by 1 band because disturbance layers start +1 year from time series start
  dynamicBandIndex =  ltcdb.year_to_band(runName, 0) # os.path.basename(attributeList)
  endYear = info['endYear']
  indexID = info['indexID']
  version = info['version']
  
  # loop through the polygons
  for fn, polyFile in enumerate(polyFiles):
    #fn=0
    #polyFile = polyFiles[0]
    
    # get the year out
    year = int(os.path.splitext(os.path.basename(polyFile))[0][-4:])    
    
    # are there features to work on?
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(polyFile, 0) # 0 means read-only. 1 means writeable.
    layer = dataSource.GetLayer()
    nFeatures = layer.GetFeatureCount()
    layer = None
    dataSource = None
    if nFeatures == 0:
      print('Skipping year: '+str(fn+1)+'/'+str(len(polyFiles))+' ('+str(year)+') - no polygon features')
      continue
    
    print('Working on year: '+str(fn+1)+'/'+str(len(polyFiles))+' ('+str(year)+')')
    
    
    # define name of tmp polygom file
    newPolyFile = os.path.join(tmpDir, os.path.basename(polyFile))
    
    # do the annual attributes, the id attributes, and the shape attributes - doing this through pandas and and
    band = annualBandIndex[year]
    fullDF = pd.DataFrame()
    for ri, attr in annualAttr.iterrows():
      #print(attr.iloc[1])
      
      #attr = attrList[1,]
      
      # TODO: need to check to make sure that the file to summarize exits
      attrBname = attr.iloc[1]
      print('    attribute: '+attrBname)
      stats = zonal_stats(polyFile, attr.iloc[0], band=band, stats=['mean', 'std'])
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
      schema['properties']['uniqID'] = 'str:30'
      
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
          feature['properties']['uniqID'] = indexID+'_'+version+'_'+str(year)+'_'+str(annualID)
          
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
  
    # do the dynamic attributes
    for ri, attr in dynamicAttr.iterrows():
      #attr = dynamicAttr.iloc[0,:]
      
      # TODO: need to check to make sure that the file to summarize exits
      
      if ri > 0:
        nextLine = '\n'
      else:
        nextLine = ''
      
      # make field names
      #pstRun = int(attr.iloc[6]) # this is taken care of earlier on
      #if pstRun == 0:
      #  continue
      pstIntervals = attr.iloc[5].split('|')
      pstIntervalsLabel = [thisOne.zfill(2) for thisOne in pstIntervals]
      pstIntervalsInt = [int(thisOne) for thisOne in pstIntervals]
      print(nextLine+'    attribute: '+attr[1]+' year intervals '+', '.join(pstIntervals))
      
      fieldNamesPre = np.array([attr.iloc[1]+thisOne for thisOne in pstIntervalsLabel]) # need this to be np array for later use in indexing
      fieldNamesAll = []
      for thisOne in fieldNamesPre:
        fieldNamesAll.append(thisOne+'Mn')
        fieldNamesAll.append(thisOne+'Sd')
      
      # read in the polygon
      driver = ogr.GetDriverByName('ESRI Shapefile')
      dataSource = driver.Open(newPolyFile, 1) # 0 means read-only. 1 means writeable.
      layer = dataSource.GetLayer()
      
      # add field names to the polygon
      for fieldName in fieldNamesAll:
        layer = ltcdb.add_field(layer, fieldName, ogr.OFTInteger)
  
      # get the number of features in the layer
      nFeatures = layer.GetFeatureCount()


      for i in range(nFeatures):
        progress = (i+1.0)/nFeatures
        ltcdb.update_progress(progress, '        ') 
        
        feature = layer.GetFeature(i) 
        yod = int(feature.GetField("yod"))-1
        durMean = int(feature.GetField("durMn"))
        distEndYear = yod+durMean
        postYearsInt = np.array([distEndYear+thisOne for thisOne in pstIntervalsInt])
        goodYears = np.where(postYearsInt <= endYear)
        postYearsInt = postYearsInt[goodYears]
        postYearsLabel = fieldNamesPre[goodYears]
                
        for yr, field in zip(postYearsInt, postYearsLabel):
          #print(yearIndex[yr])
          summary = ltcdb.zonal_stats(feature, newPolyFile, attr[0], dynamicBandIndex[yr]) 
        
          feature.SetField(field+'Mn', summary[0])
          feature.SetField(field+'Sd', summary[1])
      
          # set the changes to ith feature in the layer
        layer.SetFeature(feature)
        feature = None

      layer = None
      dataSource = None
  
  
  
  
  
    # do the static attributes
    print('\n')
    if staticAttr.shape[0] > 0:
      fullDF = pd.DataFrame()
      tempFile = os.path.join(os.path.dirname(newPolyFile), 'temp.shp')
      for ri, attr in staticAttr.iterrows():
        #print(attr.iloc[1])
        
        #attr = attrList[1,]
        attrBname = attr.iloc[1]
        print('    attribute: '+attrBname)
        # TODO: need to check to make sure that the file to summarize exits
        stats = zonal_stats(polyFile, attr.iloc[0], band=int(attr.iloc[5]), stats=['mean', 'std']) # TODO when the attribute table is read in set the column types so we don't need to specify type every time 
        statsDF = pd.DataFrame.from_dict(stats).round().astype(int)
        statsDF.columns = [attrBname+'Mn', attrBname+'Sd']
        fullDF = pd.concat([fullDF, statsDF], axis=1)
      
  
      with fiona.open(newPolyFile, 'r') as src:
        # make a copy of the schema
        schema = src.schema.copy()
        
        # add fields to the schema      
        for col in fullDF.columns:
          schema['properties'][col] = 'int:10'
              
        # copy info as template for the new polgon file
        crs = src.crs
        driver = src.driver
  
  
          
        # open the shapefile for writing to using info from the source polygon file # TODO: we're assuming that this new files exits, if it doesn't then we need to create a new file first
        with fiona.open(tempFile, 'w', crs=crs, driver=driver, schema=schema) as poly:
          # loop through all the features
          for i, feature in enumerate(src):
            # add all the attributes from the attribute list
            for col in fullDF.columns:
              feature['properties'][col] = fullDF.loc[i, col]  # this will add both the "mean" and "stDev"        
                      
            # write the feature to disk 
            poly.write(feature)
  
      #replace the file 
      tempFiles = glob(os.path.join(os.path.dirname(newPolyFile), '*temp*'))
      newPolyFileBase = os.path.splitext(newPolyFile)[0]
      replacements = [newPolyFileBase+os.path.splitext(thisOne)[1] for thisOne in tempFiles]
      deleteThese = glob(newPolyFileBase+'*')
      for thisOne in deleteThese:
        os.remove(thisOne)
      for old, new in zip(tempFiles,replacements):
        os.rename(old, new)
      
      
      


  # find all the shapefiles that have been attributed 
  shpFiles = glob(os.path.join(tmpDir,'*.shp'))     
  if len(shpFiles) == 0:
    sys.exit('ERROR: No .shp files were found in directory: '+tmpDir)
  
  # sort the list
  shpFiles.sort()
  
  # merge the polygons  
  mergedPolyOutPath = os.path.join(tmpDir, 'changeDB.shp')
  
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
  dbName = 'change'
  """
  if firstTime == 0:
    changeDBfile = mergedPolyOutPath.replace('.shp', '.sqlite')
    #changeDBfile = os.path.join(polyDir,'lt_change_database.sqlite') #vectorDir
    convertCmd = 'ogr2ogr -f "SQLite" -nlt PROMOTE_TO_MULTI -nln '+dbName+' -dsco SPATIALITE=YES ' + changeDBfile + ' ' + mergedPolyOutPath  
    firstTime += 1
  else:
    convertCmd = 'ogr2ogr -f "SQLite" -nlt PROMOTE_TO_MULTI -nln '+dbName+' -dsco SPATIALITE=YES -update ' + changeDBfile + ' ' + mergedPolyOutPath  
  """
  changeDBfile = mergedPolyOutPath.replace('.shp', '.sqlite')
  convertCmd = 'ogr2ogr -f "SQLite" -nlt PROMOTE_TO_MULTI -nln '+dbName+' -dsco SPATIALITE=YES -lco SPATIAL_INDEX=NO ' + changeDBfile + ' ' + mergedPolyOutPath  
  subprocess.call(convertCmd, shell=True)

  # move the filled polys
  shpFiles = glob(os.path.join(tmpDir,'*'))     
  newShpFiles = [os.path.join(polyDir, os.path.basename(fn)) for fn in shpFiles]
  for old, new in zip(shpFiles, newShpFiles):
    os.rename(old, new)
    
  os.rmdir(tmpDir)
  
  #remove the _merge file
  mergeFiles = glob(os.path.join(polyDir,'*merged*'))     
  for fn in mergeFiles:
    os.remove(fn)

  # write a file to know that zonal stats have been appended - don't need this since we know that if *merged* does not exist, stats have been appended
  #with open(os.path.join(polyDir, 'stats_appended.txt'), 'w') as the_file:
  #  the_file.write('zonal stats have been appended to all polygon files in this directory\n')

print('\nDone!')      
print("Appending zonal stats took {} minutes".format(round((time.time() - startTime)/60, 1)))  
  
  
  
     