# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 10:53:53 2018

@author: braatenj
"""


import sys
from osgeo import gdal, ogr, osr
import numpy as np




def zonal_stats(feat, input_zone_polygon, input_value_raster, band): #, raster_band

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
  dataBandRaster = raster.GetRasterBand(band)
  data = dataBandRaster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float)
  bandmask = target_ds.GetRasterBand(1)
  datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(np.float)

  # data zone of raster
  dataZone = np.ma.masked_array(data,  np.logical_not(datamask))

  raster_srs = None
  raster = None
  shp = None
  lyr = None
  # Calculate statistics of zonal raster
  return int(round(np.mean(dataZone))),int(round(np.std(dataZone)))

def add_field(layer, fieldName, dtype):
  field = ogr.FieldDefn(fieldName, dtype)
  layer.CreateField(field)
  return layer

import ltcdb





inPolygon = r"D:\work\proj\park_service\nccn-glkn\LT-ChangeDB_test\mora\vector\change\PARK_CODE-MORA-NBRz-7-19842017-06010930-dist_info_11mmu_8con\PARK_CODE-MORA-NBRz-7-19842017-06010930-dist_info_11mmu_8con_1992.shp"
inRaster = r"D:\work\proj\park_service\nccn-glkn\LT-ChangeDB_test\mora\raster\landtrendr\segmentation\PARK_CODE-MORA-NBRz-7-19842017-06010930\PARK_CODE-MORA-NBRz-7-19842017-06010930-ftv_tcb.tif"
#attributeList = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-change_attributes.csv"

# reference: https://gis.stackexchange.com/questions/141966/python-gdal-ogr-open-or-driver-open
driver = ogr.GetDriverByName('ESRI Shapefile')

# open the shapefile as writeable 
dataSource = driver.Open(inPolygon, 1) # 0 means read-only. 1 means writeable.

# get the layer from the file - a gdal dataset can potentially have many layers
# we just want the first layer
# reference: http://www.gdal.org/ogr_apitut.html
layer = dataSource.GetLayer()

"""
# make a list of the field to add to the layer
postChangeAttr = ['tcb01yrMn','tcb01yrSd',
                  'tcb03yrMn','tcb03yrSd',
                  'tcb07yrMn','tcb07yrSd',
                  'tcb15yrMn','tcb15yrSd',
                  'tcg01yrMn','tcg01yrSd',
                  'tcg03yrMn','tcg03yrSd',
                  'tcg07yrMn','tcg07yrSd',
                  'tcg15yrMn','tcg15yrSd', 
                  'tcw01yrMn','tcw01yrSd',
                  'tcw03yrMn','tcw03yrSd',
                  'tcw07yrMn','tcw07yrSd',
                  'tcw15yrMn','tcw15yrSd',]
"""
# add the fields to the layer !!!! this needs to be done from a for loop looking to the summary list .csv file
for attr in postChangeAttr:
  #layer = add_field(layer, attrList[attr,1], eval(attrList[attr,3]))
  layer = add_field(layer, attr, ogr.OFTInteger)



# get year bands  
yearIndex = ltcdb.year_to_band(os.path.basename(inRaster), 0)

# get end year
endYear = ltcdb.get_info(os.path.basename(inRaster))['endYear']

# get the number of features in the layer
nFeatures = layer.GetFeatureCount()

# Add features to the ouput Layer
postDataType = ['tcb']
for pdt in postDataType:
  #pdt = postDataType[0]
  for i in range(nFeatures):
    # get the ith feature
    #i=0
    feature = layer.GetFeature(i) 
    yod = int(feature.GetField("yod"))-1
    durMean = int(feature.GetField("durMean"))
    distEndYear = yod+durMean
    yr01 = distEndYear+1 
    yr03 = distEndYear+3
    yr07 = distEndYear+7
    yr15 = distEndYear+15
    postYears = np.array([yr01, yr03, yr07, yr15])
    postFields = np.array(['01yr','03yr','07yr','15yr'])
  
    goodYears = np.where(postYears <= endYear)
    postYears = postYears[goodYears]
    postFields = postFields[goodYears]
    
    for yr, field in zip(postYears, postFields):
      #print(yearIndex[yr])
      summary = zonal_stats(feature, inPolygon, inRaster, yearIndex[yr]) 
    
      feature.SetField(pdt+field+'Mn', summary[0])
      feature.SetField(pdt+field+'Sd', summary[1])
  
      # set the changes to ith feature in the layer
    layer.SetFeature(feature)
  
  feature = None
  
# Close the Shapefile
layer = None
dataSource = None












