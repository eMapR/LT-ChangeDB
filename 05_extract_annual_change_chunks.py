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



def get_info(name):
  pieces = name.split('-')[0:6]
  return {'key': pieces[0],
          'value': pieces[1],
          'indexID': pieces[2],
          'nVert': int(pieces[3]),
          'startYear':int(pieces[4][0:4]),
          'endYear':int(pieces[4][4:8])}

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


def get_dir(message):
  root = Tkinter.Tk()
  root.withdraw()
  root.overrideredirect(1)
  root.attributes('-alpha', 0.0)
  root.deiconify()
  root.lift()
  root.focus_force()
  thisDir = str(tkFileDialog.askdirectory(initialdir = "/",title = message))
  root.destroy()
  return thisDir



def make_output_blanks(inputFtv, outPuts):
  #inputFtv = vertYrsFile
  src_ds = gdal.Open(inputFtv)
  tx = src_ds.GetGeoTransform()
  prj = src_ds.GetProjection()
  driver = src_ds.GetDriver()
  band = src_ds.GetRasterBand(1)
  xsize = band.XSize
  ysize = band.YSize
  nBands = src_ds.RasterCount
  src_ds = None
  
  nBands -= 1
  for i, thisOut in enumerate(outPuts):
    if i == 0:
      # make a new file
      copyThis = thisOut
      dst_ds = driver.Create(thisOut, xsize, ysize, nBands, band.DataType)
      dst_ds.SetGeoTransform(tx)
      dst_ds.SetProjection(prj)
      dst_ds = None
    else:
      copyfile(copyThis, thisOut)
  print(nBands)
  return nBands



def fill_blank(value, band, nBlank):
  blank = np.zeros(nBlank, np.int16)
  blank[band] = value
  return blank



def write_array(dsOut, band, data, x, y):
  dataBand = dsOut.GetRasterBand(band+1)
  data = data[band, :, :]
  dataBand.WriteArray(data, x, y)
  
  
#################################################################################################################
#################################################################################################################



segDir = get_dir("Select a folder that contains LT segmentation files\n\n(*\\raster\\landtrendr\\segmentation\\*)")
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
vertFitFile = vertYrsFile.replace('yrs.tif', 'fit.tif')
if not os.path.exists(vertFitFile):
  sys.exit('ERROR: There was no *vert_fit.tif file in the folder selected.\nPlease fix this.') 

#segDir = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930"
#vertYrsFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-vert_yrs.tif"
#vertFitFile = r"D:\work\proj\al\gee_test\test\raster\landtrendr\segmentation\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-vert_fit.tif"
#info = get_info('PARK_CODE-MORA-NBR-7-19842017-06010930')


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

# create ouput file - needs to be a copy of an ftv minus 1 band
# find an ftv file
ftvFiles = glob(os.path.dirname(vertFitFile)+'/*ftv_idx.tif')
# TODO - deal with not finding an ftv file
ftvFile = ftvFiles[0]

# make new file names
distInfoOutYrs = os.path.join(outDir, bname+'-change_yrs.tif')
distInfoOutMag = os.path.join(outDir, bname+'-change_mag.tif')
distInfoOutDur = os.path.join(outDir, bname+'-change_dur.tif')
distInfoOutPre = os.path.join(outDir, bname+'-change_pre.tif')
outPuts = [distInfoOutYrs, distInfoOutMag, distInfoOutDur, distInfoOutPre]

# create the blanks
nBands = make_output_blanks(ftvFile, outPuts)


###################################################################################

# get run info
info = get_info(bname)
indexID = info['indexID']
startYear = info['startYear']
endYear = info['endYear']

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
srcFit = gdal.Open(vertFitFile)
srcYrs = gdal.Open(vertYrsFile)

# open the output files
dstYrs = gdal.Open(distInfoOutYrs, gdal.GA_Update)
dstMag = gdal.Open(distInfoOutMag, gdal.GA_Update)
dstDur = gdal.Open(distInfoOutDur, gdal.GA_Update)
dstPre = gdal.Open(distInfoOutPre, gdal.GA_Update)

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
    
    npYrs = srcYrs.ReadAsArray(x, y, cols, rows)
    npFit = srcFit.ReadAsArray(x, y, cols, rows)
    
    npOutYrs = dstYrs.ReadAsArray(x, y, cols, rows)
    npOutMag = dstMag.ReadAsArray(x, y, cols, rows)
    npOutDur = dstDur.ReadAsArray(x, y, cols, rows)
    npOutPre = dstPre.ReadAsArray(x, y, cols, rows)
    
    if flipper == -1:
      npFit = npFit * flipper
    nVerts, subYsize, subXsize = npYrs.shape
 
    for subY in xrange(subYsize):
      #subY = 0
      #progress = (y+1.0)/ySize
      #update_progress(progress)    
      for subX in xrange(subXsize):
        #subX = 0
        # read in the vert years for this pixel
        vertYrsPix = npYrs[:, subY, subX]

        # check to see if this is a NoData pixel    
        if (vertYrsPix == 0).all():
          continue

        # get indices of the verts
        vertIndex = np.where(vertYrsPix != 0)[0]
        
        # extract the vert years
        vertYrsPix = vertYrsPix[vertIndex]

        # extract this pixels vert fit - going to see if there are disturbances
        vertFitPix = npFit[vertIndex, subY, subX]

        # get the fit value delta for each segment
        segStartFit = vertFitPix[:-1]
        segEndFit = vertFitPix[1:]
        segMag = segEndFit - segStartFit

        # figure out which segs are disturbance
        distIndex = np.where(segMag < minMag)[0] # why have to index 0?
        
        # check to see if there are any disturbances
        if len(distIndex) == 0:
          continue

        #  calc the year of segment identification
        segStartYear = vertYrsPix[:-1]+1
        #  extract the year of segment identification for the identified disturbances
        yod = segStartYear[distIndex]
        
        # extract the mag for this disturbance
        mag = segMag[distIndex]
        
        # extract the dur for this disturbance
        segStartYr = vertYrsPix[:-1]
        segEndYr = vertYrsPix[1:]
        segDur = segEndYr - segStartYr
        dur = segDur[distIndex]

        # extract the predist value this disturbance
        pre = vertFitPix[distIndex]
        if flipper == -1:
          pre = pre * flipper
        
        for i, thisYear in enumerate(yod):
          thisBand = thisYear-(startYear+1)
          npOutYrs[:, subY, subX] = fill_blank(yod[i], thisBand, nBands)   
          npOutMag[:, subY, subX] = fill_blank(mag[i], thisBand, nBands)
          npOutDur[:, subY, subX] = fill_blank(dur[i], thisBand, nBands)
          npOutPre[:, subY, subX] = fill_blank(pre[i], thisBand, nBands)

    for b in range(nBands):
      print(b)
      dataBand = dstYrs.GetRasterBand(b+1)
      data = npOutYrs[b, :, :]
      dataBand.WriteArray(data, x, y)
      
      
      
      #write_array(dstYrs, b, npOutYrs, x, y)
      #write_array(dstMag, b, npOutMag, x, y)
      #write_array(dstDur, b, npOutDur, x, y)
      #write_array(dstPre, b, npOutPre, x, y)
    
    
# close the output files
srcYrs = None
srcFit = None
dstYrs = None
dstMag = None
dstDur = None
dstPre = None    

