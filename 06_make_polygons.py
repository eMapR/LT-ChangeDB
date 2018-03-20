# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:51:32 2018

@author: braatenj
"""


import os
import sys
from shutil import copyfile
from glob import glob

# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb






changeDir = ltcdb.get_dir("Select a folder that contains LT change files\n\n(*\\raster\\landtrendr\\change\\*)")
if changeDir == '':
  sys.exit('ERROR: No folder containing LT change files was selected.\nPlease re-run the script and select a folder.')


threshold = 11
connectedness = 8 # 8 or 4

changeDir = os.path.normpath(changeDir)

yodFile = glob(changeDir+'/*yrs.tif')
if len(yodFile) == 0:
  sys.exit('ERROR: There was no *yrs.tif file in the folder selected.\nPlease fix this.')  

# TODO what if multiple were found
yodFile = yodFile[0]

# make a patch raster file
patchMaskFile = yodFile.replace('yrs.tif', 'patches.tif')
copyfile(yodFile, patchMaskFile)

# make patch rasters
  print('\nSieving to minimum mapping unit...\n')
srcPatches = gdal.Open(patchMaskFile, gdal.GA_Update)
nBands = srcPatches.RasterCount
for band in range(1,nBands+1): 
  srcBand = srcPatches.GetRasterBand(band)
  dstBand = srcBand
  maskBand = None
  # will also fill gaps that less than threshold
  gdal.SieveFilter(srcBand, maskBand, dstBand, threshold=threshold, connectedness=connectedness)

srcPatches = None



print('Making polygons from disturbance pixel patches...\n')
gdal_polygonize(distMaskOutPath, distMaskOutPath, distPolyOutPath)



  write_raster(mask, distMaskOutPath, prj, origin, 'GTiff')  
  
  
  
  ###################################################################
  # MMU the raster
  ###################################################################
  print('\nSieving to minimum mapping unit...\n')
  gdal_sieve(distMaskOutPath, mmu)
  #sieveCmd = 'gdal_sieve.py -of GTiff -st '+str(mmu)+' -8 '+distMaskOutPath  
  #subprocess.call(sieveCmd, shell=True)
  
  
  
  ###################################################################
  # polygonize the raster
  ###################################################################
  print('Making polygons from disturbance pixel patches...\n')
  gdal_polygonize(distMaskOutPath, distMaskOutPath, distPolyOutPath)
  #polyCmd = 'gdal_polygonize.py -8 -f "ESRI shapefile" -mask ' + distMaskOutPath +' '+ distMaskOutPath +'  '+ distPolyOutPath
  #subprocess.call(polyCmd, shell=True)
  
  
  
  ###################################################################
  # remove the DN column  
  ###################################################################
  print('\nAdding disturbance attributes to the shapefile table...\n')
  
  polyBname = os.path.splitext(os.path.basename(distPolyOutPath))[0]
  alterCmd = 'ogrinfo ' + distPolyOutPath + ' ' + '-sql "ALTER TABLE ' + polyBname + ' DROP COLUMN DN"'
  subprocess.call(alterCmd, shell=True)
  
  
  #  convert = 'ogr2ogr -f SQLite -nlt MULTIPOLYGON -dsco "SPATIALITE=YES" ' + distPolyOutPathsql +' '+ distPolyOutPathshp
  #  subprocess.call(convert, shell=True)
  
  
  # get the shapefile driver - if you don't specify driver, then in the 
  # next line you can use ogr.Open() and it will try all drivers until it
  # finds the one that opens the file, by specifying it will only try the
  # defined driver
  # reference: https://gis.stackexchange.com/questions/141966/python-gdal-ogr-open-or-driver-open
  driver = ogr.GetDriverByName('ESRI Shapefile')
  
  # open the shapefile as writeable 
  dataSource = driver.Open(distPolyOutPath, 1) # 0 means read-only. 1 means writeable.
  
  # get the layer from the file - a gdal dataset can potentially have many layers
  # we just want the first layer
  # reference: http://www.gdal.org/ogr_apitut.html
  layer = dataSource.GetLayer()
  
  
  
  # make new fields
  # reference: http://www.gdal.org/classOGRFieldDefn.html
  # for list of type see http://www.gdal.org/ogr__core_8h.html#a787194bea637faf12d61643124a7c9fc
  index = ogr.FieldDefn('index', ogr.OFTString)
  yodField = ogr.FieldDefn('yod', ogr.OFTInteger)
  patchID = ogr.FieldDefn('patchID', ogr.OFTInteger)
  uniqID = ogr.FieldDefn('uniqID', ogr.OFTString)
  magMeanField = ogr.FieldDefn('magMean', ogr.OFTInteger)
  magStdvField = ogr.FieldDefn('magStdv', ogr.OFTInteger)
  durMeanField = ogr.FieldDefn('durMean', ogr.OFTInteger)
  durStdvField = ogr.FieldDefn('durStdv', ogr.OFTInteger)
  areaField = ogr.FieldDefn('area', ogr.OFTInteger)
  perimField = ogr.FieldDefn('perim', ogr.OFTInteger)
  shapeField = ogr.FieldDefn('shape', ogr.OFTReal)
  
  
  # add the new field to the layer
  layer.CreateField(index)
  layer.CreateField(yodField)
  layer.CreateField(patchID)
  layer.CreateField(uniqID)
  layer.CreateField(magMeanField)
  layer.CreateField(magStdvField)
  layer.CreateField(durMeanField)
  layer.CreateField(durStdvField)
  layer.CreateField(areaField)
  layer.CreateField(perimField)
  layer.CreateField(shapeField)
  
  # check to see if it was added
  # get the layer's attribute schema
  # reference: http://www.gdal.org/classOGRLayer.html#a80473bcfd11341e70dd35bebe94026cf
  #layerDefn = layer.GetLayerDefn()
  #fieldNames = [layerDefn.GetFieldDefn(i).GetName() for i in range(layerDefn.GetFieldCount())]
  
  # get the number of features in the layer
  nFeatures = layer.GetFeatureCount()
  
  # Add features to the ouput Layer
  for i in range(nFeatures):
    # get the ith feature
    feature = layer.GetFeature(i) 
    
    # set the ith feature's fields
    patchID = i+1
    feature.SetField('index', indexID)
    feature.SetField('yod', year)
    feature.SetField('patchID', patchID)
    feature.SetField('uniqID', indexID+str(year)+str(patchID))
    
    # get zonal stats on disturbance
    summary = zonal_stats(feature, distPolyOutPath, distInfoOutPath) #, 2
    #durSummary = zonal_stats(feature, distPolyOutPath, distInfoOutPath, 3)
  
    geometry = feature.GetGeometryRef()
    area = geometry.GetArea()
    areaCircle = math.sqrt(area/math.pi)*2*math.pi
    perimeter = geometry.Boundary().Length()
    pa = round(perimeter/areaCircle, 6)
  
    # set the ith features summary stats fields
    feature.SetField('magMean', int(round(summary[0])))
    feature.SetField('magStdv', int(round(summary[1])))
    feature.SetField('durMean', int(round(summary[2])))
    feature.SetField('durStdv', int(round(summary[3])))
    feature.SetField('area', int(area))
    feature.SetField('perim', int(perimeter))
    feature.SetField('shape', pa)
    
    # set the changes to ith feature in the layer
    layer.SetFeature(feature)
    
    #feature = None
    
  # Close the Shapefile
  dataSource = None
  
  
  # merge the polygons
  if first:
    mergeCmd = 'ogr2ogr -f "ESRI Shapefile" ' + mergedPolyOutPath + ' ' + distPolyOutPath
  else:
    mergeCmd = 'ogr2ogr -f "ESRI Shapefile" -append -update ' + mergedPolyOutPath + ' ' + distPolyOutPath  
  
  subprocess.call(mergeCmd, shell=True)
  
  first = 0
  
print('Done!')