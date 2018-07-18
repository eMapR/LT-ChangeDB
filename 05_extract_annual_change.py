# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 16:16:42 2017

@author: braatenj
"""

import time
import os
import sys
import numpy as np
from glob import glob
import csv
from osgeo import gdal


# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)

import ltcdb






#def update_progress(progress):
#  sys.stdout.write( '\r   {0}% {1}'.format(int(math.floor(progress*100)), 'done'))
#  sys.stdout.flush()



  
#################################################################################################################
#################################################################################################################


headDir = ltcdb.get_dir("Select the project head folder")

#headDir = r'D:\work\proj\al\gee_test\test'


if headDir == '':
  sys.exit('ERROR: No folder containing LT-GEE files was selected.\nPlease re-run the script and select a folder.')

segDir = os.path.join(headDir, 'raster', 'landtrendr', 'segmentation')
if not os.path.isdir(segDir):
  sys.exit('ERROR: Can\'t find the segmentation folder.\nTrying to find it at this location: '+segDir+'\nIt\'s possible you provided an incorrect project head folder.\nPlease re-run the script and select the project head folder.')

# could try to find the gee_chunk folder
#[x[0] for x in os.walk(chunkDir)]



"""
segDir = ltcdb.get_dir("Select a folder that contains LT segmentation files\n\n(*\\raster\\landtrendr\\segmentation\\*)")
if segDir == '':
  sys.exit('ERROR: No folder containing LT segmentation files was selected.\nPlease re-run the script and select a folder.')
"""




segDir = os.path.normpath(segDir)
#segDir = r'D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation'
ltRunDirs = [os.path.join(segDir, thisRunDir) for thisRunDir in os.listdir(segDir)]
minMags = []
for segDir in ltRunDirs:
  # get the min mag
  minMagGood = 0
  while minMagGood is 0:
    minMag = raw_input('\nRegarding LT run: '+os.path.basename(segDir) + '\nWhat is the desired minimum disturbance magnitude: ')
    try:
      minMag = int(minMag)
      minMag = abs(minMag) * -1
      minMagGood = 1
    except ValueError: 
      print('\n')
      print('ERROR: The selected value cannot be converted to an integer.')
      print('       Please try again and make sure to enter a number.')
  
  minMags.append(minMag)





for i, segDir in enumerate(ltRunDirs):
  i=0
  segDir = ltRunDirs[0]
  
  
  print('\n\nWorking on LT run: ' + os.path.basename(segDir))
  vertYrsFile = glob(segDir+'/*vert_yrs.tif')
  if len(vertYrsFile) == 0:
    sys.exit('ERROR: There was no *vert_yrs.tif file in the folder selected.\nPlease fix this.')   # TODO make this a better error message
  
  #TODO need to deal with multiple finds
  
  pieces = segDir.split(os.sep)
  bname = pieces[-1]
  outDir = os.path.normpath(os.path.join('/'.join(pieces[0:-2]), 'change', bname))
  if not os.path.exists(outDir):
    os.makedirs(outDir)
  
  
  """
  #vertYrsFile = 'D:/work/proj/al/gee_test/raster/landtrendr/segmentation/ltee_nccn_mora_seg08test_06010930_20180109_vert_yrs.bsq'
  outDir = 'D:/work/proj/al/gee_test/raster/landtrendr/annual_disturbance/'
  startYear = 1984
  endYear = 2016
  mmu = 9
  minMag = -50
  
  #flipper = -1    
  #nYears = endYear-startYear+1
  """
  #################################################################################################################
  
  # get the vert fit file
  vertYrsFile = vertYrsFile[0]
  vertFitIDXFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_idx.tif')
  vertFitTCBFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcb.tif')
  vertFitTCGFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcg.tif')
  vertFitTCWFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcw.tif')
  
  #TODO need to error check for existence of all files that we just identified names for
  if not os.path.exists(vertFitTCBFile): #vertFitIDXFile
    sys.exit('ERROR: There was no *vert_fit_tcb.tif file in the folder selected.\nPlease fix this.') 
  
  
  
  #segDir = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930"
  #vertYrsFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-vert_yrs.tif"
  #vertFitFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-vert_fit.tif"
  #info = get_info('PARK_CODE-MORA-NBR-7-19842017-06010930')
  
  
  # get the min mag
  minMag = minMags[i]
  
  startTime = time.time()

  
  ###################################################################################
  # get run info
  info = ltcdb.get_info(bname)
  indexID = info['indexID']
  startYear = info['startYear']
  endYear = info['endYear']
  startYearChng = startYear+1
  
  
  
  ###################################################################################
  
  
  # make new file names
  distInfoOutYrs = os.path.join(outDir, bname+'-change_yrs.tif')
  distInfoOutDur = os.path.join(outDir, bname+'-change_dur.tif')
  distInfoOutMagIDX = os.path.join(outDir, bname+'-change_idx_mag.tif')
  #distInfoOutPreIDX = os.path.join(outDir, bname+'-change_idx_pre.tif')
  distInfoOutMagTCB = os.path.join(outDir, bname+'-change_tcb_mag.tif')
  distInfoOutPreTCB = os.path.join(outDir, bname+'-change_tcb_pre.tif')
  distInfoOutPostTCB = os.path.join(outDir, bname+'-change_tcb_post.tif')
  distInfoOutMagTCG = os.path.join(outDir, bname+'-change_tcg_mag.tif')
  distInfoOutPreTCG = os.path.join(outDir, bname+'-change_tcg_pre.tif')
  distInfoOutPostTCG = os.path.join(outDir, bname+'-change_tcg_post.tif')
  distInfoOutMagTCW = os.path.join(outDir, bname+'-change_tcw_mag.tif')
  distInfoOutPreTCW = os.path.join(outDir, bname+'-change_tcw_pre.tif')
  distInfoOutPostTCW = os.path.join(outDir, bname+'-change_tcw_post.tif')
  
  # make a summary stats file
  summaryInfoFile = os.path.join(outDir, bname+'-change_attributes.csv') 
  summaryInfo = [
      [distInfoOutDur   , 'dur'   , 'con', 'annual', 'int'],  # con (continuous) or cat (categorical)
      [distInfoOutMagIDX, 'idxMag', 'con', 'annual', 'int'],
      [distInfoOutMagTCB, 'tcbMag', 'con', 'annual', 'int'],
      [distInfoOutMagTCG, 'tcgMag', 'con', 'annual', 'int'],
      [distInfoOutMagTCW, 'tcwMag', 'con', 'annual', 'int'],
      #[distInfoOutPreIDX, 'idxPre', 'con', 'annual', 'int'],
      [distInfoOutPreTCB, 'tcbPre', 'con', 'annual', 'int'],
      [distInfoOutPreTCG, 'tcgPre', 'con', 'annual', 'int'],
      [distInfoOutPreTCW, 'tcwPre', 'con', 'annual', 'int'],
      
      [distInfoOutPostTCB, 'tcbPost', 'con', 'annual', 'int'],
      [distInfoOutPostTCG, 'tcgPost', 'con', 'annual', 'int'],
      [distInfoOutPostTCW, 'tcwPost', 'con', 'annual', 'int'],
  ]
  
  with open(summaryInfoFile, 'w') as f:
      writer = csv.writer(f, lineterminator='\n')
      writer.writerows(summaryInfo)
  
  
  
  # create the blanks  needs to be a copy of an ftv minus 1 band
  outPuts = [distInfoOutYrs, distInfoOutDur, 
             distInfoOutMagIDX, #distInfoOutPreIDX,
             distInfoOutMagTCB, distInfoOutPreTCB, distInfoOutPostTCB,
             distInfoOutMagTCG, distInfoOutPreTCG, distInfoOutPostTCG,
             distInfoOutMagTCW, distInfoOutPreTCW, distInfoOutPostTCW]
  
  ftvTemplate = glob(os.path.dirname(vertYrsFile)+'/*ftv_tcb.tif')
  
  if len(ftvTemplate) == 0: #vertFitIDXFile
    sys.exit('ERROR: There was no *ftv_tcb.tif file in the folder selected.\nPlease fix this.')
  
  nBands = ltcdb.make_output_blanks(ftvTemplate[0], outPuts, -1) # use a TC FTV file as a template for image specs
  
  
  ###################################################################################
  
  # get run info
  info = ltcdb.get_info(bname)
  indexID = info['indexID']
  startYear = info['startYear']
  endYear = info['endYear']
  startYearChng = startYear+1
  
  ##############################################################################
  # figure out if we did to flip the data over
  # available spectral indices: ['NBR', -1], ['B5', 1], ['NDVI', -1], ['TCB', 1], ['NDSI', -1], ['TCG', -1], ['B3', 1]];
  flippers = {
    'NBR' : -1,
    'B5'  :  1,
    'NDVI': -1,
    'TCB' :  1,
    'NDSI': -1,
    'TCG' : -1,
    'B3'  :  1,
    'NBRz':  1,
    'ENC' :  1
  }
  flipper = flippers[indexID]*-1
  
  ##############################################################################
  # open inputs
  srcYrs = gdal.Open(vertYrsFile)
  srcFitIDX = gdal.Open(vertFitIDXFile)
  srcFitTCB = gdal.Open(vertFitTCBFile)
  srcFitTCG = gdal.Open(vertFitTCGFile)
  srcFitTCW = gdal.Open(vertFitTCWFile)
  
  
  # open the output files
  dstYrs = gdal.Open(distInfoOutYrs, gdal.GA_Update)
  dstDur = gdal.Open(distInfoOutDur, gdal.GA_Update)
  dstMagIDX = gdal.Open(distInfoOutMagIDX, gdal.GA_Update)
  #dstPreIDX = gdal.Open(distInfoOutPreIDX, gdal.GA_Update)
  dstMagTCB = gdal.Open(distInfoOutMagTCB, gdal.GA_Update)
  dstPreTCB = gdal.Open(distInfoOutPreTCB, gdal.GA_Update)
  dstPostTCB = gdal.Open(distInfoOutPostTCB, gdal.GA_Update)
  dstMagTCG = gdal.Open(distInfoOutMagTCG, gdal.GA_Update)
  dstPreTCG = gdal.Open(distInfoOutPreTCG, gdal.GA_Update)
  dstPostTCG = gdal.Open(distInfoOutPostTCG, gdal.GA_Update)
  dstMagTCW = gdal.Open(distInfoOutMagTCW, gdal.GA_Update)
  dstPreTCW = gdal.Open(distInfoOutPreTCW, gdal.GA_Update)
  dstPostTCW = gdal.Open(distInfoOutPostTCW, gdal.GA_Update)
  
  
  
  
  ##############################################################################
  
  # set some size variables
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
      
      # load the SRC vert data for yrs, idx, and tc 
      npYrs = srcYrs.ReadAsArray(x, y, cols, rows)
      npFitIDX = srcFitIDX.ReadAsArray(x, y, cols, rows)    
      npFitTCB = srcFitTCB.ReadAsArray(x, y, cols, rows)
      npFitTCG = srcFitTCG.ReadAsArray(x, y, cols, rows)
      npFitTCW = srcFitTCW.ReadAsArray(x, y, cols, rows)
  
      # load the annual IDX output chunk as an np array
      npOutYrs = dstYrs.ReadAsArray(x, y, cols, rows)
      npOutDur = dstDur.ReadAsArray(x, y, cols, rows)
      npOutMagIDX = dstMagIDX.ReadAsArray(x, y, cols, rows)
      #npOutPreIDX = dstPreIDX.ReadAsArray(x, y, cols, rows)
      
      # load the annual TC output chunk as an np array
      npOutMagTCB = dstMagTCB.ReadAsArray(x, y, cols, rows)
      npOutPreTCB = dstPreTCB.ReadAsArray(x, y, cols, rows)
      npOutPostTCB = dstPostTCB.ReadAsArray(x, y, cols, rows)
      npOutMagTCG = dstMagTCG.ReadAsArray(x, y, cols, rows)
      npOutPreTCG = dstPreTCG.ReadAsArray(x, y, cols, rows)
      npOutPostTCG = dstPostTCG.ReadAsArray(x, y, cols, rows)
      npOutMagTCW = dstMagTCW.ReadAsArray(x, y, cols, rows)
      npOutPreTCW = dstPreTCW.ReadAsArray(x, y, cols, rows)
      npOutPostTCW = dstPostTCW.ReadAsArray(x, y, cols, rows)
  
      # TODO flip the magnitude if need - is this needed - how best to deal with this 
      if flipper == -1:
        npFitIDX = npFitIDX * flipper
      nVerts, subYsize, subXsize = npYrs.shape
   
      for subY in xrange(subYsize):
        #subY = 0
        #progress = (y+1.0)/ySize
        #update_progress(progress)    
        for subX in xrange(subXsize):
          #subX = 0
          # read in the vert years for this pixel
          vertYrs = npYrs[:, subY, subX]
  
          # check to see if this is a NoData pixel    
          if (vertYrs == -9999).all():
            continue
  
          # get indices of the verts
          vertIndex = np.where(vertYrs != 0)[0]
          
          # extract the vert years
          vertYrs = vertYrs[vertIndex]
  
          # extract this pixels vert fit - going to see if there are disturbances
          vertValsIDX = npFitIDX[vertIndex, subY, subX]
  
          # get the fit value delta for each segment
          segMagIDX = ltcdb.get_delta(vertValsIDX)
          
          # figure out which segs are disturbance
          distIndex = np.where(segMagIDX < minMag)[0] # why have to index 0?
          
          # check to see if there are any disturbances
          if len(distIndex) == 0:
            continue
  
          # get vertVals for TC
          vertValsTCB = npFitTCB[vertIndex, subY, subX]
          vertValsTCG = npFitTCG[vertIndex, subY, subX]
          vertValsTCW = npFitTCW[vertIndex, subY, subX]
  
          #  extract year of detection yod
          segStartYear = vertYrs[:-1]+1
          yod = segStartYear[distIndex]
          
          # extract the dur for this disturbance
          segStartYr = vertYrs[:-1]
          segEndYr = vertYrs[1:]
          segDur = segEndYr - segStartYr
          dur = segDur[distIndex]
          
          # extract the mags for the disturbance(s)
          magIDX = segMagIDX[distIndex]
          magTCB = ltcdb.get_delta(vertValsTCB)[distIndex]
          magTCG = ltcdb.get_delta(vertValsTCG)[distIndex]
          magTCW = ltcdb.get_delta(vertValsTCW)[distIndex]
          
          # extract the predist value this disturbance
          #preIDX = vertValsIDX[distIndex]
          #if flipper == -1:
            #preIDX = preIDX * flipper
          
          preTCB = vertValsTCB[distIndex]
          preTCG = vertValsTCG[distIndex]
          preTCW = vertValsTCW[distIndex]
            
          postDistIndex = [ix+1 for ix in distIndex]
          postTCB = vertValsTCB[postDistIndex]
          postTCG = vertValsTCG[postDistIndex]
          postTCW = vertValsTCW[postDistIndex]
          
          
          # replace the pixel values of the ouput series 
          theseBands = [thisYear-startYearChng for thisYear in yod]
          npOutYrs[theseBands, subY, subX] = yod
          npOutDur[theseBands, subY, subX] = dur
          npOutMagIDX[theseBands, subY, subX] = magIDX
          npOutMagTCB[theseBands, subY, subX] = magTCB
          npOutMagTCG[theseBands, subY, subX] = magTCG
          npOutMagTCW[theseBands, subY, subX] = magTCW        
          #npOutPreIDX[theseBands, subY, subX] = preIDX
          npOutPreTCB[theseBands, subY, subX] = preTCB
          npOutPreTCG[theseBands, subY, subX] = preTCG
          npOutPreTCW[theseBands, subY, subX] = preTCW
          
          npOutPostTCB[theseBands, subY, subX] = postTCB
          npOutPostTCG[theseBands, subY, subX] = postTCG
          npOutPostTCW[theseBands, subY, subX] = postTCW
  
  
  
      for b in range(nBands):
        '''
        dataBand = dstYrs.GetRasterBand(b+1)
        data = npOutYrs[b, :, :]
        dataBand.WriteArray(data, x, y)
        '''
        ltcdb.write_array(dstYrs, b, npOutYrs, x, y)
        ltcdb.write_array(dstDur, b, npOutDur, x, y)
        ltcdb.write_array(dstMagIDX, b, npOutMagIDX, x, y)
        ltcdb.write_array(dstMagTCB, b, npOutMagTCB, x, y)
        ltcdb.write_array(dstMagTCG, b, npOutMagTCG, x, y)
        ltcdb.write_array(dstMagTCW, b, npOutMagTCW, x, y)
        #ltcdb.write_array(dstPreIDX, b, npOutPreIDX, x, y)
        ltcdb.write_array(dstPreTCB, b, npOutPreTCB, x, y)
        ltcdb.write_array(dstPreTCG, b, npOutPreTCG, x, y)
        ltcdb.write_array(dstPreTCW, b, npOutPreTCW, x, y)
        
        ltcdb.write_array(dstPostTCB, b, npOutPostTCB, x, y)
        ltcdb.write_array(dstPostTCG, b, npOutPostTCG, x, y)
        ltcdb.write_array(dstPostTCW, b, npOutPostTCW, x, y)
    
  # close the output files
  srcYrs = None
  srcFitIDX = None
  srcFitTCB = None
  srcFitTCG = None
  srcFitTCW = None
  
  dstYrs = None
  dstDur = None
  dstMagIDX = None
  dstMagTCB = None
  dstMagTCG = None
  dstMagTCW = None
  dstPreIDX = None
  dstPreTCB = None
  dstPreTCG = None
  dstPreTCW = None
  dstPostTCB = None
  dstPostTCG = None
  dstPostTCW = None


print('\n\nDone!')      
print("Change identification took {} minutes".format(round((time.time() - startTime)/60, 1)))


