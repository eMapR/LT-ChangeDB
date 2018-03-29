# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 15:39:37 2018

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


def add_field(layer, fieldName, dtype):
  field = ogr.FieldDefn(fieldName, dtype)
  return layer.CreateField(field)



inPolygon = r"D:\work\proj\al\gee_test\test\vector\PARK_CODE-MORA-NBR-7-19842017-06010930-dist_info_11mmu.shp"
attributeList = r"D:\work\proj\al\gee_test\test\raster\landtrendr\change\PARK_CODE-MORA-NBR-7-19842017-06010930\PARK_CODE-MORA-NBR-7-19842017-06010930-change_attributes.csv"

print('\nAdding disturbance attributes to the shapefile table...\n')




# get the shapefile driver - if you don't specify driver, then in the 
# next line you can use ogr.Open() and it will try all drivers until it
# finds the one that opens the file, by specifying it will only try the
# defined driver
# reference: https://gis.stackexchange.com/questions/141966/python-gdal-ogr-open-or-driver-open
driver = ogr.GetDriverByName('ESRI Shapefile')

# open the shapefile as writeable 
dataSource = driver.Open(inPolygon, 1) # 0 means read-only. 1 means writeable.

# get the layer from the file - a gdal dataset can potentially have many layers
# we just want the first layer
# reference: http://www.gdal.org/ogr_apitut.html
layer = dataSource.GetLayer()


# read in the table of attributes to add and append new fields
attrList = np.genfromtxt(attributeList, delimiter=',', dtype='object')

for attr in range(attrList.shape[0]):
  layer = add_field(layer, attrList[attr,1], eval(attrList[attr,3]))

layer = add_field(layer, 'area', ogr.OFTInteger)
layer = add_field(layer, 'perim', ogr.OFTInteger)
layer = add_field(layer, 'shape', ogr.OFTReal)


# TODO if this is a file resulting from spatial change all the fields except yod need to be deleted



# make new fields
# reference: http://www.gdal.org/classOGRFieldDefn.html
# for list of type see http://www.gdal.org/ogr__core_8h.html#a787194bea637faf12d61643124a7c9fc

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










