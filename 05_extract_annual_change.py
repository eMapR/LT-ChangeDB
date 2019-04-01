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


# change working directory to this script's dir so we can load the ltcdb library
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)
import ltcdb

# get the head folder
headDir = ltcdb.get_dir("Select the project head folder", scriptDname)
ltcdb.is_headDir(headDir)

# get dir paths we need 
segDir = ltcdb.dir_path(headDir, 'rLs')
changeDir = ltcdb.dir_path(headDir, 'rLc')

# list the run directories in the seg folder 
ltRunDirs = [os.path.join(segDir, thisRunDir) for thisRunDir in os.listdir(segDir)]

# get the min change for each 
changeTypes = []
minMags = []
collapseEm = []
for segDir in ltRunDirs:
  # get the min mag
  changeTypeGood = 0
  while changeTypeGood is 0:
    changeType = raw_input('\nRegarding LT run: '+os.path.basename(segDir) + '\nWhat change do you want to map (disturbance or growth)?: ')
    changeType = str(changeType).lower()
    if changeType in ['growth', 'disturbance']:
      changeTypeGood = 1
      minMagAdj = 1 if changeType == 'disturbance' else -1
    else:
      print('\n')
      print('ERROR: The selected change type does not equal either disturbance or growth.')
      print('       Please try again and make sure to enter only a single accepted option.')
  changeTypes.append(changeType)

  minMagGood = 0
  while minMagGood is 0:
    minMag = raw_input('\nRegarding LT run: '+os.path.basename(segDir) + '\nWhat is the desired minimum change magnitude: ')
    try:
      minMag = int(minMag)
      minMag = abs(minMag) * -1 * minMagAdj
      minMagGood = 1
    except ValueError: 
      print('\n')
      print('ERROR: The selected value cannot be converted to an integer.')
      print('       Please try again and make sure to enter a number.')
  minMags.append(minMag)
  
  collapseGood = 0
  while collapseGood is 0:
    collapse = raw_input('\nRegarding LT run: '+os.path.basename(segDir) + '\nMaximum segment slope difference to collapse (-1 to ignore): ')
    try:
      collapse = float(minMag)
      collapseGood = 1
    except ValueError: 
      print('\n')
      print('ERROR: The selected value cannot be converted to a float value.')
      print('       Please try again and make sure to enter a number.')
  collapseEm.append(collapse)
  


# iterate through each run
for i, segDir in enumerate(ltRunDirs):
  #i=0
  #segDir = ltRunDirs[0]

  print('\n\nWorking on LT run: ' + os.path.basename(segDir))
  
  # get the vert_yrs.tif
  vertYrsFile = glob(segDir+'/*vert_yrs.tif')
  if len(vertYrsFile) == 0:
    sys.exit('\nERROR: There was no *vert_yrs.tif file in the folder selected.\n       Please fix this.')   # TODO make this a better error message
  vertYrsFile = vertYrsFile[0]
  #TODO need to deal with multiple finds
  
  # make a change output dir for this run
  bname = os.path.basename(segDir)+'-'+changeTypes[i]+'_'+str(abs(minMags[i]))
  outDir = os.path.join(changeDir, bname)
  if os.path.exists(outDir):
    sys.exit('\nERROR: Directory '+outDir+' already exits.\n       Please re-run with different change type and/or magnitude, if so desired.')
  else:
    os.makedirs(outDir)
  
  
  #################################################################################################################
  
  # make output file names
  vertFitIDXFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_idx.tif')
  vertFitTCBFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcb.tif')
  vertFitTCGFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcg.tif')
  vertFitTCWFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcw.tif')
  
  #TODO need to error check for existence of all files that we just identified names for
  if not os.path.exists(vertFitTCBFile): #vertFitIDXFile
    sys.exit('ERROR: There was no *vert_fit_tcb.tif file in the folder selected.\nPlease fix this.') 
  
  # start tracking time
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
  

  # create the blanks  needs to be a copy of an ftv minus 1 band
  outPuts = [distInfoOutYrs, distInfoOutDur, 
             distInfoOutMagIDX, #distInfoOutPreIDX,
             distInfoOutMagTCB, distInfoOutPreTCB, distInfoOutPostTCB,
             distInfoOutMagTCG, distInfoOutPreTCG, distInfoOutPostTCG,
             distInfoOutMagTCW, distInfoOutPreTCW, distInfoOutPostTCW]
  
  # find the tc tfv files
  tcbFtv = glob(os.path.dirname(vertYrsFile)+'/*ftv_tcb.tif') 
  tcgFtv = glob(os.path.dirname(vertYrsFile)+'/*ftv_tcg.tif')
  tcwFtv = glob(os.path.dirname(vertYrsFile)+'/*ftv_tcw.tif')

  # make sure the tc ftv fiels are found
  for fn, srch in zip([tcbFtv, tcgFtv, tcwFtv], ['*ftv_tcb.tif', '*ftv_tcg.tif', '*ftv_tcw.tif',]):
    if len(fn) != 1:
      sys.exit('ERROR: There was no '+srch+' file in the folder selected.\nPlease fix this.') 
  
  tcbFtv = tcbFtv[0]
  tcgFtv = tcgFtv[0]
  tcwFtv = tcwFtv[0]
  
  
  # make blank copies for annual change writing to  
  nBands = ltcdb.make_output_blanks(tcbFtv, outPuts, -1) # use a TC FTV file as a template for image specs
  
  
  # make a summary stats file
  summaryInfoFile = os.path.join(outDir, bname+'-change_attributes.csv') 
  summaryInfo = [
      [distInfoOutDur   , 'dur'   , 'con', 'annual', 'int', '0', '1'],  # con (continuous) or cat (categorical)
      [distInfoOutMagIDX, 'idxMag', 'con', 'annual', 'int', '0', '1'],
      [distInfoOutMagTCB, 'tcbMag', 'con', 'annual', 'int', '0', '1'],
      [distInfoOutMagTCG, 'tcgMag', 'con', 'annual', 'int', '0', '1'],
      [distInfoOutMagTCW, 'tcwMag', 'con', 'annual', 'int', '0', '1'],
      #[distInfoOutPreIDX, 'idxPre', 'con', 'annual', 'int'],
      [distInfoOutPreTCB, 'tcbPre', 'con', 'annual', 'int', '0', '1'],
      [distInfoOutPreTCG, 'tcgPre', 'con', 'annual', 'int', '0', '1'],
      [distInfoOutPreTCW, 'tcwPre', 'con', 'annual', 'int', '0', '1'],
      
      [distInfoOutPostTCB, 'tcbPst', 'con', 'annual', 'int', '0', '1'],
      [distInfoOutPostTCG, 'tcgPst', 'con', 'annual', 'int', '0', '1'],
      [distInfoOutPostTCW, 'tcwPst', 'con', 'annual', 'int', '0', '1'],
      
      [tcbFtv, 'tcbPst', 'con', 'dynamic', 'int', '1|3|7|15', '1'],
      [tcbFtv, 'tcgPst', 'con', 'dynamic', 'int', '1|3|7|15', '1'],
      [tcbFtv, 'tcwPst', 'con', 'dynamic', 'int', '1|3|7|15', '1']
  ]
  
  with open(summaryInfoFile, 'w') as f:
      writer = csv.writer(f, lineterminator='\n')
      writer.writerows(summaryInfo)
  
  
  
  
  ###################################################################################
  
  # get run info
  info = ltcdb.get_info(bname)
  indexID = info['indexID']
  startYear = info['startYear']
  endYear = info['endYear']
  startYearChng = startYear+1
  
  ##############################################################################
  # figure out if we did to flip the data over - we always want disturbance to be a negative delta
  # available spectral indices: ['NBR', -1], ['B5', 1], ['NDVI', -1], ['TCB', 1], ['NDSI', -1], ['TCG', -1], ['B3', 1]];
  # TODO: need to error if the index is not found
  flippers = {
    'NBR' : -1,
    'B5'  :  1,
    'NDVI': -1,
    'TCB' :  1,
    'NDSI': -1,
    'TCG' : -1,
    'B3'  :  1,
    'NBRz':  1,
    'ENC' :  1,
    'Band5z': 1
  }
  flipper = flippers[indexID]*-1 # above are the flipper from LT-GEE - there dist is considered postive delta
  
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
      ltcdb.update_progress(progress, '   ')
      
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
          
          if collapseEm[i] != -1:
            vertIndex = ltcdb.collapse_segs(vertYrs, npFitIDX[:, subY, subX], collapseEm[i])
          else:
            vertIndex = np.where(vertYrs != 0)[0]
          
          # get vertVals for TC
          vertValsTCB = npFitTCB[vertIndex, subY, subX]
          if len(np.where(vertValsTCB == -9999)[0]) != 0:
            continue
          
          vertValsTCG = npFitTCG[vertIndex, subY, subX]
          vertValsTCW = npFitTCW[vertIndex, subY, subX]
          

          # extract the vert years
          vertYrs = vertYrs[vertIndex]
  
          # extract this pixels vert fit - going to see if there are disturbances
          vertValsIDX = npFitIDX[vertIndex, subY, subX]
  
          # get the fit value delta for each segment
          segMagIDX = ltcdb.get_delta(vertValsIDX)
          
          # figure out which segs are disturbance
          if changeTypes[i] == 'disturbance':
            distIndex = np.where(segMagIDX < minMags[i])[0] # why have to index 0?
          else:
            distIndex = np.where(segMagIDX > minMags[i])[0] # why have to index 0?

          
          # check to see if there are any disturbances
          if len(distIndex) == 0:
            continue
  

  
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


