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


# load vert years file
dsYrs = gdal.Open(vertYrsFile)
vertYrs = dsYrs.ReadAsArray()
tx = dsYrs.GetGeoTransform()
prj = dsYrs.GetProjection()
driver = dsYrs.GetDriver()
ds_years = None


# get run info
info = get_info(bname)
indexID = info['indexID']
startYear = info['startYear']
endYear = info['endYear']


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


# load the vert fit file
dsFit = gdal.Open(vertFitFile)
vertFit = dsFit.ReadAsArray()
# flip the values around 0, if disturbance is a spectral increase
if flipper == -1:
  vertFit = vertFit * flipper


# get the size of the vert yearsraster    
nVerts, ySize, xSize = vertYrs.shape


# loop through all the years
first = 1
for year in range(startYear+1,endYear+1): # [1993]:
  #year = 1993
  print('Working on year: '+str(year))
  # start a zero'd matrix to hold disturbance information  
  distInfo = np.full((3, ySize, xSize), 0, np.int16)
  for y in xrange(ySize):
    progress = (y+1.0)/ySize
    update_progress(progress)    
    for x in xrange(xSize):
      """
      # mock a pixel to play with
      year = 1985
      y = 844 #500
      x = 767 #500
      
      (-1959124.3 - -1981905)/30
      (2953875 - 2952874.4)/30      
      year = 1993
      x = 759
      y = 33
      """
      
      # read in the vert years for this pixel
      vertYrsPix = vertYrs[:, y, x]
      
      # check to see if this is a NoData pixel    
      if (vertYrsPix == 0).all():
        continue
      
      # get indices of the verts
      vertIndex = np.where(vertYrsPix != 0)[0]
      
      # extract the vert years
      vertYrsPix = vertYrs[vertIndex, y, x]
      
      # extract this pixels vert fit - going to see if there are disturbances
      vertFitPix = vertFit[vertIndex, y, x]
      
      # get the fit value delta for each segment
      segStartFit = vertFitPix[:-1]
      segEndFit = vertFitPix[1:]
      segMag = segEndFit - segStartFit
      
      # figure out which segs are disturbance
      distIndex = np.where(segMag < minMag)[0] # why have to index 0?
      
      # check to see if there are any disturbances
      if len(distIndex) == 0:
        continue
      
      # figure out if any of the disturbances happened this year
      #  calc the year of segment identification
      segStartYear = vertYrsPix[:-1]+1
      #  extract the year of segment identification for the identified disturbances
      segStartYearDist = segStartYear[distIndex]
      
      # check to see if the segment identification years match the year being worked on
      segStartIndex = np.where(segStartYearDist == year)[0]
      if len(segStartIndex) is 0:
        continue
      
      # extract the mag for this disturbance
      mag = segMag[distIndex][segStartIndex][0]
      
      # extract the dur for this disturbance
      segStartYr = vertYrsPix[:-1]
      segEndYr = vertYrsPix[1:]
      segDur = segEndYr - segStartYr
      dur = segDur[distIndex][segStartIndex][0]
      
      # fill in the info
      distInfo[0, y, x] = year
      distInfo[1, y, x] = mag
      distInfo[2, y, x] = dur
      mask = distInfo[0, :, :] != 0

  origin = tx[0], tx[3]
  distInfoOutPath = os.path.join(outDir, bname+'-'+str(year)+'-dist_info.tif')
  distMaskOutPath = os.path.join(outDir, bname+'-'+str(year)+'-dist_mask-'+str(mmu)+'mmu.tif')
  distPolyOutPath = os.path.join(outDir, bname+'-'+str(year)+'-dist_info-'+str(mmu)+'mmu.shp') #os.path.join(outDir, 'dist_info_'+str(year)+'.shp')
  mergedPolyOutPath = os.path.join(outDir, bname+'-annual-dist_info-'+str(mmu)+'mmu.shp') #os.path.join(outDir, 'ltee_mora_'+str(mmu)+'mmu_annual_dist.shp') # this should be set
  
  if not os.path.isdir(outDir):
    os.mkdir(outDir)
  
  print('\n')
  write_raster(distInfo, distInfoOutPath, prj, origin, 'GTiff')  
  write_raster(mask, distMaskOutPath, prj, origin, 'GTiff')  
  
  
  
  ###################################################################
  # MMU the raster
  ###################################################################
  print('\nSieving to minimum mapping unit...\n')
  gdal_sieve(distMaskOutPath, mmu)
  #sieveCmd = 'gdal_sieve.py -of GTiff -st '+str(mmu)+' -8 '+distMaskOutPath  
  #subprocess.call(sieveCmd, shell=True)
  
  
  
  ###################################################################
  # polygonize the raster
  ###################################################################
  print('Making polygons from disturbance pixel patches...\n')
  gdal_polygonize(distMaskOutPath, distMaskOutPath, distPolyOutPath)
  #polyCmd = 'gdal_polygonize.py -8 -f "ESRI shapefile" -mask ' + distMaskOutPath +' '+ distMaskOutPath +'  '+ distPolyOutPath
  #subprocess.call(polyCmd, shell=True)
  
  
  
  ###################################################################
  # remove the DN column  
  ###################################################################
  print('\nAdding disturbance attributes to the shapefile table...\n')
  
  polyBname = os.path.splitext(os.path.basename(distPolyOutPath))[0]
  alterCmd = 'ogrinfo ' + distPolyOutPath + ' ' + '-sql "ALTER TABLE ' + polyBname + ' DROP COLUMN DN"'
  subprocess.call(alterCmd, shell=True)
  
  
  #  convert = 'ogr2ogr -f SQLite -nlt MULTIPOLYGON -dsco "SPATIALITE=YES" ' + distPolyOutPathsql +' '+ distPolyOutPathshp
  #  subprocess.call(convert, shell=True)
  
  
  # get the shapefile driver - if you don't specify driver, then in the 
  # next line you can use ogr.Open() and it will try all drivers until it
  # finds the one that opens the file, by specifying it will only try the
  # defined driver
  # reference: https://gis.stackexchange.com/questions/141966/python-gdal-ogr-open-or-driver-open
  driver = ogr.GetDriverByName('ESRI Shapefile')
  
  # open the shapefile as writeable 
  dataSource = driver.Open(distPolyOutPath, 1) # 0 means read-only. 1 means writeable.
  
  # get the layer from the file - a gdal dataset can potentially have many layers
  # we just want the first layer
  # reference: http://www.gdal.org/ogr_apitut.html
  layer = dataSource.GetLayer()
  
  
  
  # make new fields
  # reference: http://www.gdal.org/classOGRFieldDefn.html
  # for list of type see http://www.gdal.org/ogr__core_8h.html#a787194bea637faf12d61643124a7c9fc
  index = ogr.FieldDefn('index', ogr.OFTString)
  yodField = ogr.FieldDefn('yod', ogr.OFTInteger)
  patchID = ogr.FieldDefn('patchID', ogr.OFTInteger)
  uniqID = ogr.FieldDefn('uniqID', ogr.OFTString)
  magMeanField = ogr.FieldDefn('magMean', ogr.OFTInteger)
  magStdvField = ogr.FieldDefn('magStdv', ogr.OFTInteger)
  durMeanField = ogr.FieldDefn('durMean', ogr.OFTInteger)
  durStdvField = ogr.FieldDefn('durStdv', ogr.OFTInteger)
  areaField = ogr.FieldDefn('area', ogr.OFTInteger)
  perimField = ogr.FieldDefn('perim', ogr.OFTInteger)
  shapeField = ogr.FieldDefn('shape', ogr.OFTReal)
  
  
  # add the new field to the layer
  layer.CreateField(index)
  layer.CreateField(yodField)
  layer.CreateField(patchID)
  layer.CreateField(uniqID)
  layer.CreateField(magMeanField)
  layer.CreateField(magStdvField)
  layer.CreateField(durMeanField)
  layer.CreateField(durStdvField)
  layer.CreateField(areaField)
  layer.CreateField(perimField)
  layer.CreateField(shapeField)
  
  # check to see if it was added
  # get the layer's attribute schema
  # reference: http://www.gdal.org/classOGRLayer.html#a80473bcfd11341e70dd35bebe94026cf
  #layerDefn = layer.GetLayerDefn()
  #fieldNames = [layerDefn.GetFieldDefn(i).GetName() for i in range(layerDefn.GetFieldCount())]
  
  # get the number of features in the layer
  nFeatures = layer.GetFeatureCount()
  
  # Add features to the ouput Layer
  for i in range(nFeatures):
    # get the ith feature
    feature = layer.GetFeature(i) 
    
    # set the ith feature's fields
    patchID = i+1
    feature.SetField('index', indexID)
    feature.SetField('yod', year)
    feature.SetField('patchID', patchID)
    feature.SetField('uniqID', indexID+str(year)+str(patchID))
    
    # get zonal stats on disturbance
    summary = zonal_stats(feature, distPolyOutPath, distInfoOutPath) #, 2
    #durSummary = zonal_stats(feature, distPolyOutPath, distInfoOutPath, 3)
  
    geometry = feature.GetGeometryRef()
    area = geometry.GetArea()
    areaCircle = math.sqrt(area/math.pi)*2*math.pi
    perimeter = geometry.Boundary().Length()
    pa = round(perimeter/areaCircle, 6)
  
    # set the ith features summary stats fields
    feature.SetField('magMean', int(round(summary[0])))
    feature.SetField('magStdv', int(round(summary[1])))
    feature.SetField('durMean', int(round(summary[2])))
    feature.SetField('durStdv', int(round(summary[3])))
    feature.SetField('area', int(area))
    feature.SetField('perim', int(perimeter))
    feature.SetField('shape', pa)
    
    # set the changes to ith feature in the layer
    layer.SetFeature(feature)
    
    #feature = None
    
  # Close the Shapefile
  dataSource = None
  
  
  # merge the polygons
  if first:
    mergeCmd = 'ogr2ogr -f "ESRI Shapefile" ' + mergedPolyOutPath + ' ' + distPolyOutPath
  else:
    mergeCmd = 'ogr2ogr -f "ESRI Shapefile" -append -update ' + mergedPolyOutPath + ' ' + distPolyOutPath  
  
  subprocess.call(mergeCmd, shell=True)
  
  first = 0
  
print('Done!')


