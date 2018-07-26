# -*- coding: utf-8 -*-
"""
Created on Tue Mar 06 14:09:32 2018

@author: braatenj
"""

import time
import os
import fnmatch
import subprocess
import sys
import numpy as np
from osgeo import gdal, ogr
from glob import glob
from shutil import copyfile


# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)

import ltcdb





headDir = ltcdb.get_dir("Select the project head folder", scriptDname)

#headDir = r'D:\work\proj\al\gee_test\test'


if headDir == '':
  sys.exit('ERROR: No folder containing LT-GEE files was selected.\nPlease re-run the script and select a folder.')

chunkDir = os.path.join(headDir, 'raster', 'prep', 'gee_chunks')
if not os.path.isdir(chunkDir):
  sys.exit('ERROR: Can\'t find the gee_chunk folder.\nTrying to find it at this location: '+chunkDir+'\nIt\'s possible you provided an incorrect project head folder.\nPlease re-run the script and select the project head folder.')

# could try to find the gee_chunk folder
#[x[0] for x in os.walk(chunkDir)]


# find the tif chunks
tifs = []
for root, dirnames, filenames in os.walk(chunkDir):
  for filename in fnmatch.filter(filenames, '*LTdata*.tif'):
    tifs.append(os.path.join(root, filename))

# are there any tif files to work with?
if len(tifs) == 0:
  sys.exit('ERROR: There are no TIF files in the folder selected.\nPlease fix this.')


outDir = os.path.normpath(os.path.join(chunkDir, os.sep.join([os.pardir]*2), 'landtrendr', 'segmentation'))
# could just make the folder
if not os.path.isdir(chunkDir):
    sys.exit('ERROR: Can\'t find the segmentation folder.\nTrying to find it at this location: '+outDir+'\nIt\'s possible you have not run the directory setup script.\nPlease make sure the folder exists.')
#outDir = ltcdb.get_dir("Select folder to place LT segmentation outputs in\n\n(*\\raster\\landtrendr\segmentation)")
#if outDir == '':
#  sys.exit('ERROR: No folder containing LT-GEE files was selected.\nPlease re-run the script and select a folder.')
  
#TODO check for existing files

"""
root = Tkinter.Tk()
clipFile = str(tkFileDialog.askopenfilename(initialdir = "/",title = "Select standardized vector file\n\n(*\\vector\\*ltgee*.shp)"))
root.destroy()
"""
  
#TODO check to make sure that it is a .shp and that it has *ltgee* possibly check for epsg5070 proj - should be file is *ltgee*



startTime = time.time()

######################################################################



# make sure path parts are right
if chunkDir[-1] != '/':
  chunkDir += '/'
if outDir[-1] != '/':
  outDir += '/'

# set the unique names 
names = list(set(['-'.join(fn.split('-')[0:8]) for fn in tifs])) 

# loop through each unique names, find the matching set, merge them as vrt, and then decompose them
for name in names:
  #name = names[0] 
  # create output dirs
  runName = os.path.basename(name)  #  #runName = os.path.splitext(bname)[0]

  
  # make a dir to unpack the data
  thisOutDirPrep = os.path.join(os.path.dirname(chunkDir), os.pardir, runName)
  if not os.path.exists(thisOutDirPrep):
    os.mkdir(thisOutDirPrep)
  
  # make a dir for the final data stacks 
  thisOutDir = os.path.join(outDir, runName)
  if not os.path.exists(thisOutDir):
    os.mkdir(thisOutDir)


  print('\nWorking on LT run: '+runName)
  # find the files that belong to this set  
  matches = []
  for tif in tifs:   
    if name in tif:
      matches.append(tif)


  # define the projection - get the first matched file and extract the crs from it
  proj = os.path.basename(matches[0]).split('-')[6]
  proj = proj[0:4]+':'+proj[4:]
  
  
  # deal with the shapefile - find it reproject it to the vector folder
  prepDir = os.path.dirname(matches[0])
  ltAoi = glob(chunkDir+'/'+runName+'*LTaoi.shp')
  if(len(ltAoi) != 0):
    outShpFile = os.path.join(os.path.sep.join(chunkDir.split(os.path.sep)[:-3]),'vector',runName+'-LTaoi.shp')
    cmd = 'ogr2ogr -f "ESRI Shapefile" -t_srs '+proj+' '+outShpFile+' '+ltAoi[0]
    subprocess.call(cmd, shell=True)
  else:
    sys.exit('ERROR: Can\'t find the shapefile that is suppose to be with the data downloaded from Google Drive')

  
  # get info about the GEE run
  info = ltcdb.get_info(runName)


  # make a master vrt
  masterVrtFile = os.path.normpath(os.path.join(thisOutDirPrep, runName+'.vrt'))
  ltcdb.make_vrt(matches, masterVrtFile)
  
  
  # define the list of replacement types in the new out images    
  outTypes = ['vert_yrs.tif',
              'vert_fit_idx.tif',
              'seg_rmse.tif',        
              'ftv_tcb.tif',
              'ftv_tcg.tif',
              'ftv_tcw.tif']


  # make a list of band ranges for each out type
  vertStops = []
  for vertType in range(3): #4  
    vertStops.append(vertType*info['nVert']+1)
  
  rmseStops = [vertStops[-1]+1]
  
  nYears = (info['endYear'] - info['startYear']) + 1
  ftvStops = []  
  for ftvType in range(1,len(outTypes)-2):  
    ftvStops.append(ftvType*nYears+rmseStops[0])
    
  bandStops = vertStops+rmseStops+ftvStops
  bandRanges = [range(bandStops[i],bandStops[i+1]) for i in range(len(bandStops)-1)]


  # set some size variables
  srcVrt = gdal.Open(masterVrtFile)
  xSize = srcVrt.RasterXSize
  ySize = srcVrt.RasterYSize
  blockSize = 512
  srcVrt = None

  
  # loop through the datasets and pull them out of the mega stack and write them to the define outDir
  print('   Unpacking file:')
  for i in range(len(outTypes)):
    print('      '+runName+'-'+outTypes[i])
    block = 0
    for y in xrange(0, ySize, blockSize):
      #yRange = range(0, ySize, blockSize)
      #y=yRange[5]
      if y + blockSize < ySize:
        rows = blockSize
      else:
        rows = ySize - y
      for x in xrange(0, xSize, blockSize):
        #xRange = range(0, xSize, blockSize)
        #x=xRange[4]
        if x + blockSize < xSize:
          cols = blockSize
        else:
          cols = xSize - x  
        
        outBname = runName+'-'+ str(block).zfill(3)+'_'+outTypes[i]
        outFileBlock = os.path.normpath(os.path.join(thisOutDirPrep, outBname))
        bands = ' -b '+' -b '.join([str(band) for band in bandRanges[i]])
        win = '{0} {1} {2} {3}'.format(x, y, blockSize, blockSize)
        cmd = 'gdal_translate -q -of GTiff -a_srs ' + proj + ' -srcwin '+ win + ' ' + bands +' '+ masterVrtFile + ' ' + outFileBlock #
        subprocess.call(cmd, shell=True)
  
        block += 1

    blockFiles = glob(thisOutDirPrep+'/*'+outTypes[i])
    # TODO deal with not finding files 
    
    # create vrt
    outTypeVrtFile = os.path.normpath(os.path.join(thisOutDirPrep, runName+'-'+outTypes[i])).replace('.tif', '.vrt')
    ltcdb.make_vrt(blockFiles, outTypeVrtFile)
    
    # make the merged file
    # read in the inShape file and get the extent
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource = driver.Open(outShpFile, 0)
    extent = inDataSource.GetLayer().GetExtent()
    projwin = '{} {} {} {}'.format(extent[0], extent[3], extent[1], extent[2])  
    inDataSource = None
    extent = None
  
    outFile = os.path.normpath(os.path.join(thisOutDir, runName+'-'+outTypes[i]))
    cmd = 'gdal_translate -q -of GTiff -a_nodata -9999 -a_srs ' + proj + ' -projwin ' + projwin + ' ' + outTypeVrtFile + ' ' + outFile #
    subprocess.call(cmd, shell=True)

    # make background values -9999
    nBands = gdal.Open(outFile).RasterCount
    bands = ' '.join(['-b '+str(band) for band in range(1,nBands+1)])
    cmd = 'gdal_rasterize -q -i -burn -9999 '+bands+' '+outShpFile+' '+outFile
    subprocess.call(cmd, shell=True)



    # clear the dir for the next data
    deleteThese = glob(thisOutDirPrep+'/*'+os.path.splitext(outTypes[i])[0]+'*')
    for this in deleteThese:
      os.remove(this)


  
  vertYrsFile = glob(os.path.join(thisOutDir,'*vert_yrs.tif'))[0]
  
  # TODO return error message if the vertYrsFile is not found




  ##########################################################################################################
  ######## MAKE THE vert_fit_tc* FILES
  ##########################################################################################################
  print('   Creating TC vert_fit data')
   
  # make a copy of vert files for tc vals
  vertTCBfitFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcb.tif')
  vertTCGfitFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcg.tif')
  vertTCWfitFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcw.tif')
  outPuts = [vertTCBfitFile, vertTCGfitFile, vertTCWfitFile]
  
  #ltcdb.make_output_blanks(vertYrsFile, outPuts, 0)
  for outPut in outPuts:
    copyfile(vertYrsFile, outPut)
  
  
  # open the output files for update
  dstTCB = gdal.Open(vertTCBfitFile, gdal.GA_Update)
  dstTCG = gdal.Open(vertTCGfitFile, gdal.GA_Update)
  dstTCW = gdal.Open(vertTCWfitFile, gdal.GA_Update)
  
  # open the vertYrs file for read - so w eknow what years to pull out of the TC FTV stacks
  srcYrs = gdal.Open(vertYrsFile, gdal.GA_ReadOnly)
  
  # read in the TC FTV stacks (all years)
  ftvTCBfitFile = vertYrsFile.replace('vert_yrs.tif', 'ftv_tcb.tif')
  ftvTCGfitFile = vertYrsFile.replace('vert_yrs.tif', 'ftv_tcg.tif')
  ftvTCWfitFile = vertYrsFile.replace('vert_yrs.tif', 'ftv_tcw.tif')
  
  srcFtvTCB = gdal.Open(ftvTCBfitFile, gdal.GA_ReadOnly)
  srcFtvTCG = gdal.Open(ftvTCGfitFile, gdal.GA_ReadOnly)
  srcFtvTCW = gdal.Open(ftvTCWfitFile, gdal.GA_ReadOnly)
  
  ##############################################################################
  
  
  # set some size variables
  ftvIndex =  ltcdb.year_to_band(os.path.basename(vertYrsFile), 1) #TODO: make sure that the offset is correct here - compared the old and new year_to_band functions results and using adj 1 makes them equal, so should be okay, but look at actual numbers
  xSize = srcYrs.RasterXSize
  ySize = srcYrs.RasterYSize
  blockSize = 256
  
  # get info to print progress
  nBlocks = 0
  nBlock = 0
  for y in xrange(0, ySize, blockSize):
    for x in xrange(0, xSize, blockSize):
      nBlocks += 1
  
  
  ##############################################################################
  
  for y in xrange(0, ySize, blockSize):
    #yRange = range(0, ySize, blockSize)
    #y=yRange[4]
    if y + blockSize < ySize:
      rows = blockSize
    else:
      rows = ySize - y
    for x in xrange(0, xSize, blockSize):
      #xRange = range(0, xSize, blockSize)
      #x=xRange[4]
      if x + blockSize < xSize:
        cols = blockSize
      else:
        cols = xSize - x
      
      
      # print progress
      nBlock += 1.0
      progress = (nBlock)/nBlocks
      ltcdb.update_progress(progress)
      
      
      npYrs = srcYrs.ReadAsArray(x, y, cols, rows)
         
      npOutTCB = dstTCB.ReadAsArray(x, y, cols, rows)
      npOutTCG = dstTCG.ReadAsArray(x, y, cols, rows)
      npOutTCW = dstTCW.ReadAsArray(x, y, cols, rows)
      
      npFtvTCB = srcFtvTCB.ReadAsArray(x, y, cols, rows)
      npFtvTCG = srcFtvTCG.ReadAsArray(x, y, cols, rows)
      npFtvTCW = srcFtvTCW.ReadAsArray(x, y, cols, rows)
      
      nVerts, subYsize, subXsize = npYrs.shape
      for subY in xrange(subYsize):
        #subY = 0
        #progress = (y+1.0)/ySize
        #update_progress(progress)    
        for subX in xrange(subXsize):
          #subX = 0
          vertYrsPix = npYrs[:, subY, subX]
          
          # check to see if this is a NoData pixel    
          if (vertYrsPix == -9999).all():   #0
            continue
          
          vertIndex = vertYrsPix[np.where(vertYrsPix != 0)[0]]
          theseBands = ftvIndex[vertIndex]
          replaceThese = range(len(theseBands))
          npOutTCB[replaceThese, subY, subX] = npFtvTCB[theseBands, subY, subX]
          npOutTCG[replaceThese, subY, subX] = npFtvTCG[theseBands, subY, subX]
          npOutTCW[replaceThese, subY, subX] = npFtvTCW[theseBands, subY, subX]
          
        for b in range(nVerts):
          ltcdb.write_array(dstTCB, b, npOutTCB, x, y)
          ltcdb.write_array(dstTCG, b, npOutTCG, x, y)
          ltcdb.write_array(dstTCW, b, npOutTCW, x, y)
        
  # close the output files
  dstTCB = None
  dstTCG = None
  dstTCW = None
  srcYrs = None
  srcFtvTCB = None
  srcFtvTCG = None
  srcFtvTCW = None

  """
  # make background values -9999
  for outPut in outPuts:
    nBands = gdal.Open(outPut).RasterCount
    bands = ' '.join(['-b '+str(band) for band in range(1,nBands+1)])
    cmd = 'gdal_rasterize -i -burn -9999 '+bands+' '+outShpFile+' '+outPut
    subprocess.call(cmd, shell=True)
  """

print('\nDone!')      
print("LT-GEE data unpacking took {} minutes".format(round((time.time() - startTime)/60, 1)))

  
    
    
      
