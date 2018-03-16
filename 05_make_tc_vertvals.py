# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 11:56:59 2018

@author: braatenj
"""

import ltcdb
import os
from osgeo import gdal
import numpy as np


# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)


# read in vert vertYr file
vertYrsFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-vert_yrs.tif"

# make a copy of vert files for tc vals
vertTCBfitFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcb.tif')
vertTCGfitFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcg.tif')
vertTCWfitFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcw.tif')
outPuts = [vertTCBfitFile, vertTCGfitFile, vertTCWfitFile]

ltcdb.make_output_blanks(vertYrsFile, outPuts, 0)



ftvTCBfitFile = vertYrsFile.replace('vert_yrs.tif', 'ftv_tcb.tif')
ftvTCGfitFile = vertYrsFile.replace('vert_yrs.tif', 'ftv_tcg.tif')
ftvTCWfitFile = vertYrsFile.replace('vert_yrs.tif', 'ftv_tcw.tif')



# open the output files for update
dstTCB = gdal.Open(vertTCBfitFile, gdal.GA_Update)
dstTCG = gdal.Open(vertTCGfitFile, gdal.GA_Update)
dstTCW = gdal.Open(vertTCWfitFile, gdal.GA_Update)

# open the vertYrs file for read
srcYrs = gdal.Open(vertYrsFile, gdal.GA_ReadOnly)

srcFtvTCB = gdal.Open(ftvTCBfitFile, gdal.GA_ReadOnly)
srcFtvTCG = gdal.Open(ftvTCGfitFile, gdal.GA_ReadOnly)
srcFtvTCW = gdal.Open(ftvTCWfitFile, gdal.GA_ReadOnly)

##############################################################################

info = ltcdb.get_info(os.path.basename(vertYrsFile))

# set some size variables
startYear = info['startYear']
endYear = info['endYear']
nYears = (endYear - startYear)+1
ftvIndex = np.array([0]*(startYear)+range(0, nYears))
xSize = srcYrs.RasterXSize
ySize = srcYrs.RasterYSize
blockSize = 256

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
        if (vertYrsPix == 0).all():
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
