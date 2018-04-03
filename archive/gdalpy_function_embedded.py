# -*- coding: utf-8 -*-
"""
Created on Mon Apr 02 14:45:51 2018

@author: braatenj
"""

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