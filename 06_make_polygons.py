# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:51:32 2018

@author: braatenj
"""

import time
import os
from osgeo import gdal, ogr, osr
import sys
import shutil
from glob import glob


# change working directory to this script's dir so we can load the ltcdb library
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb

# get the head folder
headDir = ltcdb.get_dir("Select the project head folder", scriptDname)
ltcdb.is_headDir(headDir)

# get dir paths we need 
changeDir = ltcdb.dir_path(headDir, 'rLc')

# get the various run dirs
ltRunDirs = [os.path.join(changeDir, thisRunDir) for thisRunDir in os.listdir(changeDir)]




"""
# get the dir that contains the change raster stacks TODO make this more descriptive about what dir to get
changeDir = ltcdb.get_dir("Select a folder that contains LT change files\n\n(*\\raster\\landtrendr\\change\\*)")
if changeDir is '.':
  sys.exit()

if len(changeDir.split('-')) is not 6:
  sys.exit('\nERROR: The folder you selected does not seem correct.\n'+
           'It should look something like this:\n\n'+
           'PARK_CODE-MORA-NBR-7-19842017-06010930\n\n'+
           'Please re-run the script and select a different folder.')
"""

mmus = []
for changeDir in ltRunDirs:
  # get the mmu
  mmuGood = 0
  while mmuGood is 0:
    mmu = raw_input('\nRegarding LT run: '+os.path.basename(changeDir) + '\nWhat is the desired minimum mapping unit in pixels per patch: ')
    try:
      mmu = int(mmu)
      mmuGood = 1
    except ValueError: 
      print('\nERROR: The selected value cannot be converted to an integer.')
      print('       Please try again and make sure to enter a number.')
  
  mmus.append(mmu)

  
    
# get the connected
connectednesses = []
for changeDir in ltRunDirs:
  connectednessGood = 0
  while connectednessGood is 0:
    connectedness = raw_input('\nRegarding LT run: '+os.path.basename(changeDir) + '\nShould diagonal adjacency warrant pixel inclusion in patches? - yes or no: ').lower().strip()
    if connectedness not in ['yes', 'no']:
      print('\nERROR: The given entry was not yes or no.')
      print('       Please type either: yes or no.\n')
    else:
      if connectedness == 'yes':
        connectedness = 8
      else:
        connectedness = 4
      connectednessGood = 1
  connectednesses.append(connectedness) 

for i, changeDir in enumerate(ltRunDirs):
  print('\n\nWorking on LT run: ' + os.path.basename(changeDir))
  # get the year of detection file - will patchify this
  yodFile = glob(os.path.join(changeDir,'*yrs.tif'))
  if len(yodFile) == 0:
    sys.exit('ERROR: There was no *yrs.tif file in the folder selected.\nPlease fix this.')  
  
  yodFile = yodFile[0] # TODO what if multiple were found
  mmu = mmus[i]
  connectedness = connectednesses[i]
  
  
  startTime = time.time()

                   
  # get info 
  info = ltcdb.get_info(os.path.basename(yodFile))
  
  # figure out the vector path
  bname = info['name']
  vectorBnameDir = bname+'-dist_info_'+str(mmu)+'mmu_'+str(connectedness)+'con'#+'nbr' #os.path.join(polyDir, 'ltee_mora_'+str(mmu)+'mmu_annual_dist.shp') # this should be set  !!!!USED TO BE: vectorBname
  vectorBname = 'dist' # TODO: this can change to grow, if we switch to mapping growth
  
  vectorDirFull = os.path.join(headDir, 'vector', 'change', vectorBnameDir)
  #vectorDirFullBlank = os.path.join(vectorDirFull, 'blank')  # not used ???
  if not os.path.isdir(vectorDirFull):
    os.makedirs(vectorDirFull)

  
###outDir = os.path.normpath(os.path.join(chunkDir, os.sep.join([os.pardir]*2), 'landtrendr', 'segmentation'))  

                 
  # make a patch raster file from years - event has to occur on the same year
  patchMaskFile = os.path.join(vectorDirFull, vectorBname+'_patches.tif')#yodFile.replace('yrs.tif', 'patches.tif')
  shutil.copyfile(yodFile, patchMaskFile)
  
  # copy the change attributes file
  chngAttrFile = yodFile.replace('yrs.tif', 'attributes.csv')
  # TODO deal with checking to see if exists
  chngAttrFileCopy = os.path.join(vectorDirFull, os.path.basename(chngAttrFile))
  shutil.copyfile(chngAttrFile, chngAttrFileCopy)
  
  
  print('    sieving to minimum mapping unit...')
  
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
  print('    making polygons from disturbance pixel patches...')
  
  # read in the patch raster
  srcPatches = gdal.Open(patchMaskFile, gdal.GA_ReadOnly)
  
  # make a srs definition from patch raster file
  srs = osr.SpatialReference()
  srs.ImportFromWkt(srcPatches.GetProjectionRef())
  
  # set things needed for each band (year)
  nBands = srcPatches.RasterCount
  drv = ogr.GetDriverByName('ESRI shapefile')
  

  
  #mergedPolyOutPath = os.path.join(vectorDirFull, vectorBname+'_merged.shp') #os.path.join(polyDir, 'ltee_mora_'+str(mmu)+'mmu_annual_dist.shp') # this should be set
  dst_layername = 'out'
  dst_fieldname = 'yod'
  


  
  # loop through bands
  for band, year in enumerate(range(info['startYear']+1,info['endYear']+1)):  
    band += 1
    print('        working on year: '+str(band)+'/'+str(nBands)+' ('+str(year)+')')
    polyFile = os.path.join(vectorDirFull, vectorBname+str(year)+'.shp')  #os.path.join(polyDir, info['name']+'-'+str(year)+'.shp')
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
  
print('\n\nDone!')      
print("Polygon creation took {} minutes".format(round((time.time() - startTime)/60, 1)))  
  
