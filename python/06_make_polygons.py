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
import subprocess


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
ltRunDirsBase = [os.path.basename(thisRunDir) for thisRunDir in ltRunDirs]

print('\nHere is the list of raster change definitions:')
for i, thisOne in enumerate(ltRunDirsBase):
  print(str(i+1)+': '+thisOne)

changeDirIndexGood = 0
while changeDirIndexGood is 0:
  changeDirIndex = raw_input('\nWhich one would you like to convert to polygons (enter the number): ')
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

ltRunDirs = [ltRunDirs[changeDirIndex]]
mmus = []
for changeDir in ltRunDirs:
  # get the mmu
  mmuGood = 0
  while mmuGood is 0:
    mmu = raw_input('\n\nRegarding raster change definition: '+os.path.basename(changeDir) + '\nWhat is the desired minimum mapping unit in pixels per patch: ')
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
    connectedness = raw_input('\n\nRegarding raster change definition: '+os.path.basename(changeDir) + '\nShould diagonal adjacency warrant pixel inclusion in patches? - yes or no: ').lower().strip()
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
  print('\n\nWorking on raster change definition: ' + os.path.basename(changeDir))
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
  #TODO: add the changeDir name to the info getter/printer
  bname = os.path.basename(changeDir) #info['name']
  vectorBnameDir = bname+'-'+str(mmu)+'mmu_'+str(connectedness)+'con'#+'nbr' #os.path.join(polyDir, 'ltee_mora_'+str(mmu)+'mmu_annual_dist.shp') # this should be set  !!!!USED TO BE: vectorBname
  vectorBname = 'change' # TODO: this can change to grow, if we switch to mapping growth
  
  vectorDirFull = os.path.join(headDir, 'vector', 'change', vectorBnameDir)
  #vectorDirFullBlank = os.path.join(vectorDirFull, 'blank')  # not used ???
  if os.path.exists(vectorDirFull):
    sys.exit('\nERROR: Directory '+vectorDirFull+' already exits.\n       Please re-run with different MMU and/or connectivity, if so desired.')
  else:
    os.makedirs(vectorDirFull)
  

  # copy the change attributes file
  chngAttrFile = yodFile.replace('yrs.tif', 'attributes.csv')
  if not os.path.exists(chngAttrFile):
    sys.exit('ERROR: Could not find file: '+chngAttrFile+'.\Something might have gone wrong while running script: 05_extract_annual_change.py')  

  chngAttrFileCopy = os.path.join(vectorDirFull, 'attributes.csv')
  shutil.copyfile(chngAttrFile, chngAttrFileCopy)
                 
  # make a patch raster file from years
  patchMaskFile = os.path.join(vectorDirFull, 'patches.tif')
  shutil.copyfile(yodFile, patchMaskFile)
  

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
  

  dst_layername = 'out'
  dst_fieldname = 'yod'
  

  # loop through bands
  mergedPolyOutPath = os.path.join(vectorDirFull, '_'+vectorBname+'_merged.shp')
  for band, year in enumerate(range(info['startYear']+1,info['endYear']+1)):  
    band += 1
    print('        working on year: '+str(band)+'/'+str(nBands)+' ('+str(year)+')')
    polyFile = os.path.join(vectorDirFull, vectorBname+'_'+str(year)+'.shp')  #os.path.join(polyDir, info['name']+'-'+str(year)+'.shp')
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
    if band == 1:
      mergeCmd = 'ogr2ogr -f "ESRI Shapefile" ' + mergedPolyOutPath + ' ' + polyFile
    else:
      mergeCmd = 'ogr2ogr -f "ESRI Shapefile" -append -update ' + mergedPolyOutPath + ' ' + polyFile  
    subprocess.call(mergeCmd, shell=True)
    
  # close the files
  srcPatches = None
  
  """
  # find the annual files and merge them 
  shpFiles = glob(os.path.join(vectorBnameDir,'*.shp'))     
  if len(shpFiles) == 0:
    sys.exit('ERROR: No .shp files were found in directory: '+vectorBnameDir)
  
  # merge the polygons  
  mergedPolyOutPath = os.path.join(vectorBnameDir, os.path.splitext(os.path.basename(shpFiles[0]))[0][:-4]+'all.shp')
  
  mergeCmd = 'ogr2ogr -f "ESRI Shapefile" ' + mergedPolyOutPath + ' ' + shpFiles[0]
  subprocess.call(mergeCmd, shell=True)
  
  for i in range(1,len(shpFiles)):
    mergeCmd = 'ogr2ogr -f "ESRI Shapefile" -append -update ' + mergedPolyOutPath + ' ' + shpFiles[i]  
    subprocess.call(mergeCmd, shell=True)
  
  
  # remove the individual year files
  #shutil.rmtree(polyDir)
  """
print('\n\nDone!')      
print("Polygon creation took {} minutes".format(round((time.time() - startTime)/60, 1)))  

