# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:51:32 2018

@author: braatenj
"""

import os
from osgeo import gdal, ogr, osr
import sys
import shutil
from glob import glob
import subprocess

# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb






# get the dir that contains the change raster stacks TODO make this more descriptive about what dir to get
changeDir = ltcdb.get_dir("Select a folder that contains LT change files\n\n(*\\raster\\landtrendr\\change\\*)")
if changeDir is '.':
  sys.exit()

if len(changeDir.split('-')) is not 6:
  sys.exit('\nERROR: The folder you selected does not seem correct.\n'+
           'It should look something like this:\n\n'+
           'PARK_CODE-MORA-NBR-7-19842017-06010930\n\n'+
           'Please re-run the script and select a different folder.')


# get the mmu
mmuGood = 0
while mmuGood is 0:
  mmu = raw_input('\nWhat is the desired minimum mapping unit in pixels per patch: ')
  try:
    mmu = int(mmu)
    mmuGood = 1
  except ValueError: 
    print('\nERROR: The selected value cannot be converted to an integer.')
    print('       Please try again and make sure to enter a number.')
    
    
# get the connected
connectednessGood = 0
while connectednessGood is 0:
  connectedness = raw_input('\nShould diagonal adjacency warrant pixel inclusion in patches? - yes or no: ').lower().strip()
  if connectedness not in ['yes', 'no']:
    print('\nERROR: The given entry was not yes or no.')
    print('       Please type either: yes or no.\n')
  else:
    if connectedness == 'yes':
      connectedness = 8
    else:
      connectedness = 4
    connectednessGood = 1
    

# get the year of detection file - will patchify this
yodFile = glob(os.path.join(changeDir,'*yrs.tif'))
if len(yodFile) == 0:
  sys.exit('ERROR: There was no *yrs.tif file in the folder selected.\nPlease fix this.')  

yodFile = yodFile[0] # TODO what if multiple were found


                 


                 
# make a patch raster file from years - event has to occur on the same year
patchMaskFile = yodFile.replace('yrs.tif', 'patches.tif')
shutil.copyfile(yodFile, patchMaskFile)

print('\nSieving to minimum mapping unit...\n')

srcPatches = gdal.Open(patchMaskFile, gdal.GA_Update)
nBands = srcPatches.RasterCount
for band in range(1,nBands+1): 
  srcBand = srcPatches.GetRasterBand(band)
  dstBand = srcBand
  maskBand = None
  # will also fill gaps that less than threshold
  gdal.SieveFilter(srcBand, maskBand, dstBand, threshold=mmu, connectedness=connectedness)

srcPatches = None






# make polygons
print('Making polygons from disturbance pixel patches...\n')

# read in the patch raster
srcPatches = gdal.Open(patchMaskFile, gdal.GA_ReadOnly)

# make a srs definition from patch raster file
srs = osr.SpatialReference()
srs.ImportFromWkt(srcPatches.GetProjectionRef())

# set things needed for each band (year)
nBands = srcPatches.RasterCount
drv = ogr.GetDriverByName('ESRI shapefile')

# get info 
info = ltcdb.get_info(os.path.basename(patchMaskFile))

# set outDir paths
polyDir = os.path.join(os.path.dirname(patchMaskFile), 'polygon')
vectorDir = os.path.normpath(os.path.join(changeDir, os.sep.join([os.pardir]*4), 'vector'))
bname = info['name']
mergedPolyOutPath = os.path.join(vectorDir, bname+'-dist_info_'+str(mmu)+'mmu.shp') #os.path.join(polyDir, 'ltee_mora_'+str(mmu)+'mmu_annual_dist.shp') # this should be set
dst_layername = 'out'
dst_fieldname = 'yod'

if not os.path.exists(polyDir):
  os.makedirs(polyDir)
  
if not os.path.exists(vectorDir):
  os.makedirs(vectorDir)

# loop through bands
for band, year in enumerate(range(info['startYear']+1,info['endYear']+1)):  
  band += 1
  print('Working on year: '+str(band)+'/'+str(nBands)+' ('+str(year)+')')
  polyFile = os.path.join(polyDir, str(year)+'.shp')
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
   
  # merge the polygons
  #if band == 1:
  #  mergeCmd = 'ogr2ogr -f "ESRI Shapefile" ' + mergedPolyOutPath + ' ' + polyFile
  #else:
  #  mergeCmd = 'ogr2ogr -f "ESRI Shapefile" -append -update ' + mergedPolyOutPath + ' ' + polyFile  
  #subprocess.call(mergeCmd, shell=True)
  
# close the files
srcPatches = None

# remove the individual year files
#shutil.rmtree(polyDir)



