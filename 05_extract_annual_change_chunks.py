# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 16:16:42 2017

@author: braatenj
"""


import os
import sys   #sys.exit() - if numpy and gdal are not found print to use script 01 and exit
import subprocess
from osgeo import gdal, ogr, osr
import numpy as np
import math
import Tkinter, tkFileDialog
from glob import glob
from shutil import copyfile
import csv


# change working directory to this script's dir
scriptAbsPath = os.path.abspath(__file__)
scriptDname = os.path.dirname(scriptAbsPath)
os.chdir(scriptDname)

import ltcdb


def write_raster(data, filename, prj, origin, driver, dtype=gdal.GDT_Int16, pixel_size=30):
  # origin = [X, Y] offset
  # srs = template.GetProjectionRef()
  
  nDataDims = len(data.shape)
  if nDataDims == 2:
    rows, cols = data.shape
    bands = 1
  else:
    bands, rows, cols = data.shape

  #driver = gdal.GetDriverByName('GTiff')
  outRaster = gdal.GetDriverByName(driver).Create(filename, cols, rows, bands, dtype)

  outRaster.SetGeoTransform((origin[0], pixel_size, 0, origin[1], 0, -pixel_size))
  outRaster.SetProjection(prj)

  for i in range(bands):
    band = outRaster.GetRasterBand(i+1)
    if nDataDims == 2:        
      band.WriteArray(data)
    else:
      band.WriteArray(data[i,:,:])
  print 'Raster written to ', filename
    

def gdal_sieve(src_filename, mmu):
  # mmu the raster
  format = 'GTiff' # -of
  connectedness = 8 # -4 (4) or -8 (8)
  quiet_flag = 0 # -q -quiet | bool
  threshold = mmu # -st
  mask = 'default' # -nomask -mask
  src_filename = src_filename # None
  dst_filename = None

  gdal.AllRegister()

  # =============================================================================
  # 	Verify we have next gen bindings with the sievefilter method.
  # =============================================================================
  try:
    gdal.SieveFilter
  except:
    print('')
    print('gdal.SieveFilter() not available.  You are likely using "old gen"')
    print('bindings or an older version of the next gen bindings.')
    print('')
    sys.exit(1)

  # =============================================================================
  #	Open source file
  # =============================================================================

  if dst_filename is None:
    src_ds = gdal.Open( src_filename, gdal.GA_Update )
  else:
    src_ds = gdal.Open( src_filename, gdal.GA_ReadOnly )

  if src_ds is None:
    print('Unable to open %s ' % src_filename)
    sys.exit(1)

  srcband = src_ds.GetRasterBand(1)

  if mask is 'default':
    maskband = srcband.GetMaskBand()
  elif mask is 'none':
    maskband = None
  else:
    mask_ds = gdal.Open( mask )
    maskband = mask_ds.GetRasterBand(1)
  
  # =============================================================================
  #       Create output file if one is specified.
  # =============================================================================

  if dst_filename is not None:

    drv = gdal.GetDriverByName(format)
    dst_ds = drv.Create( dst_filename,src_ds.RasterXSize, src_ds.RasterYSize,1,
      						  srcband.DataType )
    wkt = src_ds.GetProjection()
    if wkt != '':
      dst_ds.SetProjection( wkt )
    dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )

    dstband = dst_ds.GetRasterBand(1)
  else:
    dstband = srcband 
  
  # =============================================================================
  #	Invoke algorithm.
  # =============================================================================

  if quiet_flag:
    prog_func = None
  else:
    prog_func = gdal.TermProgress

    result = gdal.SieveFilter( srcband, maskband, dstband,
    							      threshold, connectedness,
    							      callback = prog_func )

    src_ds = None
    dst_ds = None
    mask_ds = None



def gdal_polygonize(mask, inFile, outFile):

  format = 'ESRI shapefile'
  options = []
  quiet_flag = 0
  src_filename = inFile
  src_band_n = 1
  
  dst_filename = outFile
  dst_layername = None
  dst_fieldname = None
  dst_field = -1
  
  mask = mask #'default'

  options.append('8CONNECTED=8')
  
  if dst_layername is None:
      dst_layername = 'out'

  # =============================================================================
  # 	Verify we have next gen bindings with the polygonize method.
  # =============================================================================
  try:
    gdal.Polygonize
  except:
    print('')
    print('gdal.Polygonize() not available.  You are likely using "old gen"')
    print('bindings or an older version of the next gen bindings.')
    print('')
    sys.exit(1)

  # =============================================================================
  #	Open source file
  # =============================================================================
  
  src_ds = gdal.Open( src_filename )
  
  if src_ds is None:
    print('Unable to open %s' % src_filename)
    sys.exit(1)
  
  srcband = src_ds.GetRasterBand(src_band_n)
  
  if mask is 'default':
    maskband = srcband.GetMaskBand()
  elif mask is 'none':
    maskband = None
  else:
    mask_ds = gdal.Open( mask )
    maskband = mask_ds.GetRasterBand(1)


  # =============================================================================
  #       Try opening the destination file as an existing file.
  # =============================================================================
  
  try:
    gdal.PushErrorHandler( 'CPLQuietErrorHandler' )
    dst_ds = ogr.Open( dst_filename, update=1 )
    gdal.PopErrorHandler()
  except:
    dst_ds = None

  # =============================================================================
  # 	Create output file.
  # =============================================================================
  if dst_ds is None:
    drv = ogr.GetDriverByName(format)
    if not quiet_flag:
        print('Creating output %s of format %s.' % (dst_filename, format))
    dst_ds = drv.CreateDataSource( dst_filename )


  # =============================================================================
  #       Find or create destination layer.
  # =============================================================================
  try:
    dst_layer = dst_ds.GetLayerByName(dst_layername)
  except:
    dst_layer = None
  
  if dst_layer is None:
  
    srs = None
    if src_ds.GetProjectionRef() != '':
      srs = osr.SpatialReference()
      srs.ImportFromWkt( src_ds.GetProjectionRef() )
  
    dst_layer = dst_ds.CreateLayer(dst_layername, geom_type=ogr.wkbPolygon, srs = srs )
  
    if dst_fieldname is None:
      dst_fieldname = 'DN'
  
    fd = ogr.FieldDefn( dst_fieldname, ogr.OFTInteger )
    dst_layer.CreateField( fd )
    dst_field = 0
  else:
    if dst_fieldname is not None:
      dst_field = dst_layer.GetLayerDefn().GetFieldIndex(dst_fieldname)
      if dst_field < 0:
        print("Warning: cannot find field '%s' in layer '%s'" % (dst_fieldname, dst_layername))


  # =============================================================================
  #	Invoke algorithm.
  # =============================================================================
  
  if quiet_flag:
    prog_func = None
  else:
    prog_func = gdal.TermProgress
  
  result = gdal.Polygonize( srcband, maskband, dst_layer, dst_field, options,
                            callback = prog_func )
  
  srcband = None
  src_ds = None
  dst_ds = None
  mask_ds = None



def zonal_stats(feat, input_zone_polygon, input_value_raster): #, raster_band

  # Open data
  raster = gdal.Open(input_value_raster)
  shp = ogr.Open(input_zone_polygon)
  lyr = shp.GetLayer()
  
  # Get raster georeference info
  transform = raster.GetGeoTransform()
  xOrigin = transform[0]
  yOrigin = transform[3]
  pixelWidth = transform[1]
  pixelHeight = transform[5]
  
  # Reproject vector geometry to same projection as raster
  #sourceSR = lyr.GetSpatialRef()
  #targetSR = osr.SpatialReference()
  #targetSR.ImportFromWkt(raster.GetProjectionRef())
  #coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
  #feat = lyr.GetNextFeature()
  #geom = feat.GetGeometryRef()
  #geom.Transform(coordTrans)
  
  # Get extent of feat
  geom = feat.GetGeometryRef()
  if (geom.GetGeometryName() == 'MULTIPOLYGON'):
    count = 0
    pointsX = []; pointsY = []
    for polygon in geom:
      geomInner = geom.GetGeometryRef(count)
      ring = geomInner.GetGeometryRef(0)
      numpoints = ring.GetPointCount()
      for p in range(numpoints):
        lon, lat, z = ring.GetPoint(p)
        pointsX.append(lon)
        pointsY.append(lat)
      count += 1
  elif (geom.GetGeometryName() == 'POLYGON'):
    ring = geom.GetGeometryRef(0)
    numpoints = ring.GetPointCount()
    pointsX = []; pointsY = []
    for p in range(numpoints):
      lon, lat, z = ring.GetPoint(p)
      pointsX.append(lon)
      pointsY.append(lat)

  else:
    sys.exit("ERROR: Geometry needs to be either Polygon or Multipolygon")

  xmin = min(pointsX)
  xmax = max(pointsX)
  ymin = min(pointsY)
  ymax = max(pointsY)

  # Specify offset and rows and columns to read
  xoff = int((xmin - xOrigin)/pixelWidth)
  yoff = int((yOrigin - ymax)/pixelWidth)
  xcount = int((xmax - xmin)/pixelWidth) #+1 !!!!!!!!!!!!!!!!!!!!! This adds a pixel to the right side
  ycount = int((ymax - ymin)/pixelWidth) #+1 !!!!!!!!!!!!!!!!!!!!! This adds a pixel to the bottom side
  
  #print(xoff, yoff, xcount, ycount)
              
  # Create memory target raster
  target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
  target_ds.SetGeoTransform((
    xmin, pixelWidth, 0,
    ymax, 0, pixelHeight,
  ))

  # Create for target raster the same projection as for the value raster
  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt(raster.GetProjectionRef())
  target_ds.SetProjection(raster_srs.ExportToWkt())

  # Rasterize zone polygon to raster
  gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

  # Read raster as arrays
  magBandRaster = raster.GetRasterBand(2)
  magBandData = magBandRaster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float)

  durBandRaster = raster.GetRasterBand(3)
  durBandData = durBandRaster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float)


  bandmask = target_ds.GetRasterBand(1)
  datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(np.float)

  # Mask zone of raster
  magZone = np.ma.masked_array(magBandData,  np.logical_not(datamask))
  durZone = np.ma.masked_array(durBandData,  np.logical_not(datamask))


  # Calculate statistics of zonal raster
  #return numpy.average(zoneraster),numpy.mean(zoneraster),numpy.median(zoneraster),numpy.std(zoneraster),numpy.var(zoneraster)
  return np.mean(magZone),np.std(magZone),np.mean(durZone),np.std(durZone)



def update_progress(progress):
  sys.stdout.write( '\r   {0}% {1}'.format(int(math.floor(progress*100)), 'done'))
  sys.stdout.flush()



  
#################################################################################################################
#################################################################################################################



segDir = ltcdb.get_dir("Select a folder that contains LT segmentation files\n\n(*\\raster\\landtrendr\\segmentation\\*)")
if segDir == '':
  sys.exit('ERROR: No folder containing LT segmentation files was selected.\nPlease re-run the script and select a folder.')

segDir = os.path.normpath(segDir)

vertYrsFile = glob(segDir+'/*vert_yrs.tif')
if len(vertYrsFile) == 0:
  sys.exit('ERROR: There was no *vert_yrs.tif file in the folder selected.\nPlease fix this.')   

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
vertFitIDXFile = vertYrsFile.replace('yrs.tif', 'fit.tif')
vertFitTCBFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcb.tif')
vertFitTCGFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcg.tif')
vertFitTCWFile = vertYrsFile.replace('vert_yrs.tif', 'vert_fit_tcw.tif')

#TODO need to error check for existence of TC vert files
if not os.path.exists(vertFitIDXFile):
  sys.exit('ERROR: There was no *vert_fit.tif file in the folder selected.\nPlease fix this.') 

#segDir = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930"
#vertYrsFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-vert_yrs.tif"
#vertFitFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-vert_fit.tif"
#info = get_info('PARK_CODE-MORA-NBR-7-19842017-06010930')

"""
# get the mmu
mmuGood = 0
while mmuGood is 0:
  print('\n')
  mmu = raw_input('What is the desired minimum patch size in pixels: ')
  try:
    mmu = int(mmu)
    mmuGood = 1
  except ValueError: 
    print('\n')
    print('ERROR: The selected value cannot be converted to an integer.')
    print('       Please try again and make sure to enter a number.')
"""

# get the min mag
minMagGood = 0
while minMagGood is 0:
  minMag = raw_input('What is the desired minimum disturbance magnitude: ')
  try:
    minMag = int(minMag)
    minMag = abs(minMag) * -1
    minMagGood = 1
  except ValueError: 
    print('\n')
    print('ERROR: The selected value cannot be converted to an integer.')
    print('       Please try again and make sure to enter a number.')






###################################################################################
# get run info
info = ltcdb.get_info(bname)
indexID = info['indexID']
startYear = info['startYear']
endYear = info['endYear']
startYearChng = startYear+1



###################################################################################

# create ouput file - needs to be a copy of an ftv minus 1 band
# find an ftv file
ftvFiles = glob(os.path.dirname(vertFitIDXFile)+'/*ftv_idx.tif')
# TODO - deal with not finding an ftv file
ftvFile = ftvFiles[0]

# make new file names
distInfoOutYrs = os.path.join(outDir, bname+'-change_yrs.tif')
distInfoOutDur = os.path.join(outDir, bname+'-change_dur.tif')
distInfoOutMagIDX = os.path.join(outDir, bname+'-change_idx_mag.tif')
distInfoOutPreIDX = os.path.join(outDir, bname+'-change_idx_pre.tif')
distInfoOutMagTCB = os.path.join(outDir, bname+'-change_tcb_mag.tif')
distInfoOutPreTCB = os.path.join(outDir, bname+'-change_tcb_pre.tif')
distInfoOutMagTCG = os.path.join(outDir, bname+'-change_tcg_mag.tif')
distInfoOutPreTCG = os.path.join(outDir, bname+'-change_tcg_pre.tif')
distInfoOutMagTCW = os.path.join(outDir, bname+'-change_tcw_mag.tif')
distInfoOutPreTCW = os.path.join(outDir, bname+'-change_tcw_pre.tif')

# make a summary stats file
summaryInfoFile = os.path.join(outDir, bname+'-change_attributes.csv') 
summaryInfo = [
    [distInfoOutDur   , 'yod'       , 'min' , 'ogr.OFTInteger'],
    [distInfoOutDur   , 'durStdv'   , 'stdv', 'ogr.OFTInteger'],
    [distInfoOutDur   , 'durMean'   , 'mean', 'ogr.OFTInteger'],
    [distInfoOutDur   , 'durStdv'   , 'stdv', 'ogr.OFTInteger'],
    [distInfoOutMagIDX, 'idxMagMean', 'mean', 'ogr.OFTInteger'],
    [distInfoOutMagIDX, 'idxMagStdv', 'stdv', 'ogr.OFTInteger'],
    [distInfoOutMagTCB, 'tcbMagMean', 'mean', 'ogr.OFTInteger'],
    [distInfoOutMagTCB, 'tcbMagStdv', 'stdv', 'ogr.OFTInteger'],  
    [distInfoOutMagTCG, 'tcgMagMean', 'mean', 'ogr.OFTInteger'],
    [distInfoOutMagTCG, 'tcgMagStdv', 'stdv', 'ogr.OFTInteger'],
    [distInfoOutMagTCW, 'tcwMagMean', 'mean', 'ogr.OFTInteger'],
    [distInfoOutMagTCW, 'tcwMagStdv', 'stdv', 'ogr.OFTInteger'],
    [distInfoOutPreIDX, 'idxPreMean', 'mean', 'ogr.OFTInteger'],
    [distInfoOutPreIDX, 'idxPreStdv', 'stdv', 'ogr.OFTInteger'],
    [distInfoOutPreTCB, 'tcbPreMean', 'mean', 'ogr.OFTInteger'],
    [distInfoOutPreTCB, 'tcbPreStdv', 'stdv', 'ogr.OFTInteger'],  
    [distInfoOutPreTCG, 'tcgPreMean', 'mean', 'ogr.OFTInteger'],
    [distInfoOutPreTCG, 'tcgPreStdv', 'stdv', 'ogr.OFTInteger'],
    [distInfoOutPreTCW, 'tcwPreMean', 'mean', 'ogr.OFTInteger'],
    [distInfoOutPreTCW, 'tcwPreStdv', 'stdv', 'ogr.OFTInteger']
]

with open(summaryInfoFile, 'w') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(summaryInfo)



# create the blanks
outPuts = [distInfoOutYrs, distInfoOutDur, 
           distInfoOutMagIDX, distInfoOutPreIDX,
           distInfoOutMagTCB, distInfoOutPreTCB,
           distInfoOutMagTCG, distInfoOutPreTCG,
           distInfoOutMagTCW, distInfoOutPreTCW]

nBands = ltcdb.make_output_blanks(ftvFile, outPuts, -1)


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
  'B3'  :  1
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
dstPreIDX = gdal.Open(distInfoOutPreIDX, gdal.GA_Update)
dstMagTCB = gdal.Open(distInfoOutMagTCB, gdal.GA_Update)
dstPreTCB = gdal.Open(distInfoOutPreTCB, gdal.GA_Update)
dstMagTCG = gdal.Open(distInfoOutMagTCG, gdal.GA_Update)
dstPreTCG = gdal.Open(distInfoOutPreTCG, gdal.GA_Update)
dstMagTCW = gdal.Open(distInfoOutMagTCW, gdal.GA_Update)
dstPreTCW = gdal.Open(distInfoOutPreTCW, gdal.GA_Update)




##############################################################################

# set some size variables
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
    npOutPreIDX = dstPreIDX.ReadAsArray(x, y, cols, rows)
    
    # load the annual TC output chunk as an np array
    npOutMagTCB = dstMagTCB.ReadAsArray(x, y, cols, rows)
    npOutPreTCB = dstPreTCB.ReadAsArray(x, y, cols, rows)
    npOutMagTCG = dstMagTCG.ReadAsArray(x, y, cols, rows)
    npOutPreTCG = dstPreTCG.ReadAsArray(x, y, cols, rows)
    npOutMagTCW = dstMagTCW.ReadAsArray(x, y, cols, rows)
    npOutPreTCW = dstPreTCW.ReadAsArray(x, y, cols, rows)

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
        if (vertYrs == 0).all():
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
        preIDX = vertValsIDX[distIndex]
        if flipper == -1:
          preIDX = preIDX * flipper
        
        preTCB = vertValsTCB[distIndex]
        preTCG = vertValsTCG[distIndex]
        preTCW = vertValsTCW[distIndex]

        
        
        # replace the pixel values of the ouput series 
        theseBands = [thisYear-startYearChng for thisYear in yod]
        npOutYrs[theseBands, subY, subX] = yod
        npOutDur[theseBands, subY, subX] = dur
        npOutMagIDX[theseBands, subY, subX] = magIDX
        npOutMagTCB[theseBands, subY, subX] = magTCB
        npOutMagTCG[theseBands, subY, subX] = magTCG
        npOutMagTCW[theseBands, subY, subX] = magTCW        
        npOutPreIDX[theseBands, subY, subX] = preIDX
        npOutPreTCB[theseBands, subY, subX] = preTCB
        npOutPreTCG[theseBands, subY, subX] = preTCG
        npOutPreTCW[theseBands, subY, subX] = preTCW



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
      ltcdb.write_array(dstPreIDX, b, npOutPreIDX, x, y)
      ltcdb.write_array(dstPreTCB, b, npOutPreTCB, x, y)
      ltcdb.write_array(dstPreTCG, b, npOutPreTCG, x, y)
      ltcdb.write_array(dstPreTCW, b, npOutPreTCW, x, y)
      
  
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
