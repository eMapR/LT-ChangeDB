# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 12:04:05 2018

@author: braatenj
"""

from osgeo import gdal, ogr, osr
from shutil import copyfile
import Tkinter, tkFileDialog
import subprocess
import os
import numpy as np
import sys
import math
import pandas as pd


def make_output_blanks(inputFtv, outPuts, adj):
  #inputFtv = vertYrsFile
  src_ds = gdal.Open(inputFtv)
  tx = src_ds.GetGeoTransform()
  prj = src_ds.GetProjection()
  driver = gdal.GetDriverByName('GTiff')
  band = src_ds.GetRasterBand(1)
  xsize = band.XSize
  ysize = band.YSize
  nBands = src_ds.RasterCount
  src_ds = None
  
  nBands += adj
  for i, thisOut in enumerate(outPuts):
    if i == 0:
      # make a new file
      copyThis = thisOut
      dst_ds = driver.Create(thisOut, xsize, ysize, nBands, gdal.GDT_Int16)
      dst_ds.SetGeoTransform(tx)
      dst_ds.SetProjection(prj)
      #dst_ds = None
      
      array = np.add(dst_ds.GetRasterBand(1).ReadAsArray(),-9999)
      for b in range(1,nBands+1):
        band = dst_ds.GetRasterBand(b)
        band.WriteArray(array)
        band.SetNoDataValue(-9999)
        band.FlushCache()
      dst_ds = None
      
    else:
      copyfile(copyThis, thisOut)
  return nBands


def get_info(name):
  pieces = name.split('-')
  if len(pieces) >= 8:
    pieces = pieces[0:8]
    crs = pieces[7]
    crs = crs[0:4]+':'+crs[4:]
    del pieces[7]
    info = {'key': pieces[0],
            'value': pieces[1],
            'indexID': pieces[2],
            'nVert': int(pieces[3]),
            'startYear':int(pieces[4][0:4]),
            'endYear':int(pieces[4][4:8]),
            'startDay':pieces[5][0:4],
            'endDay':pieces[5][4:8],
            'crs':crs,
            'version':pieces[6],
            'name': '-'.join(pieces)}
  else:
    pieces = pieces[0:7]
    info = {'key': pieces[0],
            'value': pieces[1],
            'indexID': pieces[2],
            'nVert': int(pieces[3]),
            'startYear':int(pieces[4][0:4]),
            'endYear':int(pieces[4][4:8]),
            'startDay':pieces[5][0:4],
            'endDay':pieces[5][4:8],
            'version':pieces[6],
            'name': '-'.join(pieces)}
  return info

 
def write_array(dsOut, band, data, x, y):
  dataBand = dsOut.GetRasterBand(band+1)
  data = data[band, :, :]
  dataBand.WriteArray(data, x, y)
  
  
  
def get_dir(message, initialdir = "/"):
  root = Tkinter.Tk()
  root.withdraw()
  root.overrideredirect(1)
  root.attributes('-alpha', 0.0)
  root.deiconify()
  root.lift()
  root.focus_force()
  thisDir = os.path.normpath(str(tkFileDialog.askdirectory(initialdir = initialdir, title = message)))
  root.destroy()
  return thisDir


def get_file(message, initialdir = "/", filetypes = [("all files","*.*")]):
  root = Tkinter.Tk()
  root.withdraw()
  root.overrideredirect(1)
  root.attributes('-alpha', 0.0)
  root.deiconify()
  root.lift()
  root.focus_force()
  thisFile = os.path.normpath(str(tkFileDialog.askopenfilename(initialdir = initialdir, title = message, filetypes = filetypes)))
  root.destroy()
  return thisFile


def save_file(message, initialdir = "/"):
  root = Tkinter.Tk()
  root.withdraw()
  root.overrideredirect(1)
  root.attributes('-alpha', 0.0)
  root.deiconify()
  root.lift()
  root.focus_force()
  thisFile = tkFileDialog.asksaveasfile(initialdir = initialdir, title = message, mode='w',defaultextension=".shp")
  root.destroy()
  fileName = os.path.normpath(str(thisFile.name))
  thisFile.close()
  os.remove(fileName)
  return fileName


def get_delta(vertVals):
  segStartVal = vertVals[:-1]
  segEndVal = vertVals[1:]
  segDelta = segEndVal - segStartVal
  return segDelta


def make_vrt(chunkFiles, vrtFile):
  listFile = vrtFile.replace('.vrt', '_filelist.txt')
  tileList = open(listFile, 'w')
  for fn in chunkFiles:
    tileList.write(fn+'\n')
  tileList.close()
  
  cmd = 'gdalbuildvrt -q -input_file_list '+listFile+' '+vrtFile
  subprocess.call(cmd, shell=True)
  

def add_field(layer, fieldName, dtype):
  field = ogr.FieldDefn(fieldName, dtype)
  layer.CreateField(field)
  return layer


def year_to_band(bname, adj):
  info = get_info(bname)
  startYear = info['startYear'] + adj
  endYear = info['endYear']
  nYears = (endYear - startYear)+1
  yearIndex = np.array([0]*(startYear)+range(1, nYears+1))
  return yearIndex


def update_progress(progress, space='     '):
  sys.stdout.write( '\r'+space+'{0}% {1}'.format(int(math.floor(progress*100)), 'done'))
  sys.stdout.flush()
  
  
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


def dir_path(headDir, path):
  dirs = {
    'ts':os.path.join(headDir, 'timesync'),
    'tsR':os.path.join(headDir, 'timesync', 'raster'),
    'tsP':os.path.join(headDir, 'timesync', 'prep'),
    'tsV':os.path.join(headDir, 'timesync', 'vector'),
    'vid':os.path.join(headDir, 'video'),
    'r':os.path.join(headDir, 'raster'),
    'v':os.path.join(headDir, 'vector'),
    's':os.path.join(headDir, 'scripts'),
    'rP':os.path.join(headDir, 'raster', 'prep'),
    'rPg':os.path.join(headDir, 'raster', 'prep', 'gee_chunks'),            
    'rL':os.path.join(headDir, 'raster', 'landtrendr'),
    'rLs':os.path.join(headDir, 'raster', 'landtrendr', 'segmentation'),
    'rLc':os.path.join(headDir, 'raster', 'landtrendr', 'change')
  }
  
  if path == 'all':
    out = [os.path.normpath(value) for key, value in dirs.iteritems()]
  else:    
    out = os.path.normpath(dirs[path])
  return out

def is_headDir(headDir):
  if headDir == '.':
    sys.exit()
  test = dir_path(headDir, 'rLs')
  if not os.path.isdir(test):
    sys.exit('ERROR: The selected folder does not appear to be an LT-ChangeDB project head folder.\nPlease re-run the script and select an LT-ChangeDB project head folder.')

def is_success(cmdFailed):
  if cmdFailed:
    sys.exit('\nERROR: A command sent to an external program has failed.\nThe program may have printed a message above, please address the issue and re-run this script.')


def save_metadata(inFile, outFile):
  df = pd.read_csv(inFile).iloc[:, 1:-1]
  df = pd.DataFrame.transpose(df)
  labels = [i+':' for i in df.index]
  df.index = labels
  df.to_csv(outFile, ' ', header=False)

def calc_delta(ftvFile, deltaFile):
  srcFtv = gdal.Open(ftvFile)
  srcDelta = gdal.Open(deltaFile, 1)
  nBands = srcFtv.RasterCount
  noDataMask = np.where(srcFtv.GetRasterBand(1).ReadAsArray() == -9999)
  
  for b in range(0,nBands):     
    if b == 0:
      former = srcFtv.GetRasterBand(1).ReadAsArray()
      latter = former 
      delta = np.subtract(latter, former)
    else:
      former = srcFtv.GetRasterBand(b).ReadAsArray()
      latter = srcFtv.GetRasterBand(b+1).ReadAsArray() 
      delta = np.subtract(latter, former)
      
    delta[noDataMask] = -9999  
    outBand = srcDelta.GetRasterBand(b+1)
    outBand.SetNoDataValue(-9999)
    outBand.WriteArray(delta)
  
  srcFtv = None
  srcDelta = None

  
  
def get_dur(vertYrs):
  segStartYr = vertYrs[:-1]
  segEndYr = vertYrs[1:]
  segDur = segEndYr - segStartYr
  return segDur  
  
def collapse_segs(vertYrs, npFitIDX, thresh):
  vertIndex = np.where(vertYrs != 0)[0]
  if len(vertIndex) > 2:
    check = True
    while check:
      vertYrsTemp = vertYrs[vertIndex]
      vertValsIDXTemp = npFitIDX[vertIndex]
      segMagIDXTemp = get_delta(vertValsIDXTemp).astype(float) 
      segDurTemp = get_dur(vertYrsTemp).astype(float) 
      slope = np.divide(segMagIDXTemp, segDurTemp)
      checkLen = len(segMagIDXTemp)-1
      for i in range(checkLen):
        if np.sign(slope[i]) == np.sign(slope[i+1]):  # -1, 0, 1
          dif = abs(slope[i] - slope[i+1])/((slope[i] + slope[i+1])/2.0)
          if dif < thresh:
            vertIndex = np.delete(vertIndex, i+1)
            break
      if i == checkLen-1:
        check = False
  return(vertIndex)