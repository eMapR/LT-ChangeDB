# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:51:32 2018

@author: braatenj
"""


import os
from osgeo import gdal, ogr, osr
import sys
from shutil import copyfile
from glob import glob
import subprocess

# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb






changeDir = ltcdb.get_dir("Select a folder that contains LT change files\n\n(*\\raster\\landtrendr\\change\\*)")
if changeDir == '':
  sys.exit('ERROR: No folder containing LT change files was selected.\nPlease re-run the script and select a folder.')






changeDir = os.path.normpath(changeDir)

yodFile = glob(changeDir+'/*yrs.tif')
if len(yodFile) == 0:
  sys.exit('ERROR: There was no *yrs.tif file in the folder selected.\nPlease fix this.')  

# TODO what if multiple were found
yodFile = yodFile[0]

# make a patch raster file
patchMaskFile = yodFile.replace('yrs.tif', 'patches.tif')
#patchMaskFile = 'D:\\work\\proj\\al\\gee_test\\test\\raster\\landtrendr\\change\\PARK_CODE-MORA-NBR-7-19842017-06010930\\PARK_CODE-MORA-NBR-7-19842017-06010930-change_patches.tif'
copyfile(yodFile, patchMaskFile)


# make patch rasters
print('\nSieving to minimum mapping unit...\n')
threshold = 11
connectedness = 8 # 8 or 4
srcPatches = gdal.Open(patchMaskFile, gdal.GA_Update)
nBands = srcPatches.RasterCount
for band in range(1,nBands+1): 
  srcBand = srcPatches.GetRasterBand(band)
  dstBand = srcBand
  maskBand = None
  # will also fill gaps that less than threshold
  gdal.SieveFilter(srcBand, maskBand, dstBand, threshold=threshold, connectedness=connectedness)

srcPatches = None


# make polygons
print('Making polygons from disturbance pixel patches...\n')


# set defaults 
dst_layername = 'out'
dst_fieldname = 'DN'

# read in the patch raster
srcPatches = gdal.Open(patchMaskFile, gdal.GA_ReadOnly)

# make a srs definition from patch raster file
srs = osr.SpatialReference()
srs.ImportFromWkt(srcPatches.GetProjectionRef())

# set things needed for each band (year)
nBands = srcPatches.RasterCount
outDir = os.path.join(os.path.dirname(patchMaskFile), 'polygon')
drv = ogr.GetDriverByName('ESRI shapefile')

if not os.path.exists(outDir):
  os.makedirs(outDir)


# loop through bands
for band in range(1,nBands+1):
  print('Working on Year: '+str(band)+'/'+str(nBands))
  polyFile = os.path.join(outDir,'band_'+str(band)+'.shp')
  srcBand = srcPatches.GetRasterBand(band)
  maskBand = srcBand
  
  # create a polygon file
  dstPoly = drv.CreateDataSource(polyFile)
  # set the layer name and srs of the poly file
  dstLayer = dstPoly.CreateLayer(dst_layername, geom_type=ogr.wkbPolygon, srs=srs)
        
  # create a field
  fd = ogr.FieldDefn(dst_fieldname, ogr.OFTInteger)
  dstLayer.CreateField(fd)
  
  # perform the operation
  gdal.Polygonize(srcBand, maskBand, dstLayer, iPixValField=0, options=['8CONNECTED=8'])
  
  dstPoly = None
  
# close the files
srcPatches = None

# remove the DN column
polygonFiles = glob(outDir+'/*shp')
for polygon in polygonFiles:
  polyBname = os.path.splitext(os.path.basename(polygon))[0]
  alterCmd = 'ogrinfo ' + polygon + ' ' + '-sql "ALTER TABLE ' + polyBname + ' DROP COLUMN DN"'
  subprocess.call(alterCmd, shell=True)





